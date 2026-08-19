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

from mist.campaign_environment import Validator, ContextProxy
from mist.utils.errors import CCTXValidationError

class AFLGoAnalysisScriptFileV(Validator):
    def __init__(self):
        super().__init__('aflgo_analysis_script_file')

    def validate_field(self, cctx: ContextProxy) -> None:
        aflgo_analysis_script_file: Path = cctx.select(self._field)

        if not aflgo_analysis_script_file.is_file():
            raise CCTXValidationError('AFLGo analysis script file does not exist.', self._field)
