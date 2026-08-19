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
import textwrap
import logging

from mist.wizard import WizardStep
from mist.campaign_environment import ContextProxy

logger = logging.getLogger(__name__)

class SUTBuildSetup(WizardStep):
    def __init__(self):
        super().__init__('Configure SUT Build Commands')

    def _collect_preparation_cmds(self) -> str:
        cmds = inquirer.text(
            message = 'Enter preparation commands to set up the build system:',
            multiline = True,
            default = './autogen.sh; make distclean'
        ).execute()

        return cmds
    
    def _collect_build_cmds(self, cctx: ContextProxy) -> str:
        fuzzer_dir: Path = cctx.select('fuzzer_dir')
        cc = Path(cctx.select('aflgo_dir')) / 'instrument' / 'aflgo-clang'
        cxx = Path(cctx.select('aflgo_dir')) / 'instrument' / 'aflgo-clang++'
        
        default_build_cmd = textwrap.dedent(
            f"""
            CFLAGS="$ADDITIONAL" CXXFLAGS="$ADDITIONAL" ../configure --disable-shared --prefix=`pwd`
            make clean; make
            """
        ).strip()

        long_instruction = textwrap.dedent(
            f"""
            \n
            Defined environment variables (do not override!):
            $CC
            $CXX
            $LDFLAGS = -lpthread\n
            [ WARNING ] The provided commands will later be run from {str(fuzzer_dir)} (the SUT is in the parent dir)
            [ WARNING ] If needed use $CC and $CXX instead of hardcoding compilers.\n
            These build commands are collected now to generate some campaign automation scripts. 
            You can review and edit each script later to fit any SUT-specific requirements before execution.
            """
        ).rstrip()

        cmds = inquirer.text(
            message="Enter the SUT build commands:",
            instruction = '(use $ADDITIONAL placeholder for AFLGo compile flags)',
            long_instruction = long_instruction,
            multiline = True,
            default = default_build_cmd,
            validate = lambda s: '$ADDITIONAL' in s,
            invalid_message = 'Should use the $ADDITIONAL placeholder.'
        ).execute()

        return cmds

    def run(self, cctx: ContextProxy) -> None:
        preparation_cmds = self._collect_preparation_cmds()
        cctx.update('build_prep_cmd', preparation_cmds)
        build_cmds = self._collect_build_cmds(cctx)
        cctx.update('build_cmd', build_cmds)

        logger.info(f'All build commands saved.')
        return
    
    def should_run(self, cctx: ContextProxy) -> bool:
        decision = False
        produced_fields = [
            'build_prep_cmd',
            'build_cmd'
        ]

        for f in produced_fields:
            if not cctx.field_is_set(f):
                decision = True
        
        return decision