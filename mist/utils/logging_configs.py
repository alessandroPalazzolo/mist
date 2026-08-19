'''
Copyright 2026 Alessandro Palazzolo

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from pathlib import Path
from typing import Dict

def CONSOLE_AND_FILE_CFG(log_file: Path) -> Dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "verbose": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            },
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s[ %(levelname)s ] %(message)s",
                "log_colors": {
                    "DEBUG": "white",
                    "INFO": "thin,white",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "colored",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "verbose",
                "filename": str(log_file),
                "mode": "w",
                "maxBytes": 1_000_000,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },

        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },

        "loggers": {
            "asyncio": {
                "level": "WARNING",
                "propagate": False
            }
        }
    }

def CONSOLE_CFG() -> Dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s[ %(levelname)s ] %(message)s",
                "log_colors": {
                    "DEBUG": "white",
                    "INFO": "thin,white",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "colored",
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "loggers": {
            "asyncio": {
                "level": "WARNING",
                "propagate": False
            }
        }
    }

def FILE_CFG(log_file: Path) -> Dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "verbose": {
                "format": "%(asctime)s | %(message)s",
            }
        },

        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "verbose",
                "filename": str(log_file),
                "mode": "w",
                "maxBytes": 1_000_000,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },

        "root": {
            "level": "DEBUG",
            "handlers": ["file"],
        },

        "loggers": {
            "asyncio": {
                "level": "WARNING",
                "propagate": False
            }
        }
    }
