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

class SeedsDirV(Validator):
    def __init__(self):
        super().__init__('seeds_dir')

    def validate_field(self, cctx: ContextProxy) -> None:
        seeds_dir: Path = cctx.select(self._field)

        mist_dir: Path = cctx.select('mist_dir')
        out_dir: Path = cctx.select('fuzzer_dir') / 'out'
        log_file: Path = mist_dir / 'monitor.log'

        if str(seeds_dir) == '-':
            if not ( log_file.is_file() and out_dir.is_dir() ):
                raise CCTXValidationError('Impossible to resume fuzzing: previous results are missing.', self._field)
        elif not seeds_dir.is_dir():
            raise CCTXValidationError('Seeds directory does not exist.', self._field)
