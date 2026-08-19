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

from __future__ import annotations
import logging
import logging.config
from pathlib import Path

from .logging_configs import *

class LoggingManager():
    def use_console(self) -> LoggingManager:
        config = CONSOLE_CFG()
        logging.config.dictConfig(config)
        return self
    
    def use_file(self, file_path: Path) -> LoggingManager:
        config = FILE_CFG(file_path)
        logging.config.dictConfig(config)
        return self

    def use_console_and_file(self, file_path: Path) -> LoggingManager:
        config = CONSOLE_AND_FILE_CFG(file_path)
        logging.config.dictConfig(config)
        return self
    
    def use_custom(self, cfg: Dict) -> LoggingManager:
        config = cfg
        logging.config.dictConfig(config)
        return self