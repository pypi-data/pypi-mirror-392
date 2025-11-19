import os
import csv
import logging
from pathlib import Path
from datetime import datetime
import json
import traceback
import time
from typing import List
# Heavy libs are imported at runtime when needed in real environments.

from .exceptions import FileProcessingError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class FileProcessor:
    SUPPORTED_EXTENSIONS = ['txt', 'csv', 'json', 'py', 'docx', 'pdf']

    @staticmethod
    def read_file_content(filepath: str) -> str:
        ext = filepath.lower().split('.')[-1]
        if ext in ['txt', 'csv', 'py', 'json']:
            with open(filepath, encoding='utf-8') as f:
                return f.read()
        # Defer complex parsing to runtime imports to avoid import-time failures.
        if ext == 'docx':
            try:
                from docx import Document
            except Exception as e:
                raise FileProcessingError(f"python-docx not available: {e}")
            doc = Document(filepath)
            return '\n'.join(p.text for p in doc.paragraphs)
        if ext == 'pdf':
            try:
                import PyPDF2
            except Exception as e:
                raise FileProcessingError(f"PyPDF2 not available: {e}")
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return '\n'.join(p.extract_text() or '' for p in reader.pages)
        raise FileProcessingError(f'Unsupported extension: {ext}')

    @staticmethod
    def get_file_size(filepath: str) -> int:
        return os.path.getsize(filepath)

    @staticmethod
    def is_supported_file(filename: str) -> bool:
        ext = filename.lower().split('.')[-1]
        return ext in FileProcessor.SUPPORTED_EXTENSIONS

class Logger:
    def __init__(self, log_dir: str):
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        self.skipped_log = Path(log_dir) / 'skipped_files_log.csv'
        self.api_error_log = Path(log_dir) / 'api_error_log.csv'
        self.performance_log = Path(log_dir) / 'api_performance_log.csv'

    def _write_csv_log(self, path: Path, header: List[str], row: List):
        exists = path.exists()
        with open(path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(header)
            writer.writerow(row)

    def log_skipped_file(self, filename: str, reason: str):
        self._write_csv_log(self.skipped_log, ['ts', 'filename', 'reason'], [datetime.utcnow().isoformat(), filename, reason])

    def log_api_error(self, operation: str, batch_num: int, error_message: str):
        self._write_csv_log(self.api_error_log, ['ts', 'operation', 'batch_num', 'err'], [datetime.utcnow().isoformat(), operation, batch_num, error_message])

    def log_performance(self, operation=None, batch_num=None, latency=None,
                    request_size=None, response_size=None, result_count=None,
                    files_processed=None, error: Exception = None):
        """
        SAFE CSV logger for all SDK operations.
        It will never throw TypeError regardless of input type.
        """

        logfile = getattr(self, "perf_csv", "performance_logs.csv")

        # --- Safe stringify for ANY type ---
        def safe_str(value):
            try:
                if isinstance(value, (list, tuple, set)):
                    return ",".join(str(v) for v in value)
                return str(value) if value is not None else ""
            except Exception:
                return "UNSERIALIZABLE"

        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": safe_str(operation),
            "batch_num": safe_str(batch_num),
            "latency_ms": safe_str(latency),
            "request_size": safe_str(request_size),
            "response_size": safe_str(response_size),
            "result_count": safe_str(result_count),
            "files_processed": safe_str(files_processed),
            "error": safe_str(error),
        }

        try:
            file_exists = os.path.isfile(logfile)

            with open(logfile, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())

                if not file_exists:
                    writer.writeheader()

                writer.writerow(row)

        except Exception:
            print("[CSV LOGGING ERROR] Could not write performance log:")
            print(traceback.format_exc())

class BatchManager:
    def __init__(self, max_files: int, max_size_mb: int):
        self.max_files = max_files
        self.max_bytes = max_size_mb * 1024 * 1024

    def create_batches(self, files: List[str], base_path: str) -> List[List[str]]:
        file_info = []
        for f in files:
            p = os.path.join(base_path, f)
            try:
                size = os.path.getsize(p)
                if size <= self.max_bytes:
                    file_info.append((f, size))
            except Exception:
                continue

        batches = []
        cur = []
        cur_size = 0
        for fname, size in file_info:
            if len(cur) >= self.max_files or (cur_size + size) > self.max_bytes:
                if cur:
                    batches.append(cur)
                cur = []
                cur_size = 0
            cur.append(fname)
            cur_size += size
        if cur:
            batches.append(cur)
        return batches
