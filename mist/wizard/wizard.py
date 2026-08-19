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
from collections import deque
from typing import List
import logging

from .wizard_step import WizardStep
from mist.campaign_environment import ContextProxy
from mist.utils.errors import WizardStepError, CCTXValidationError

logger = logging.getLogger(__name__)

class Wizard:
    def __init__(self, cctx: ContextProxy, steps: List[WizardStep] = None):
        self._steps = steps or []
        self._cctx = cctx

    def _loop(self) -> None:
        steps_queue = deque(self._steps)

        while steps_queue:
            step = steps_queue.popleft()

            try:
                if step.should_run(self._cctx):
                    step.print_header()
                    step.run(self._cctx)
            except (WizardStepError, CCTXValidationError) as e:
                logger.error(e)
                steps_queue.appendleft(step)
    
    def _validation_loop(self) -> None:
        while True:
            try:
                self._cctx.validate()
                self._cctx.dump()
                break
            except CCTXValidationError as e:
                logger.error(e)
                self._loop()


    def add_step(self, step: WizardStep) -> Wizard:
        self._steps.append(step)
        return self

    def launch(self) -> Wizard:
        try:
            self._loop()
            self._validation_loop()
        except KeyboardInterrupt:
            self._cctx.dump()
            raise
        except Exception as e:
            self._cctx.dump()
            raise
        return self