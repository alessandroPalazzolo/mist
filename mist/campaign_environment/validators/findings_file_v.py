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
import json

from mist.campaign_environment import Validator
from mist.campaign_environment import ContextProxy
from mist.utils.errors import CCTXValidationError

class FindingsFileV(Validator):
    def __init__(self):
        super().__init__('findings_file')

    def validate_field(self, cctx: ContextProxy) -> None:
        findings_file: Path = cctx.select(self._field)

        if not findings_file.is_file():
            raise CCTXValidationError('Findings file does not exist.', self._field)
        
        try:
            with findings_file.open('r', encoding = 'utf-8') as f:
                json.load(f)
        except json.JSONDecodeError:
            raise CCTXValidationError('Findings file is has invalid JSON.', self._field) 
        except OSError:
            raise CCTXValidationError('Unable to read findings file.', self._field)