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

from typing import List

from mist.campaign_environment import Validator, ContextProxy
from mist.utils.errors import CCTXValidationError

class HarnessArgsV(Validator):
    def __init__(self):
        super().__init__('harness_args')

    def validate_field(self, cctx: ContextProxy) -> None:
        input_src = cctx.select('harness_input_src')
        harness_args: List[str] = cctx.select(self._field)

        if input_src == 'file' and not '@@' in harness_args:
            raise CCTXValidationError('File input placeholder missing.', self._field)
