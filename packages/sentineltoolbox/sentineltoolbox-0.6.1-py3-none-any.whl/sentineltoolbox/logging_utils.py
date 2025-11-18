import logging
from logging.config import dictConfig
from pathlib import Path
from typing import Any

from sentineltoolbox.exceptions import LoadingDataError
from sentineltoolbox.readers.open_standard_files import load_json
from sentineltoolbox.readers.resources import load_resource_file

logger = logging.getLogger("sentineltoolbox")

try:
    from colorama import Back, Fore, Style
except ImportError:
    DEFAULT_STDOUT_FORMATTER = "%(asctime)s [%(levelname)+8s] %(name)s\n    (%(funcName)s):" " %(message)s"
else:
    # For the sake of convenience, split log header from content
    DEFAULT_STDOUT_FORMATTER = (
        f"{Fore.YELLOW}%(asctime)s %(relativeCreated)12d"
        f" {Fore.WHITE}[{Style.BRIGHT}%(levelname)+8s{Style.RESET_ALL}]"
        f" {Fore.BLUE}{Fore.GREEN}%(name)s{Fore.RESET}\n   "
        f" {Fore.CYAN}%(funcName)s{Style.RESET_ALL}{Back.RESET}{Fore.RESET}:"
        f" {Fore.WHITE}%(message)s{Style.RESET_ALL}"
    )

DEFAULT_STDOUT_FORMATTER_NO_COLOR = "%(asctime)s [%(levelname)+8s] %(name)s\n    (%(funcName)s):" " %(message)s"

try:
    from colorlog import ColoredFormatter as ColoredFormatter
except ImportError:
    ColoredFormatter = logging.Formatter  # type: ignore


class EopfFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.module == "log" and record.funcName == "get_logger":
            return False
        else:
            return True


def disable_eopf_logging_side_effects(**kwargs: Any) -> None:
    """
    remove side effects on logging induced by EOLogging.get_logger().
    If user has defined explicitly an eopf configuration, this function has no effects.
    """
    try:
        from eopf import EOConfiguration
    except ImportError:
        if not kwargs.get("disable_log", False):
            # at this step, logging conf is not fully initialized so we need to disable logging manually is some cases
            logger.debug("disable_eopf_logging_side_effects has no effects, EOPF is not installed")
        return
    else:
        from eopf.common.constants import EOPF_CPM_DEFAULT_CONFIG_FILE

    eo_config = EOConfiguration()
    try:
        conf_files = eo_config._param_file_list
    except AttributeError:
        if not kwargs.get("disable_log", False):
            # at this step, logging conf is not fully initialized so we need to disable logging manually is some cases
            logger.info("cannot disable eopf logging side effects. EOPF/CPM internal configuration has changed")
        return

    if conf_files == {str(EOPF_CPM_DEFAULT_CONFIG_FILE)}:
        try:
            del eo_config._config_internal["logging"]["level"]
        except (KeyError, AttributeError):
            if not kwargs.get("disable_log", False):
                # at this step, logging conf is not fully initialized so we need to disable logging manually
                logger.info("cannot disable eopf logging side effects. EOPF/CPM internal configuration has changed")
            return

        try:
            eo_config._config_internal["logging"]["obfuscate"] = False
        except (KeyError, AttributeError):
            if not kwargs.get("disable_log", False):
                # at this step, logging conf is not fully initialized so we need to disable logging manually
                logger.info("cannot disable eopf logging side effects. EOPF/CPM internal configuration has changed")
            return


def build_colored_json_logging_config() -> dict[Any, Any]:
    file_formatter = "%(asctime)s %(relativeCreated)12d [%(levelname)+8s] %(name)s::(%(funcName)s): %(message)s"

    try:
        from colorama import Back, Fore, Style

        # For the sake of convenience, split log header from content
        console_formatter = (
            f"{Fore.YELLOW}%(asctime)s %(relativeCreated)12d"
            f" {Fore.WHITE}[{Style.BRIGHT}%(levelname)+8s{Style.RESET_ALL}]"
            f" {Fore.BLUE}{Fore.GREEN}%(name)s{Fore.RESET}\n   "
            f" {Fore.CYAN}%(funcName)s{Style.RESET_ALL}{Back.RESET}{Fore.RESET}:"
            f" {Fore.WHITE}%(message)s{Style.RESET_ALL}"
        )
    except ImportError:
        console_formatter = file_formatter

    json_dict = build_json_logging_config(console_formatter, file_formatter)

    return json_dict


def build_json_logging_config(console_formatter: str, file_formatter: str) -> dict[Any, Any]:
    json_dict = {
        "version": 1,
        "loggers": {
            "eopf": {"handlers": ["console"], "propagate": 0},
        },
        "formatters": {
            "console": {"format": console_formatter},
            "file": {"format": file_formatter},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "console",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "file",
                "filename": "s2msi_l2a_proto.log",
            },
        },
        "root": {"level": "INFO", "handlers": ["file", "console"]},
    }

    return json_dict


def init_logging(logging_conf: str | dict[Any, Any] | None = None, **kwargs: Any) -> None:
    if logging_conf:
        disable_eopf_logging_side_effects(**kwargs)

    if isinstance(logging_conf, dict):
        dictConfig(logging_conf)
    elif isinstance(logging_conf, str):
        conf = None
        try:
            conf = load_resource_file(f"logging_conf/{logging_conf}", **kwargs)
        except FileNotFoundError:
            if Path(logging_conf).is_file():
                try:
                    conf = load_json(logging_conf)
                except LoadingDataError:
                    logger.warning(f"Invalid json {logging_conf!r}")
            else:
                logger.warning(
                    f"Cannot find logging config sentineltoolbox/resources/logging_conf/{logging_conf} or "
                    f"in path {logging_conf!r} ",
                )

        if conf:
            dictConfig(conf)


def setup_compare_loggers(
    stream: Any = None,
    level: int = logging.INFO,
    verbose: bool = False,
) -> tuple[logging.Logger, logging.Logger, logging.Logger, logging.Logger]:
    """
    Configure and return loggers for product comparison.

    This function should only be called from CLI/main functions, not from library code.

    Parameters
    ----------
    stream : TextIO, optional
        Output stream for handlers. Defaults to sys.stderr
    level : int, optional
        Logging level. Defaults to INFO
    verbose : bool, optional
        If True, sets level to DEBUG

    Returns
    -------
    tuple[logging.Logger, logging.Logger, logging.Logger, logging.Logger]
        (main_logger, passed_logger, failed_logger)
    """
    import sys

    if stream is None:
        stream = sys.stderr

    if verbose:
        level = logging.DEBUG

    # Get the loggers (don't create new ones if they exist)
    main_logger = logging.getLogger("sentineltoolbox.compare")
    passed_logger = logging.getLogger("sentineltoolbox.compare.success")
    failed_logger = logging.getLogger("sentineltoolbox.compare.fail")
    bare_logger = logging.getLogger("sentineltoolbox.compare.bare")

    # Clear existing handlers to avoid duplicates
    main_logger.handlers.clear()
    passed_logger.handlers.clear()
    failed_logger.handlers.clear()
    bare_logger.handlers.clear()

    # Set levels and prevent propagation
    main_logger.setLevel(level)
    passed_logger.setLevel(logging.INFO)
    failed_logger.setLevel(logging.INFO)
    bare_logger.setLevel(logging.INFO)

    main_logger.propagate = False
    passed_logger.propagate = False
    failed_logger.propagate = False
    bare_logger.propagate = False

    # Create handlers
    main_handler = logging.StreamHandler(stream=stream)
    main_handler.setLevel(level)
    main_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    main_handler.setFormatter(main_formatter)
    main_logger.addHandler(main_handler)

    passed_formatter = ColoredFormatter(
        "%(log_color)s*** PASSED: %(reset)s %(message)s",
        log_colors={"INFO": "bold_green"},
        stream=stream,
    )
    failed_formatter = ColoredFormatter(
        "%(log_color)s*** FAILED: %(reset)s %(message)s",
        log_colors={"INFO": "bold_red"},
        stream=stream,
    )

    passed_handler = logging.StreamHandler(stream=stream)
    passed_handler.setLevel(logging.INFO)
    passed_handler.setFormatter(passed_formatter)
    passed_logger.addHandler(passed_handler)

    failed_handler = logging.StreamHandler(stream=stream)
    failed_handler.setLevel(logging.INFO)
    failed_handler.setFormatter(failed_formatter)
    failed_logger.addHandler(failed_handler)

    bare_handler = logging.StreamHandler(stream=stream)
    bare_handler.setLevel(logging.INFO)
    bare_logger.addHandler(bare_handler)

    return main_logger, passed_logger, failed_logger, bare_logger


def setup_conversion_loggers(
    stream: Any = None,
) -> tuple[logging.Logger, logging.Logger, logging.Logger]:
    """
    Configure and return loggers for product conversion reports.

    This function should only be called from CLI/main functions, not from library code.

    Parameters
    ----------
    stream : TextIO, optional
        Output stream for handlers. Defaults to sys.stderr

    Returns
    -------
    tuple[logging.Logger, logging.Logger, logging.Logger]
        (main_logger, passed_logger, failed_logger)
    """
    import sys

    if stream is None:
        stream = sys.stderr

    # Get the loggers
    main_logger = logging.getLogger("sentineltoolbox.conversion")
    passed_logger = logging.getLogger("sentineltoolbox.conversion.success")
    failed_logger = logging.getLogger("sentineltoolbox.conversion.fail")

    # Clear existing handlers to avoid duplicates
    main_logger.handlers.clear()
    passed_logger.handlers.clear()
    failed_logger.handlers.clear()

    # Set levels and prevent propagation
    main_logger.setLevel(logging.INFO)
    passed_logger.setLevel(logging.INFO)
    failed_logger.setLevel(logging.INFO)

    main_logger.propagate = False
    passed_logger.propagate = False
    failed_logger.propagate = False

    # Create and configure handlers
    main_handler = logging.StreamHandler(stream)
    main_handler.setFormatter(logging.Formatter("INFO: %(message)s"))
    main_logger.addHandler(main_handler)

    passed_handler = logging.StreamHandler(stream)
    passed_handler.setFormatter(logging.Formatter("SUCCESS: %(message)s"))
    passed_logger.addHandler(passed_handler)

    failed_handler = logging.StreamHandler(stream)
    failed_handler.setFormatter(logging.Formatter("TO CHECK: %(message)s"))
    failed_logger.addHandler(failed_handler)

    return main_logger, passed_logger, failed_logger
