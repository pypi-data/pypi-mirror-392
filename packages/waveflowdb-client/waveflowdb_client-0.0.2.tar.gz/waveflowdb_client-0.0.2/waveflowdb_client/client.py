import time
import logging
import json
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any

from .config import Config
from .utils import FileProcessor, Logger, BatchManager
from .exceptions import APIError
from .models import ChatResponse, MatchingDocsResponse, HealthResponse, BatchResult

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class VectorLakeClient:
    def __init__(self, config: Optional[Config] = None, **kwargs):
        if config is None:
            config = Config(**kwargs)
        logging.info(f"Initializing VectorLakeClient with base_url={config.base_url_query}")
        self.config = config
        self.logger = Logger(config.log_dir)
        self.batch_manager = BatchManager(config.max_files_per_batch, config.max_batch_size_mb)
        self.file_processor = FileProcessor()
        self.perf_csv = "performance_logs.csv" 

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'x-api-key': self.config.api_key
        }

    def _make_request(self, endpoint: str, payload: Dict[str, Any], operation: str = "", batch_num: int = 0) -> Dict[str, Any]:
        headers = self._get_headers()
        request_size = len(json.dumps(payload).encode('utf-8')) / 1024 if payload is not None else 0
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                response = requests.post(endpoint, json=payload, headers=headers, timeout=self.config.timeout)
                latency = (time.time() - start_time) * 1000
                try:
                    result = response.json()
                except Exception:
                    result = {"status_code": response.status_code, "text": response.text}

                if operation:
                    response_size = len(response.content) / 1024 if response.content is not None else 0
                    result_count = len(result.get("results", [])) if isinstance(result, dict) else "N/A"
                    self.logger.log_performance(operation, batch_num, latency, request_size, response_size, result_count)

                if response.status_code >= 400:
                    raise APIError(result.get('message', f'HTTP {response.status_code}'), status_code=response.status_code, response_text=response.text)

                return result
            except requests.exceptions.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    error_msg = f"Request failed after {self.config.max_retries} attempts: {str(e)}"
                    if operation:
                        self.logger.log_api_error(operation, batch_num, error_msg)
                    raise APIError(error_msg, getattr(e.response, 'status_code', None), getattr(e.response, 'text', None))
                time.sleep(2 ** attempt)

    def _read_files(self, filenames: List[str]) -> List[str]:
        contents = []
        for filename in filenames:
            filepath = os.path.join(self.config.vector_lake_path, filename)
            try:
                if self.file_processor.is_supported_file(filename):
                    content = self.file_processor.read_file_content(filepath)
                    contents.append(content)
                else:
                    self.logger.log_skipped_file(filename, "Unsupported file type")
                    contents.append("")
            except Exception as e:
                self.logger.log_skipped_file(filename, f"Read error: {str(e)}")
                contents.append("")
        return contents

    def chat_with_docs(self,
                       query: str,
                       user_id: str,
                       vector_lake_description: str,
                       pattern: str = "static",
                       session_id: Optional[str] = None,
                       hybrid_filter: bool = False,
                       top_docs: int = 3,
                       threshold: float = 0.2,
                       files: Optional[List[str]] = None) -> Dict[str, Any]:
        endpoint = self.config.endpoints["chat_with_docs"]
        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "vector_lake_description": vector_lake_description,
            "query": query,
            "hybrid_filter": hybrid_filter,
            "top_docs": top_docs,
            "threshold": threshold,
            "pattern": pattern
        }

        if pattern == "dynamic" and files:
            file_contents = self._read_files(files)
            payload.update({
                "files_name": files,
                "files_data": file_contents
            })

        try:
            result = self._make_request(endpoint, payload, "chat_with_docs")
            return result
        except Exception as e:
            return ChatResponse(response=f"Error: {e}", query=query, session_id=session_id or "", user_id=user_id, timestamp=time.time())

    def get_matching_docs(self,
                          query: str,
                          user_id: str,
                          vector_lake_description: str,
                          pattern: str = "static",
                          session_id: Optional[str] = None,
                          hybrid_filter: bool = False,
                          top_docs: int = 10,
                          threshold: float = 0.2,
                          files: Optional[List[str]] = None,
                          with_data: bool = False) -> Dict[str, Any]:
        endpoint_key = "top_matching_docs_with_data" if with_data else "top_matching_docs"
        endpoint = self.config.endpoints[endpoint_key]
        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "vector_lake_description": vector_lake_description,
            "query": query,
            "hybrid_filter": hybrid_filter,
            "top_docs": top_docs,
            "threshold": threshold,
            "pattern": pattern
        }

        if pattern == "dynamic" and files:
            file_contents = self._read_files(files)
            payload.update({
                "files_name": files,
                "files_data": file_contents
            })

        try:
            raw_result = self._make_request(endpoint, payload, endpoint_key)
            return raw_result
        except Exception as e:
            raise

    def add_documents(self,
                      user_id: str,
                      vector_lake_description: str,
                      start_from_batch=1,
                      intelligent_segmentation: bool = True,
                      session_id: Optional[str] = None,
                      files: Optional[List[str]] = None,
                      files_name: Optional[List[str]] = None,
                      files_data: Optional[List[str]] = None,
                      max_workers=5) -> List[BatchResult]:
        # If user supplies file names and data directly, bypass batching
        if files_name and files_data:
            if len(files_name) != len(files_data):
                raise ValueError("files_name and files_data must be same length")
            payload = {
                "session_id": session_id,
                "user_id": user_id,
                "vector_lake_description": vector_lake_description,
                "files_name": files_name,
                "files_data": files_data,
                "intelligent_segmentation": intelligent_segmentation
            }
            endpoint = self.config.endpoints["add_docs"]
            result = self._make_request(endpoint, payload, "add_docs", batch_num=1)
            return [BatchResult(batch_number=1, response=result, files_processed=files_name, success=True)]

        return self._process_files_in_batches(
            "add_docs", user_id, vector_lake_description, start_from_batch, intelligent_segmentation, session_id, files, max_workers=max_workers
        )

    def refresh_documents(self,
                          user_id: str,
                          vector_lake_description: str,
                          intelligent_segmentation: bool = True,
                          session_id: Optional[str] = None,
                          files: Optional[List[str]] = None,
                          files_name: Optional[List[str]] = None,
                          files_data: Optional[List[str]] = None) -> List[BatchResult]:
        # If user supplies file names and data directly, bypass batching
        if files_name and files_data:
            if len(files_name) != len(files_data):
                raise ValueError("files_name and files_data must be same length")
            payload = {
                "session_id": session_id,
                "user_id": user_id,
                "vector_lake_description": vector_lake_description,
                "files_name": files_name,
                "files_data": files_data,
                "intelligent_segmentation": intelligent_segmentation
            }
            endpoint = self.config.endpoints["refresh_docs"]
            result = self._make_request(endpoint, payload, "refresh_docs", batch_num=1)
            return [BatchResult(batch_number=1, response=result, files_processed=files_name, success=True)]

        return self._process_files_in_batches(
            "refresh_docs", user_id, vector_lake_description, 1, intelligent_segmentation, session_id, files
        )

    def health_check(self, user_id: str, vector_lake_description: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        endpoint = self.config.endpoints["health"]
        payload = {"session_id": session_id, "user_id": user_id, "vector_lake_description": vector_lake_description}
        try:
            result = self._make_request(endpoint, payload, "health")
            return HealthResponse(status="success", message=result.get("message", "ok"), timestamp=time.time(), details=result)
        except Exception as e:
            return HealthResponse(status="error", message=str(e), timestamp=time.time())

    def get_namespace_details(self, user_id: str, session_id: Optional[str] = None, vector_lake_description: Optional[str] = None) -> Dict[str, Any]:
        endpoint = self.config.endpoints["get_namespace_details_by_userid"]
        payload = {"session_id": session_id, "user_id": user_id}
        if vector_lake_description:
            payload["vector_lake_description"] = vector_lake_description
        try:
            result = self._make_request(endpoint, payload, "get_namespace_details")
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_docs_information(self, user_id: str, vector_lake_description: str, session_id: Optional[str] = None, keyword: Optional[str] = None, threshold: int = 70) -> Dict[str, Any]:
        endpoint = self.config.endpoints["get_docs_information"]
        payload = {"session_id": session_id, "user_id": user_id, "vector_lake_description": vector_lake_description, "threshold": threshold}
        if keyword:
            payload["keyword"] = keyword
        try:
            result = self._make_request(endpoint, payload, "get_docs_information")
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def full_corpus_search(self, user_id: str, vector_lake_description: str, keyword: str, session_id: Optional[str] = None, top_docs: int = 10) -> Dict[str, Any]:
        endpoint = self.config.endpoints["full_corpus_search"]
        payload = {"session_id": session_id, "user_id": user_id, "vector_lake_description": vector_lake_description, "keyword": keyword, "top_docs": top_docs}
        try:
            result = self._make_request(endpoint, payload, "full_corpus_search")
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _make_request_with_backoff(self, endpoint, payload, operation, batch_num, retries=5, base_delay=1):
        delay = base_delay
        for attempt in range(retries):
            try:
                result = self._make_request(endpoint, payload, operation, batch_num)
                return result
            except APIError as e:
                if getattr(e, "status_code", None) == 429:
                    logging.warning(f"Batch {batch_num} throttled, retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise
            except Exception:
                raise

    def _process_files_in_batches(self, operation: str, user_id: str, vector_lake_description: str, start_from_batch, intelligent_segmentation: bool = False, session_id: Optional[str] = None, files: Optional[List[str]] = None, max_workers: int = 1, batch_delay: float = 2):
        if files is None:
            files = [f for f in os.listdir(self.config.vector_lake_path) if os.path.isfile(os.path.join(self.config.vector_lake_path, f)) and self.file_processor.is_supported_file(f)]
        batches = self.batch_manager.create_batches(files, self.config.vector_lake_path)
        results = []
        start_batch_index = start_from_batch - 1
        if start_from_batch > 1:
            logging.info(f"Resuming from batch {start_from_batch}, skipping first {start_from_batch - 1} batches")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for i, batch in enumerate(batches):
                if i < start_batch_index:
                    logging.info(f"Skipping batch {i + 1}")
                    continue
                batch_num = i + 1
                file_contents = self._read_files(batch)
                payload = {"session_id": session_id, "user_id": user_id, "vector_lake_description": vector_lake_description, "files_name": batch, "files_data": file_contents, "intelligent_segmentation": intelligent_segmentation}
                endpoint = self.config.endpoints[operation]
                futures[executor.submit(self._make_request_with_backoff, endpoint, payload, operation, batch_num)] = (batch_num, batch, time.time())
                time.sleep(batch_delay)
            for future in as_completed(futures):
                batch_num, batch, start_time = futures[future]
                try:
                    result = future.result()
                    processing_time = time.time() - start_time
                    logging.info(f"Batch {batch_num} done")
                    results.append(BatchResult(batch_number=batch_num, response=result, files_processed=batch, success=True, processing_time=processing_time))
                except Exception as e:
                    processing_time = time.time() - start_time
                    logging.error(f"Batch {batch_num} failed: {str(e)}")
                    results.append(BatchResult(batch_number=batch_num, response=str(e), files_processed=batch, success=False, error_message=str(e), processing_time=processing_time))
        return results
