# vintrick-backend/tools/utils/error_utils.py

import logging
from functools import wraps

def log_exception(logger: logging.Logger, exc: Exception, message: str = None):
    """
    Log an exception with optional message.
    """
    if message:
        logger.error(f"{message}: {exc}", exc_info=True)
    else:
        logger.error(f"Exception: {exc}", exc_info=True)

def catch_and_log_errors(logger: logging.Logger, default_return=None):
    """
    Decorator for catching errors and logging them.
    Returns default_return if exception is raised.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                logger.error(f"Exception in {func.__name__}: {exc}", exc_info=True)
                return default_return
        return wrapper
    return decorator

# FastAPI exception handlers (for use in main.py)
from fastapi.responses import JSONResponse

def http_exception_handler(request, exc):
    logging.error(f"HTTP Error: {getattr(exc, 'detail', str(exc))}")
    return JSONResponse(
        status_code=getattr(exc, 'status_code', 500),
        content={"detail": getattr(exc, "detail", "HTTP Exception")}
    )

def validation_exception_handler(request, exc):
    # Optionally provide extra help message for clients
    logging.error(f"Validation error: {exc.errors()} Body: {getattr(exc, 'body', None)}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": getattr(exc, "body", None),
            "message": (
                "Validation failed. Check field types and required fields. "
                "Nested objects can be null or omitted. jobNumber must be a string."
            ),
            "help_url": "https://errors.pydantic.dev/2.11/v/"
        }
    )

def generic_exception_handler(request, exc):
    logging.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )