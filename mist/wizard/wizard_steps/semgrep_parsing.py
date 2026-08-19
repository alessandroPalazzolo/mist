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

import json
import subprocess
from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import PathValidator
from typing import List, Any
import re
import logging

from mist.wizard import WizardStep
from mist.campaign_environment import ContextProxy
from mist.utils.errors import WizardStepError

logger = logging.getLogger(__name__)

class SemgrepParsing(WizardStep):
    def __init__(self):
        super().__init__('Generate AFLGo Targets from Semgrep Findings')

    def _exec_semgrep(self, cctx: ContextProxy) -> Path:
        subject_dir_path: Path = cctx.select('subject_dir')
        output_file_path: Path = cctx.select('work_dir') / 'semgrep_findings.json'

        output_file_path.unlink(missing_ok=True)
        
        logger.info('Starting semgrep scan...')
        
        try:
            subprocess.run([
                'semgrep',
                'scan',
                '--config=p/security-audit',
                '--config=p/owasp-top-ten',
                '--config=auto',
                '--json',
                '--output',
                output_file_path,
                subject_dir_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            raise WizardStepError(f'Semgrep process exited with return code: {e.returncode}') from e

        logger.info('Semgrep scan completed successfully!')
        return output_file_path

    def _get_findings(self, cctx: ContextProxy) -> Path:
        has_findings_file = inquirer.confirm(
            message = 'Already have file with findings?',
            default = False
        ).execute()

        if has_findings_file:
            raw_file_path = inquirer.filepath(
                message="Enter file path:",
                default=str(cctx.select('work_dir')),
                validate=PathValidator(is_file=True, message="Not a file"),
            ).execute()
            file_path = Path(raw_file_path).expanduser().resolve()
        else:
            file_path = self._exec_semgrep(cctx) 

        return file_path
    

    def _triage_findings(self, results: List[Any]) -> List[Any]:
        filtered = [
            r 
            for r in results if 
            r['extra']["severity"] in ("WARNING", "MEDIUM", "HIGH", "ERROR", "CRITICAL") and 
            r['extra']['metadata']["category"] == "security" 
        ]

        seen = set()
        unique = []

        for r in filtered:
            key = (r['path'], r['start']['line'])
            if key not in seen:
                seen.add(key)
                unique.append(r)

        return unique
    
    def _normalize_findings(self, results: List[Any]) -> List[Any]:
        normalized = [
            {
                'path': Path(r['path']).name,
                'start_line': r['start']['line'],
                'function': r.get('extra', {}).get('metavars', {}).get('$FUNC', {}).get('abstract_content', 'undefined'),
                'cwe': r['extra']['metadata']['cwe'][0],
                'confidence': r['extra']['metadata']['confidence']
            }
            for r in results
        ]

        return normalized

    def _prompt_user_review(self, results: List[Any]) -> List[Any]:
        if not results:
            raise Exception()
        
        prompt_choices = [
            Choice(
                value = r,
                name = f"{r['path']}:{r['start_line']} | f: {r['function']} | {r['cwe']} | confidence: {r['confidence']}",
                enabled = False
            )
            for r in results
        ]
        
        selected_results = inquirer.checkbox(
            message = 'Select results:',
            choices = prompt_choices,
            transformer = lambda result: f"{len(result)} result{'s' if len(result) > 1 else ''} selected",
            instruction=f"({len(results)} interesting result{'s' if len(results) > 1 else ''}. Use spacebar to toggle)",
            cycle = False
        ).execute()

        if not selected_results:
            raise Exception()

        return selected_results
    
    ##
    # SemgrepParsing::_findings_to_targets() adds 3 targets for each Semgrep finding enabling a range of ±1 around it
    ##
    def _findings_to_targets(self, results: List[Any]) -> List[str]:
        targets = []

        for r in results:
            path = r.get('path')
            start_line = r.get('start_line')   
            if path and start_line:
                targets.extend([
                    f'{path}:{start_line-1}',
                    f'{path}:{start_line}',
                    f'{path}:{start_line+1}' 
                ])

        return list(set(targets))

    def _cull_findings(self, findings: Any) -> List[str]:
        results = findings.get('results')
        triaged_results = self._triage_findings(results)
        normalized_results = self._normalize_findings(triaged_results)
        reviewed_results = self._prompt_user_review(normalized_results)
        targets = self._findings_to_targets(reviewed_results)
        return targets
    
    def _prompt_manual_targets(self) -> List[str]:
        targets = []

        wants_manual_targets = inquirer.confirm(
            message = 'Define manual fuzzer targets?',
            long_instruction="Directed fuzzing needs at least 1 target. If NO is chosen Mist will run again this step.",
            default = True
        ).execute()
        
        def validator(targets: str) -> bool:
            isValid = True
            target_format = re.compile(r"^[^:\n]+:\d+$")
            for l in targets.strip().splitlines():
                l = l.strip()
                if not target_format.match(l):
                    isValid = False
                    break
            return isValid

        if wants_manual_targets:
            targets_string: str = inquirer.text(
                message="Enter targets:",
                long_instruction = 'Target format: [filename]:[line]\nOne target for each line.',
                multiline = True,
                validate = validator,
                invalid_message = 'Targets have wrong format.'
            ).execute()
        
        targets = targets_string.strip().splitlines()
        return targets
    
    def run(self, cctx: ContextProxy) -> bool:
        targets_file_path: Path = cctx.select('work_dir') / 'BBtargets.txt'
        findings_file_path: Path = self._get_findings(cctx)

        if not findings_file_path.is_file():
            raise WizardStepError(f'File not found: {findings_file_path}')
        
        cctx.update('findings_file', findings_file_path)

        with open(findings_file_path, 'r') as f:
            findings = json.load(f)

        try:
            targets: str = self._cull_findings(findings)
        except Exception as e:
            logger.warning(f'Found 0 interesting findings in {findings_file_path}.')
            targets: str = self._prompt_manual_targets()
            if not targets:
                raise WizardStepError(f'No targets defined.')

        cctx.update('targets_list', targets)

        with open(targets_file_path, 'w') as f:
            content = '\n'.join(targets)
            f.write(content)
        
        if not targets_file_path.is_file():
            raise WizardStepError(f'File not created: {findings_file_path}')
    
        cctx.update('targets_file', targets_file_path)

        logger.info(
            f"{len(targets)} target{'s' if len(targets) > 1 else ''} written to {targets_file_path.resolve()}"
        )
        return

    def should_run(self, cctx: ContextProxy) -> bool:
        decision = False
        produced_fields = [
            'findings_file',
            'targets_list',
            'targets_file'
        ]

        for f in produced_fields:
            if not cctx.field_is_set(f):
                decision = True
        
        return decision