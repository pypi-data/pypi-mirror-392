from enum import StrEnum


class JobStatus(StrEnum):
    """Represents the status of a LlamaParse job."""

    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    ERROR = "ERROR"
    CANCELED = "CANCELED"


class ParseBackendType(StrEnum):
    """Represents the type of parsing backend."""

    LLAMA_PARSE = "llama-parse"