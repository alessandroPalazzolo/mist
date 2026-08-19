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

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Set
from pathlib import Path
import json

from mist.campaign_environment.context import Context

@dataclass
class AFLGoCampaignContext(Context):
    name: str | None = None
    author: str | None = None
    subject_dir: Path | None = None
    mist_dir: Path | None = None
    aflgo_dir: Path | None = None
    work_dir: Path | None = None
    fuzzer_dir: Path | None = None
    checker_dir: Path | None = None
    findings_file: Path | None = None
    targets_file: Path | None = None
    targets_list: List[str] | None = None
    build_prep_cmd: str | None = None
    build_cmd: str | None = None
    aflgo_analysis_script_file: Path | None = None
    checker_build_script_file: Path | None = None
    seeds_dir: Path | None = None
    seeds_optimizations: List[str] | None = None
    harness_file: Path | None = None
    checker_harness_file: Path | None = None
    harness_input_src: str | None = None
    harness_args: List[str] | None = None
    fuzzer_enhanced_perf: bool | None = None
    fuzzer_exec_script_file: Path | None = None
    aflgo_instrumentation_script_file: Path | None = None

    def to_json(self) -> str:
        raw_data = asdict(self)
        raw_data.pop('internal_supports')

        def serialize(obj):
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, list):
                return [serialize(el) for el in obj]
            if isinstance(obj, dict):
                return {key: serialize(val) for key, val in obj.items()}
            return obj

        data = serialize(raw_data)
        return json.dumps(data, indent=2) 

    def from_json(self, file_path: Path) -> Set[str]:
        loaded_fields: Set[str] = set()

        with open(file_path) as f:
            data: Dict[str, Any] = json.load(f)

        for k, v in data.items():
            is_path: bool = k.endswith("_dir") or k.endswith("_file")
            is_field: bool = k in self.__dataclass_fields__

            if not is_field or v is None:
                continue

            if is_path:
                v = Path(v)

            setattr(self, k, v)
            loaded_fields.add(k)
        
        return loaded_fields
