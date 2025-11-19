class VectorLakeError(Exception):
    pass

class APIError(VectorLakeError):
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class FileProcessingError(VectorLakeError):
    pass
