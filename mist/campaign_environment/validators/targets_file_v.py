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
import re
from collections import Counter
from typing import List

from mist.campaign_environment import Validator, ContextProxy
from mist.utils.errors import CCTXValidationError

class TargetsFileV(Validator):
    def __init__(self):
        super().__init__('targets_file')

    def validate_field(self, cctx: ContextProxy) -> None:
        targets_file: Path = cctx.select(self._field)
        targets_list: List = cctx.select('targets_list')

        if not targets_file.is_file():
            raise CCTXValidationError('Targets file does not exist.', self._field)

        try:
            with open(targets_file) as f:
                lines = f.readlines()
        except OSError:
            raise CCTXValidationError('Unable to read targets file.', self._field)
        
        if not lines:
            raise CCTXValidationError('Targets file is empty.', self._field)
        
        target_format = re.compile(r"^[^:\n]+:\d+$")

        for (idx, l) in enumerate(lines, start = 1):
            if not target_format.match(l):
                raise CCTXValidationError(f'Target entry at line {idx} is invalid: {l}', self._field)

        if cctx.select('check_cctx_completeness'):
            with open(targets_file, 'r') as f:
                        bbtargets = [line.rstrip('\n') for line in f]
                        if not Counter(targets_list) == Counter(bbtargets):
                            raise CCTXValidationError('Mist campaign targets list and AFLGo BBtargets.txt contain different elements.', self._field)