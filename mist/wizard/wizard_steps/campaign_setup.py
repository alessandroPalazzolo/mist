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
from InquirerPy.validator import PathValidator
from pathlib import Path
import logging
import sys

from mist.wizard import WizardStep
from mist.campaign_environment import ContextProxy
from mist.utils.errors import WizardStepError
from mist.utils.logging_manager import LoggingManager
from mist.utils.runtime_frobs import RuntimeFrobs

logger = logging.getLogger(__name__)

class CampaignSetup(WizardStep):
    def __init__(self):
        super().__init__('Setup Campaign Environment')

    def _resume_prev_campaign(self, dir: Path, cctx: ContextProxy) -> None:
        mist_dir = dir / '.mist'
        cctx_file = mist_dir / 'campaign_context.json'
        log_file = mist_dir / 'mist.log'
        should_resume = False

        if mist_dir.is_dir() and cctx_file.is_file():
            should_resume = True
            log_file: Path = mist_dir / 'mist.log'
            logmgr: LoggingManager = cctx.select('logging_manager')
            logmgr.use_console_and_file(log_file)
            cctx.consume(cctx_file)

        return should_resume

    def run(self, cctx: ContextProxy) -> None:
        raw_subject_dir = inquirer.filepath(
            message = "Enter the SUT root directory:",
            default = str(Path.cwd()),
            validate = PathValidator(is_dir = True, message = 'Not a directory.'),
            only_directories=True
        ).execute()
        subject_dir: Path = Path(raw_subject_dir).expanduser().resolve()

        if self._resume_prev_campaign(subject_dir, cctx):
            RuntimeFrobs(cctx).apply(sys.argv)
            return
        
        cctx.update('subject_dir', subject_dir)

        campaign_name = inquirer.text(message='Enter the campaign name:').execute()
        cctx.update('name', campaign_name)
        author = inquirer.text(message='Name of the author:').execute()
        cctx.update('author', author)

        mist_root_dir = cctx.select("mist_root_dir")

        raw_aflgo_dir = inquirer.filepath(
            message = 'Use a custom AFLGo build:',
            default = str(mist_root_dir / 'AFLGo'),
            validate = PathValidator(is_dir = True, message = 'Not a directory.'),
            only_directories=True
        ).execute()
        aflgo_dir: Path = Path(raw_aflgo_dir).expanduser().resolve()
        cctx.update('aflgo_dir', aflgo_dir)

        fuzzer_dir: Path = subject_dir / 'obj-aflgo'
        work_dir: Path = fuzzer_dir / 'temp'
        checker_dir: Path = subject_dir / 'obj-asan'
        mist_dir: Path = subject_dir / '.mist'

        try:
            work_dir.mkdir(parents = True, exist_ok = True)
        except OSError as e:
            raise WizardStepError(f'Error: Failed to create {work_dir.resolve()}') from e
        cctx.update('fuzzer_dir', fuzzer_dir)
        cctx.update('work_dir', work_dir)

        try:
            checker_dir.mkdir(exist_ok = True)
        except OSError as e:
            raise WizardStepError(f'Error: Failed to create {checker_dir.resolve()}') from e
        cctx.update('checker_dir', checker_dir)

        try:
            mist_dir.mkdir(exist_ok = True)
        except OSError as e:
            raise WizardStepError(f'Error: Failed to create {mist_dir.resolve()}') from e
        cctx.update('mist_dir', mist_dir)

        log_file: Path = mist_dir / 'mist.log'
        logmgr: LoggingManager = cctx.select('logging_manager')
        logmgr.use_console_and_file(log_file)

        logger.info('All environment configuration saved.')
        return

    def should_run(self, cctx: ContextProxy) -> bool:
        decision = False
        produced_fields = [
            'subject_dir',
            'name',
            'author',
            'aflgo_dir',
            'fuzzer_dir',
            'work_dir',
            'checker_dir',
            'mist_dir'
        ]

        for f in produced_fields:
            if not cctx.field_is_set(f):
                decision = True
        
        return decision
