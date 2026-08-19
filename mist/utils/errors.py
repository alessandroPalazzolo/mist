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

class MistError(Exception):
    pass

class WizardStepError(MistError):
    def __init__(self, message: str, info: str = ''):
        super().__init__(message)
        self.info = info

class CCTXValidationError(MistError):
    def __init__(self, message: str, field: str): 
        super().__init__(message)
        self.wrong_field = field

class MonitorError(MistError):
    def __init__(self, message: str, info: str = ''):
        super().__init__(message)
        self.info = info
