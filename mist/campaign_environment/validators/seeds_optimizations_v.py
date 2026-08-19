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

class SeedsOptimizationsV(Validator):
    def __init__(self):
        super().__init__('seeds_optimizations')

    def validate_field(self, cctx: ContextProxy) -> None:
        seeds_optimizations: List[str] = cctx.select(self._field)
        methods = ['cmin', 'tmin']

        unsupported_method = any(opt not in methods for opt in seeds_optimizations)

        if seeds_optimizations and unsupported_method:
            raise CCTXValidationError('Seeds optimization method not supported.', self._field)
