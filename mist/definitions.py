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
import shutil

MIST_ROOT_DIR = Path(__file__).expanduser().resolve().parent.parent

IS_DOCKER_CONTAINER = Path('/.dockerenv').exists()

# FUTURE support user custom terminal emulator
SUPPORTED_TERMINAL_EMULATORS = {
    'gnome-terminal': ['--geometry=80x25', '--'],
    'konsole': ['--geometry', '80x25', '-e'],
    'xfce4-terminal': ['--geometry=80x25', '--command'],
    'xterminal': ['-geometry', '80x25', '-e']
}

U_TERMINAL_EMULATOR = next(
    (Path(shutil.which(term)) for term in SUPPORTED_TERMINAL_EMULATORS if shutil.which(term)),
    None
)