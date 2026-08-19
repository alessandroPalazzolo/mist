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

from InquirerPy import inquirer
from pathlib import Path
import subprocess
import logging

from mist.campaign_environment import ContextProxy
from mist.wizard import WizardStep
from mist.script_builder import ScriptBuilder
from mist.script_builder.script_builder_strategies import SANCheckerBuildSB
from mist.utils.errors import WizardStepError

logger = logging.getLogger(__name__)

class SANCheckerBuild(WizardStep):
    def __init__(self):
        super().__init__('Build an offline checker using ASAN instrumentation')

    def _prompt_user_choice(self) -> bool:
        user_choice = inquirer.confirm(
            message = 'Wish to update it?',
            long_instruction="This might take a few minutes.",
            default = False
        ).execute()

        return user_choice

    def run(self, cctx: ContextProxy) -> None:
        sb = ScriptBuilder(SANCheckerBuildSB(), cctx)
        logger.info('Writing the Checker build script...')
        script: Path = sb.build()

        inquirer.confirm(
            message = 'Review the Checker build script before execution!',
            instruction="(press ENTER when ready)",
            long_instruction = f'PATH: {str(script)}',
            default = True
        ).execute()

        try:
            subprocess.run(str(script), check = True)
        except subprocess.CalledProcessError as e:
            raise WizardStepError(f'Checker build script exited with error code: {e.returncode}') from e
    
    def should_run(self, cctx: ContextProxy) -> bool:
        script_field_is_set = cctx.field_is_set('checker_build_script_file')
        checker_dir: Path = cctx.select('checker_dir')
        is_empty_dir = checker_dir.is_dir() and (not any(checker_dir.iterdir()))
        decision = True
        
        if script_field_is_set and not is_empty_dir:
            logger.warning('It seems that a previous Checker build already exists!')
            decision = self._prompt_user_choice()

        return decision
