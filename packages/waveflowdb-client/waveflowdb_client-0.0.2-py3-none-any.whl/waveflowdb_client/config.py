import os
from typing import Optional, Dict

class Config:
    ALLOWED_EXTENSIONS = ["txt", "csv", "json", "py", "docx", "pdf"]

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: str = "https://waveflow-analytics.com",
        timeout: int = 60,
        max_retries: int = 2,
        max_files_per_batch: int = 100,
        max_batch_size_mb: int = 20,
        vector_lake_path: str = "upload",
        log_dir: str = "logs",
    ):
        self.api_key = api_key or os.getenv("VECTOR_LAKE_API_KEY")
        self.host = host.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_files_per_batch = max_files_per_batch
        self.max_batch_size_mb = max_batch_size_mb
        self.vector_lake_path = vector_lake_path
        self.log_dir = log_dir

        if not self.api_key:
            raise ValueError("API key is required. Provide api_key or set VECTOR_LAKE_API_KEY environment variable.")

        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.vector_lake_path, exist_ok=True)

    @property
    def base_url_query(self) -> str:
        return f"{self.host}/query"

    @property
    def base_url_upload(self) -> str:
        return f"{self.host}/upload"

    @property
    def endpoints(self) -> Dict[str, str]:
        return {
            # Query service
            "chat_with_docs": f"{self.base_url_query}/chat_with_docs",
            "top_matching_docs": f"{self.base_url_query}/top_matching_docs",
            "top_matching_docs_with_data": f"{self.base_url_query}/top_matching_docs_with_data",
            "full_corpus_search": f"{self.base_url_query}/full_corpus_search",

            # Upload service
            "add_docs": f"{self.base_url_upload}/add_docs",
            "refresh_docs": f"{self.base_url_upload}/refresh_docs",
            "health": f"{self.base_url_upload}/health",
            "get_namespace_details_by_userid": f"{self.base_url_upload}/get_namespace_details_by_userid",
            "get_docs_information": f"{self.base_url_upload}/get_docs_information",
        }
