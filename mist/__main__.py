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

import sys
import traceback
import logging

from mist.wizard import Wizard
from mist.wizard.wizard_steps import *
from mist.campaign_environment import ContextProxy
from mist.campaign_environment.contexts.aflgo_campaign_context import AFLGoCampaignContext
from mist.monitor import Monitor
from mist.utils.errors import MonitorError
from mist.campaign_environment.validators import *

logger = logging.getLogger(__name__)

cctx_validators = [
    SubjectDirV(),
    MistDirV(),
    AFLGoDirV(),
    WorkDirV(),
    FuzzerDirV(),
    CheckerDirV(),
    FindingsFileV(),
    TargetsFileV(),
    TargetsListV(),
    BuildPrepCmdV(),
    BuildCmdV(),
    AFLGoAnalysisScriptFileV(),
    CheckerBuildScriptFileV(),
    SeedsDirV(),
    SeedsOptimizationsV(),
    HarnessFileV(),
    CheckerHarnessFileV(),
    HarnessInputSrcV(),
    HarnessArgsV(),
    FuzzerEnhancedPerfV(),
    FuzzerExecScriptFileV(),
    AFLGoInstrumentationScriptFileV()
]

def print_banner():
    banner = r"""
 • ▌ ▄ ·. ▪  .▄▄ · ▄▄▄▄▄
 ·██ ▐███▪██ ▐█ ▀. •██  
 ▐█ ▌▐▌▐█·▐█·▄▀▀▀█▄ ▐█.▪
 ██ ██▌▐█▌▐█▌▐█▄▪▐█ ▐█▌·
 ▀▀  █▪▀▀▀▀▀▀ ▀▀▀▀  ▀▀▀
"""
    gray = "\033[38;2;139;138;136m"
    reset = "\033[0m"

    print(banner)  
    print(gray + "[ MIST ] Instruments Sast Targets" + reset)
    print(gray + "[ AUTHOR ] A. Palazzolo")
    print(gray + "[ VERSION ] 0.1.0.dev0" + reset)
    print(gray + "[ SOURCE ] https://github.com/alessandroPalazzolo/mist" + reset)
    print(gray + "[ USAGE ] mist {options}" + reset)

def _run():
    print_banner()

    cctx_proxy = ContextProxy(AFLGoCampaignContext(),cctx_validators)
    wiz = Wizard(cctx_proxy, [
        CampaignSetup(), 
        SemgrepParsing(), 
        SUTBuildSetup(),
        AFLGoAnalysis(),
        SANCheckerBuild(),
        FuzzingSetup(),
        AFLGoInstrumentation()
    ])
    mon = Monitor(cctx_proxy)

    wiz.launch()
    mon.spawn()

def main():
    try:
        _run()
    except MonitorError as e:
        logger.error(e)
        sys.exit(1)
    except Exception as e:
        print(e)
        traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nBona!")
        sys.exit(0)
