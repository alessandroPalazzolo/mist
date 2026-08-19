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

from __future__ import annotations
from typing import List, Any, Set, Optional
from pathlib import Path
import logging
import copy
from tqdm import tqdm
import os

from .context import Context
from .validator import Validator
from mist.utils.errors import CCTXValidationError
from mist.utils.logging_manager import LoggingManager

logger = logging.getLogger(__name__)

class ContextProxy:
    def __init__(self, cctx: Context, validators: List[Validator] = None):
        self._cctx = cctx
        self._validators = validators or []
        self._chain_validators()
        self._completed_fields: Set[str] = set()

    def _temp_developer_log(self, msg: str) -> None:
        log_file: Path = self.select('mist_dir') / 'mist.log'
        logmgr: LoggingManager = self.select('logging_manager')
        logmgr.use_file(log_file)
        logger.warning(msg)
        logmgr.use_console_and_file(log_file)

    def _chain_validators(self) -> None:
        if self._validators:
            for v in self._validators:
                v.set_next(None)

            for i in range(len(self._validators) - 1):
                self._validators[i].set_next(self._validators[i+1])

    def _forge_shadow_cctx_proxy(self, key: str, value: Any) -> ContextProxy:
        tmp_cctx = copy.deepcopy(self._cctx)
        setattr(tmp_cctx, key, value)
        tmp_cctx_proxy = ContextProxy(tmp_cctx, self._validators)
        tmp_cctx_proxy._completed_fields = self._completed_fields.copy()
        if value == None:
            tmp_cctx_proxy._completed_fields.discard(key)
        else:
            tmp_cctx_proxy._completed_fields.add(key)            
        tmp_cctx.internal_supports['check_cctx_completeness'] = False

        return tmp_cctx_proxy

    def _bootstrap_validators(self, pbar: Optional[tqdm] = None) -> None:
        if self._validators:
            try:    
                self._validators[0].check(self, pbar)
            except CCTXValidationError as e:
                self._completed_fields.discard(e.wrong_field)
                raise

    def field_is_set(self, key: str) -> bool:
        return key in self._completed_fields

    ##
    # Setting value = None ContextProxy::update acts as a remove method
    ##
    def update(self, key: str, value: Any) -> bool:
        status = True

        if key in self._cctx.internal_supports:
            self._cctx.internal_supports[key] = value
        elif hasattr(self._cctx, key):
            tmp_cctx_proxy = self._forge_shadow_cctx_proxy(key, value)
            tmp_cctx_proxy._bootstrap_validators()
            setattr(self._cctx, key, value)
            if value == None:
                self._completed_fields.discard(key)
            else:
                self._completed_fields.add(key)
        else:
            self._temp_developer_log(f'ContextProxy::update could not find any campaign field with key: {key}.')
            status = False

        return status
    
    def remove(self, key: str) -> bool:
        return self.update(key, None)

    def select(self, key: str) -> Any:
        obj = None

        if key in self._cctx.internal_supports:
            obj = self._cctx.internal_supports[key]
        elif hasattr(self._cctx, key) and self.field_is_set(key):
            obj = getattr(self._cctx, key)
        else:
            self._temp_developer_log(f'ContextProxy::select could not find any campaign field with key: {key}.')
            pass

        return copy.deepcopy(obj)
    
    def subscribe(self, v: Validator) -> None:
        if isinstance(v, Validator):
            self._validators.append(v)
            self._chain_validators()

    def validate(self) -> None:
        logger.info('Checking campaign context validity...')
        self._cctx.internal_supports['check_cctx_completeness'] = True

        print()
        with tqdm(
            total=len(self._validators), 
            bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}",
            ncols=60,
            ascii=".#",
            colour="#b2b2b2"
        ) as pbar:
            self._bootstrap_validators(pbar)
        print()

        self._cctx.internal_supports['check_cctx_completeness'] = False
        return

    def dump(self) -> Path | None:
        if not self.field_is_set('mist_dir'):
            return None
        
        cctx_file: Path = self.select('mist_dir') / 'campaign_context.json'
        serialized_cctx = self._cctx.to_json()

        if cctx_file.exists():
            os.chmod(cctx_file, 0o644)

        with open(cctx_file, 'w') as f:
            f.write(serialized_cctx)

        logger.info('Successfully dumped campaign context to file.')
        logger.info(f'Path: {cctx_file}')
        return cctx_file
    
    def consume(self, filename: Path) -> None:
        logger.info('Loading campaign context from file...')
        self._completed_fields = self._cctx.from_json(filename)
        os.chmod(filename, 0o444)
        logger.info(f"Successfully loaded '{self.select('name')}' campaign context from file.")
        self.validate()
        return