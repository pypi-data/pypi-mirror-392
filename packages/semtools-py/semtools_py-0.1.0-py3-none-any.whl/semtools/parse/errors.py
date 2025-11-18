class ParseError(Exception):
    """Base exception for parsing errors."""


class ParseHttpError(ParseError):
    """Raised for HTTP-related errors during parsing."""


class ParseTimeoutError(ParseError):
    """Raised when a parsing job times out."""


class ParseRetryExhaustedError(ParseError):
    """Raised when all retry attempts for an operation have failed."""