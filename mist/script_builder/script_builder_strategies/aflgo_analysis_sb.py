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

class AFLGoAnalysisSB(ScriptBuilderStrategy):
    def __init__(self):
        super().__init__('Build a bash script that extracts CFG and CG from SUT.')

    def build_script(self, cctx: ContextProxy) -> Path:
        subject_dir: Path = cctx.select('subject_dir')
        work_dir: Path = cctx.select('work_dir')
        fuzzer_dir: Path = cctx.select('fuzzer_dir')
        findings_file: Path = cctx.select('findings_file')
        targets_file: Path = cctx.select('targets_file')
        aflgo: Path = cctx.select('aflgo_dir')
        build_prep_cmd = cctx.select('build_prep_cmd')
        build_cmd = cctx.select('build_cmd')

        lines = [
            "#!/bin/bash",
            "set -euo pipefail",
            f"cd {str(subject_dir)}",
            f"find {str(fuzzer_dir)} -mindepth 1 -maxdepth 1 ! -name temp -exec rm -rf {{}} +",
            f"find {str(work_dir)} -mindepth 1 -maxdepth 1 ! -name '{findings_file.name}' ! -name '{targets_file.name}' -exec rm -rf {{}} +",
            f"export AFLGO={str(aflgo)}",
            f"export TMP_DIR={str(work_dir)}",
            f"export CC=$AFLGO/instrument/aflgo-clang; export CXX=$AFLGO/instrument/aflgo-clang++",
            "export LDFLAGS=-lpthread",
            f'export ADDITIONAL="-targets={str(targets_file)} -outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"',
            f'{build_prep_cmd}',
            f'cd {str(fuzzer_dir)}',
            f'{build_cmd}',
            'cat $TMP_DIR/BBnames.txt | rev | cut -d: -f2- | rev | sort | uniq > $TMP_DIR/BBnames2.txt && mv $TMP_DIR/BBnames2.txt $TMP_DIR/BBnames.txt',
            'cat $TMP_DIR/BBcalls.txt | sort | uniq > $TMP_DIR/BBcalls2.txt && mv $TMP_DIR/BBcalls2.txt $TMP_DIR/BBcalls.txt'
        ]

        script = '\n'.join(lines)
        mist_dir: Path = cctx.select('mist_dir')
        script_file = mist_dir / "aflgo_analysis.sh"

        try:
            with open(script_file, "x") as f:
                f.write(script)
        except FileExistsError:
            return script_file

        script_file.chmod(0o775)
        cctx.update('aflgo_analysis_script_file', script_file)
        
        logger.info('Successfully generated the CFG and CG extraction script.')
        logger.info(f'Path: {script_file}')
        return script_file
        