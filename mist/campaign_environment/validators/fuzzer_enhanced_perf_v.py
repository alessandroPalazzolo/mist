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

from mist.campaign_environment import Validator, ContextProxy
from mist.utils.errors import CCTXValidationError
from mist.definitions import IS_DOCKER_CONTAINER

class FuzzerEnhancedPerfV(Validator):
    def __init__(self):
        super().__init__('fuzzer_enhanced_perf')

    def validate_field(self, cctx: ContextProxy) -> None:
        fuzzer_enhanced_perf: bool = cctx.select(self._field)
        linux_scaling_governor_paths = [
            Path('/sys/devices/system/cpu/cpufreq/scaling_governor'),
            Path('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor'),
            Path('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor')
        ]

        for f in linux_scaling_governor_paths:
            if f.is_file():
                scaling_governor = f.read_text().strip()

        if IS_DOCKER_CONTAINER and fuzzer_enhanced_perf:
            raise CCTXValidationError('MIST is running in a Docker container. High performance fuzzing is not currently supported.', self._field)

        if ( fuzzer_enhanced_perf == True ) and ( scaling_governor != 'performance' ):
            raise CCTXValidationError('System is not configured for high performance fuzzing.', self._field)

        fuzzer_exec_script: Path = cctx.select('fuzzer_exec_script_file')
        fuzzer_exec_script_isValid: bool = cctx.field_is_set('fuzzer_exec_script_file') and fuzzer_exec_script.exists()
        drop_high_performance: bool = fuzzer_enhanced_perf == False

        if ( drop_high_performance and fuzzer_exec_script_isValid ):
            with open(fuzzer_exec_script, 'r') as f:
                if 'AFL_SKIP_CPUFREQ=1' not in f.read():
                    raise CCTXValidationError(
                        'Cannot run fuzzer with the current CPU scaling algorithm. You might want to set AFL_SKIP_CPUFREQ in the fuzzer script.\n' \
                        f'Path: {fuzzer_exec_script}', 
                        self._field
                    )