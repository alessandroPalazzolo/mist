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
from typing import List
import shlex
import textwrap
import logging
import subprocess

from mist.wizard import WizardStep
from mist.campaign_environment import ContextProxy
from mist.script_builder import ScriptBuilder
from mist.script_builder.script_builder_strategies import FuzzerExecSB
from mist.utils.errors import WizardStepError

logger = logging.getLogger(__name__)

class FuzzingSetup(WizardStep):
    def __init__(self):
        super().__init__('Define harness and fuzzing environment')

    def _has_seeds(self) -> bool:
        has_seeds = inquirer.confirm(
            message = 'Want to provide a seeds directory?',
            long_instruction="MIST will define an empty seed if none is provided",
            default = True
        ).execute()

        return has_seeds
    
    def _collect_seeds_dir_path(self) -> Path:
        raw_seeds_dir = inquirer.filepath(
            message = 'Path to directory:',
            default = str(Path.cwd()),
            validate = PathValidator(is_dir = True, message = 'Not a directory.'),
            only_directories=True
        ).execute()

        return Path(raw_seeds_dir).expanduser().resolve()
    
    def _select_seeds_optimizations(self) -> List[str]:
        # FUTURE
        return []
    
    def _collect_harness_file_paths(self, cctx: ContextProxy) -> tuple[Path, Path]:
        fuzzer_dir: Path = cctx.select('fuzzer_dir')
        checker_dir: Path = cctx.select('checker_dir')

        raw_f_harness_fpath = inquirer.filepath(
            message = 'Path to harness file:',
            validate = PathValidator(is_file = True, message = 'Not a file.'),
            default = str(fuzzer_dir)
        ).execute()

        f_harness_fpath = Path(raw_f_harness_fpath).expanduser().resolve()
        c_harness_fpath = checker_dir / f_harness_fpath.relative_to(fuzzer_dir)

        return (f_harness_fpath, c_harness_fpath)
    
    def _collect_harness_args(self, cctx: ContextProxy) -> str:
        input_source = inquirer.select(
            message = 'Select the harness input source:',
            choices = ['file', 'stdin']
        ).execute()

        cctx.update('harness_input_src', input_source)

        match input_source:
            case 'stdin':
                harness_args_string = inquirer.text(message = 'Enter args/flags for harness:').execute()
            case 'file':
                harness_args_string = inquirer.text(
                    message = 'Enter args/flags for harness:',
                    instruction = '(use @@ placeholder for the fuzzer input file)',
                    validate = lambda args: '@@' in args,
                    invalid_message = 'Should use the @@ placeholder.'
                ).execute()
            case _:
                raise WizardStepError(f'Input source "{input_source}" is not supported.')

        harness_args_list = shlex.split(harness_args_string)
        return harness_args_list
    
    def _use_enhanced_performance(self, cctx: ContextProxy) -> bool:
        script = cctx.select('mist_root_dir') / 'AFLGo' / 'afl-2.57b' / 'afl-system-config'

        instr = textwrap.dedent(
            f"""
            \n
            AFLGo requires some system changes for better fuzzing performance -
            see https://github.com/AFLplusplus/AFLplusplus/blob/stable/docs/fuzzing_in_depth.md

            Upon confirmation MIST will run a script provided by AFLPlusPlus -
            see https://github.com/AFLplusplus/AFLplusplus/blob/stable/afl-system-config
            The script requires sudo password.

            If you skip expect some performance drop. 
            """
        ).rstrip()

        user_choice = inquirer.confirm(
            message = 'Apply custom system config for fuzzing performance?',
            long_instruction=instr,
            default = False
        ).execute()

        if user_choice:
            try:
                subprocess.run([
                    'sudo', 'sh',
                    str(script)
                ], check=True)
            except subprocess.CalledProcessError:
                raise WizardStepError('Failed to apply the required performance system configs.')

        return user_choice
    
    def _prompt_resume_prev_fuzzing(self, cctx: ContextProxy) -> bool:
        user_choice = inquirer.confirm(
            message = 'Wish to resume from them?',
            default = True
        ).execute()

        return user_choice

    def run(self, cctx: ContextProxy) -> None:
        seeds_dir = None
        seeds_optimizations = []

        if self._has_seeds():
            seeds_dir = self._collect_seeds_dir_path()
            cctx.update('seeds_dir', seeds_dir)
            seeds_optimizations = self._select_seeds_optimizations()
            cctx.update('seeds_optimizations', seeds_optimizations)
        else:
            seeds_dir: Path = cctx.select('mist_root_dir') / 'testcases' / 'default'
            cctx.update('seeds_dir', seeds_dir)
            cctx.update('seeds_optimizations', [])

        f_harness_fpath, c_harness_fpath = self._collect_harness_file_paths(cctx)
        cctx.update('harness_file', f_harness_fpath)
        cctx.update('checker_harness_file', c_harness_fpath)
        harness_args = self._collect_harness_args(cctx)
        cctx.update('harness_args', harness_args)
        decision = self._use_enhanced_performance(cctx)
        cctx.update('fuzzer_enhanced_perf', decision)

        logger.info('Writing fuzzer execution script...')
        ScriptBuilder(FuzzerExecSB(), cctx).build()

        logger.info('All fuzzing environment saved.')
        return

    def should_run(self, cctx: ContextProxy) -> bool:
        produced_fields = [
            'seeds_dir',
            'seeds_optimizations',
            'harness_file',
            'checker_harness_file',
            'harness_args',
            'harness_input_src',
            'fuzzer_enhanced_perf',
            'fuzzer_exec_script_file'
        ]

        for f in produced_fields:
            if not cctx.field_is_set(f):
                return True

        mist_dir: Path = cctx.select('mist_dir')
        out_dir: Path = cctx.select('fuzzer_dir') / 'out'
        log_file: Path = mist_dir / 'monitor.log'
        decision = True

        if ( log_file.exists() and out_dir.exists() ):
            logger.warning('MIST found results from a previous fuzzing run!')
            if self._prompt_resume_prev_fuzzing(cctx):
                cctx.update('seeds_dir', Path('-'))
                logger.info('Updating fuzzer execution script...')
                ScriptBuilder(FuzzerExecSB(), cctx).build()
                logger.info('Fuzzing will resume from previous campaign results.')
                decision = False

        return decision