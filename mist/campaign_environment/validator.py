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
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from tqdm import tqdm

if TYPE_CHECKING:
    from .context_proxy import ContextProxy
from mist.utils.errors import CCTXValidationError

class Validator(ABC):
    def __init__(self, field_name: str):
        self._next: Optional[Validator] = None
        self._field = field_name

    def set_next(self, next: Validator) -> None:
        self._next = next
    
    def next(self, cctx: ContextProxy, pbar: Optional[tqdm] = None) -> None:
        if self._next is not None:
            self._next.check(cctx, pbar)
        
    def check(self, cctx: ContextProxy, pbar: Optional[tqdm] = None) -> None:
        full_check = cctx.select('check_cctx_completeness')
        field_is_set = cctx.field_is_set(self._field)
        if pbar:
            pbar.update(1)

        if full_check:
            if not field_is_set:
                raise CCTXValidationError(
                    f'Missing {self._field} field.',
                    self._field
                )
            self.validate_field(cctx)
        elif field_is_set:
            self.validate_field(cctx)
       
        self.next(cctx, pbar)

    @abstractmethod
    def validate_field(self, cctx: ContextProxy) -> None:
        pass