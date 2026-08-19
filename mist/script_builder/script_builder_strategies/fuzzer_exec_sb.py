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
from typing import List

import logging

from mist.script_builder import ScriptBuilderStrategy
from mist.campaign_environment import ContextProxy

logger = logging.getLogger(__name__)

class FuzzerExecSB(ScriptBuilderStrategy):
    def __init__(self):
        super().__init__('Build a bash script that executes the fuzzer.')

    def build_script(self, cctx: ContextProxy) -> Path:
        aflgo_fuzzer = cctx.select('aflgo_dir') / 'afl-2.57b' / 'afl-fuzz'
        seeds_dir = cctx.select('seeds_dir')
        output_dir = cctx.select('fuzzer_dir') / 'out'
        harness_file = cctx.select('harness_file')
        harness_args: List[str] = cctx.select('harness_args')
        fuzzer_enhanced_perf = cctx.select('fuzzer_enhanced_perf')

        perf_options = 'export AFL_SKIP_CPUFREQ=1'

        if fuzzer_enhanced_perf:
           perf_options = '' 

        lines = [
            '#!/bin/bash',
            perf_options,
            f'{str(aflgo_fuzzer)} -m none -z exp -c 45 -i {str(seeds_dir)} -o {str(output_dir)} {str(harness_file)} {" ".join(harness_args)}',
        ]

        script = '\n'.join(lines) 
        mist_dir: Path = cctx.select('mist_dir')
        script_file = mist_dir / "fuzzer_exec.sh"

        with open(script_file, "w") as f:
            f.write(script)

        script_file.chmod(0o775)
        cctx.update('fuzzer_exec_script_file', script_file)

        logger.info('Successfully generated the fuzzer execution script.')
        logger.info(f'Path: {script_file}')
        return script_file