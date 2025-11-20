import inspect
import logging
from datetime import datetime
from functools import wraps

from django.conf import settings

from fango.auth import context_request_id, context_user

logger = logging.Logger("uvicorn.access")
handler = logging.StreamHandler()

__all__ = ["logger", "log_params"]


class ColoredFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;7m"
    bold_red = "\x1b[38;5;196m"
    reset = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        record.levelname = f"{record.levelname}:".ljust(10)
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


handler.setFormatter(ColoredFormatter("%(levelname)s%(message)s"))
logger.setLevel(logging.INFO)
logger.addHandler(handler)

arg_prefix = "\t\t--> "


def log_params(prefix):
    """
    Decorator for logging function call with args.

    """

    def log(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if settings.ENABLE_CALL_LOG:
                bound_arguments = inspect.signature(func).bind(*args, **kwargs)
                bound_arguments.apply_defaults()
                args_reprs = [arg_prefix + f"{name}={value!r}" for name, value in bound_arguments.arguments.items()]
                signature = "\n".join(args_reprs)
                logger.info(f"[{prefix}] call: {func.__name__} with params:\n{signature}\n")
            return func(*args, **kwargs)

        return wrapper

    return log


def create_log_event(data: dict, level=logging.INFO, username=None) -> None:
    """
    Log data with timestamp, request_id, and user context.

    """

    if not username:
        user = context_user.get()
        username = user.username

    request_id = context_request_id.get(None)

    current_frame = inspect.currentframe()
    function_name = current_frame.f_back.f_code.co_name

    logging_event = {
        "_datetime": datetime.now().isoformat(),
        "_function": function_name,
        "_request_id": request_id,
        "_username": username,
        **data,
    }

    match level:
        case logging.DEBUG:
            logger.debug(logging_event)
        case logging.INFO:
            logger.info(logging_event)
        case logging.WARNING:
            logger.warning(logging_event)
        case logging.ERROR:
            logger.error(logging_event)
