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

from abc import ABC, abstractmethod
from rich.console import Console
from rich.text import Text 

from mist.campaign_environment import ContextProxy

class WizardStep(ABC):
    def __init__(self, title: str):
        self.title = title

    @abstractmethod
    def run(self, cctx: ContextProxy) -> None:
        pass

    @abstractmethod
    def should_run(self, cctx: ContextProxy) -> bool:
        pass

    def print_header(self) -> None:
        console = Console()
        title = Text(f" {self.title} ", style="bold #DDEEFF on #4D4D4D")
        console.print()
        console.print()
        console.print(title)
        console.print()