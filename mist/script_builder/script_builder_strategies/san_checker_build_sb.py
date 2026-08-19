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
import logging

from mist.script_builder import ScriptBuilderStrategy
from mist.campaign_environment import ContextProxy

logger = logging.getLogger(__name__)

class SANCheckerBuildSB(ScriptBuilderStrategy):
    def __init__(self):
        super().__init__('Build a bash script that instruments the SUT with ASAN for runtime offline checking.')
    
    def build_script(self, cctx: ContextProxy) -> Path:
        subject_dir: Path = cctx.select('subject_dir')
        checker_dir: Path = cctx.select('checker_dir')
        build_cmd = cctx.select('build_cmd')
        build_prep_cmd = cctx.select('build_prep_cmd')

        lines = [
            '#!/bin/bash',
            'set -euo pipefail',
            f'cd {str(subject_dir)}',
            'export CC=$(command -v clang-14 || command -v gcc)',
            'export CXX=$(command -v clang++-14 || command -v g++)',
            'export LDFLAGS="-fsanitize=address"',
            'export ADDITIONAL="-O1 -g -fsanitize=address -fno-omit-frame-pointer"',
            f'{build_prep_cmd}',
            f'cd {str(checker_dir)}',
            f'{build_cmd}'
        ]

        script = '\n'.join(lines)
        mist_dir: Path = cctx.select('mist_dir')
        script_file = mist_dir / "checker_build.sh"

        try:
            with open(script_file, "x") as f:
                f.write(script)
        except FileExistsError:
            return script_file

        script_file.chmod(0o775)
        cctx.update('checker_build_script_file', script_file)
        
        logger.info('Successfully generated the Checker build script.')
        logger.info(f'Path: {script_file}')
        return script_file