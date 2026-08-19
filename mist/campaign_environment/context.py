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

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Set
from pathlib import Path

from mist.utils.logging_manager import LoggingManager
from mist.definitions import MIST_ROOT_DIR, U_TERMINAL_EMULATOR

@dataclass
class Context(ABC):
    internal_supports: Dict[str, Any] = field(default_factory=lambda: {
        "mist_root_dir": MIST_ROOT_DIR,
        "check_cctx_completeness": False,
        "logging_manager": LoggingManager().use_console(),
        "terminal_emulator": U_TERMINAL_EMULATOR
    })

    @abstractmethod
    def to_json(self) -> str:
        pass

    @abstractmethod
    def from_json(self, file_path: Path) -> Set[str]:
        pass