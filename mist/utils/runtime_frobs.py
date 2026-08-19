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

from mist.campaign_environment import ContextProxy
from mist.utils.errors import WizardStepError

class RuntimeFrobs():
    def __init__(self, cctx: ContextProxy):
        self._cctx = cctx

    def _edit_targets(self) -> None:
        self._cctx.remove('targets_list')
        self._cctx.remove('harness_file')

    def apply(self, args: List[str]) -> None:
        for cmd in args[1:]:
            match cmd:
                case 'edit-targets':
                    self._edit_targets()
                    pass
                case _:
                    raise WizardStepError(f'mist {cmd}: operation not supported.')