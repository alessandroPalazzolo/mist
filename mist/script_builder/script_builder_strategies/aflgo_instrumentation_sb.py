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

class AFLGoInstrumentationSB(ScriptBuilderStrategy):
    def __init__(self):
        super().__init__('Build a bash script that instruments the SUT with distance metrics based on Semgrep findings, then fuzz with AFLGo.')

    def build_script(self, cctx: ContextProxy) -> Path:
        subject_dir: Path = cctx.select('subject_dir')
        work_dir: Path = cctx.select('work_dir')
        fuzzer_dir: Path = cctx.select('fuzzer_dir')
        aflgo: Path = cctx.select('aflgo_dir')
        build_cmd = cctx.select('build_cmd')
        harness_file: Path = cctx.select('harness_file')

        lines = [
            '#!/bin/bash',
            'set -euo pipefail',
            f'cd {str(subject_dir)}',
            f'export AFLGO={str(aflgo)}',
            f'export TMP_DIR={str(work_dir)}',
            'export CC=$AFLGO/instrument/aflgo-clang; export CXX=$AFLGO/instrument/aflgo-clang++',
            'export LDFLAGS=-lpthread',
            f'$AFLGO/distance/gen_distance_orig.sh {harness_file.parent} $TMP_DIR {harness_file.name}',
            'export ADDITIONAL="-distance=$TMP_DIR/distance.cfg.txt"',
            f'cd {str(fuzzer_dir)}',
            f'{build_cmd}'
        ]

        script = '\n'.join(lines) 
        mist_dir: Path = cctx.select('mist_dir')
        script_file = mist_dir / "aflgo_instrumentation.sh"

        try:
            with open(script_file, "x") as f:
                f.write(script)
        except FileExistsError:
            return script_file

        script_file.chmod(0o775)
        cctx.update('aflgo_instrumentation_script_file', script_file)

        logger.info('Successfully generated the AFLGo instrumentation script.')
        logger.info(f'Path: {script_file}')
        return script_file
        