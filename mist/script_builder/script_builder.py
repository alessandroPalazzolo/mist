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

from .script_builder_strategy import ScriptBuilderStrategy
from mist.campaign_environment import ContextProxy
from pathlib import Path
from typing import List

class ScriptBuilder:
    def __init__(self, s: ScriptBuilderStrategy, cctx: ContextProxy):
        self._strategy = s
        self._cctx = cctx
    
    def multiplex_scripts(self, scripts: List[Path]) -> Path:
        # FUTURE multiplex all phases scripts into a full one
        pass

    def set_strategy(self, s: ScriptBuilderStrategy) -> ScriptBuilder:
        self._strategy = s
        return self

    def build(self) -> Path:
        return self._strategy.build_script(self._cctx)