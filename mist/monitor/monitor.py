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
import time
from datetime import timedelta
from threading import Thread, Lock, Event
from queue import Queue
from pathlib import Path
import subprocess
import psutil
import os
from typing import Dict, List, Deque, Optional
import logging
import re
import shutil
import uuid
from collections import deque
from sparklines import sparklines

from mist.campaign_environment import ContextProxy
from mist.utils.logging_manager import LoggingManager
from mist.utils.errors import MonitorError
from mist.definitions import SUPPORTED_TERMINAL_EMULATORS, IS_DOCKER_CONTAINER

CMP_ACC_TIME = 0
SES_START_TIME = 1
##
# AFLGO fuzzer sets -1 as null distance value 
# If the current input has a non-positive count of exercised BBs, it will have distance = -1 
##
NULL_DIST = -1.

logger = logging.getLogger(__name__)

class Monitor():
    def __init__(self, cctx: ContextProxy):
        self._cctx = cctx
        self.target_crashes_dir: Path | None = None
        self.mist_pipe: Path = '/tmp/mist_pipe'
        self.pending: Queue[Path] = Queue(1000)
        self.next_queue_id = 1
        self.processed = 0
        self.distances = [NULL_DIST,NULL_DIST,NULL_DIST] # cur distance, min distance, max distance
        self.distance_history: Deque[float] = deque(maxlen=10)
        self.target_crashes = 0
        self.times = [0.,0.] # campaign accumulated time, session start time
        self.fuzzer_proc: Optional[psutil.Process] = None
        self._lock = Lock()
        self._stop = Event()

    def _resume_prev_results(self, log_file: Path) -> None:
        logger.info('Resuming previous campaign results...')            

        queue_id_pattern = re.compile(r"next-queue-id:\s+(\d+)")
        processed_pattern = re.compile(r"processed:\s+(\d+)")
        mindist_pattern = re.compile(r"min_distance:\s+(-1|\d+\.\d+)")
        maxdist_pattern = re.compile(r"max_distance:\s+(-1|\d+\.\d+)")
        crashes_pattern = re.compile(r"target-crashes:\s+(\d+)") 
        time_pattern = re.compile(r"time:\s+(\d+\.\d+)")

        with open(log_file, "r") as f:
            lines = f.readlines()
            next_queue_id_line = lines[-7]
            processed_line = lines[-6]
            mindist_line = lines[-5]
            maxdist_line = lines[-4]
            crashes_line = lines[-3]
            time_line = lines[-2]
            # line[-1] is 'Resuming previous campaign results...'

        try:
            nxt_queue_id = int(queue_id_pattern.search(next_queue_id_line).group(1))
            nprocessed = int(processed_pattern.search(processed_line).group(1))
            mindist = float(mindist_pattern.search(mindist_line).group(1))
            maxdist = float(maxdist_pattern.search(maxdist_line).group(1))
            ncrashes = int(crashes_pattern.search(crashes_line).group(1))
            acc_time = float(time_pattern.search(time_line).group(1))
        except AttributeError as e:
            logger.info('Could not resume.')
            return

        self.next_queue_id = nxt_queue_id
        self.processed = nprocessed
        self.distances[1] = mindist
        self.distances[2] = maxdist
        self.target_crashes = ncrashes
        self.times[CMP_ACC_TIME] = acc_time

        logger.info('Done.')

    def _render_ui(self, times: List[float]) -> None:
        with self._lock:
            nprocessed = self.processed
            ncrashes = self.target_crashes
            dist = self.distances

        graph = "".join(sparklines(numbers=self.distance_history, minimum=dist[1], maximum=dist[2]))
        elapsed_time = timedelta(seconds=int(times[CMP_ACC_TIME] + (time.time() - times[SES_START_TIME])))

        COLOR = "\033[1;38;2;162;115;76m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        sys.stdout.write(
            f"\r{COLOR}[{RESET}{BOLD} Mist Monitor {BOLD}{COLOR}]{RESET} "
            f"fuzz time: {elapsed_time} {COLOR}|{RESET} "
            f"processed: {nprocessed} {COLOR}|{RESET} "
            f"distance: {graph} {dist[0]} [ {dist[1]} ][ {dist[2]} ] {COLOR}|{RESET} "
            f"target crashes: {ncrashes} "
        )
        sys.stdout.flush()

    def _ui_loop(self) -> None:
        print()

        while not self._stop.is_set():
            self._render_ui(self.times)
            time.sleep(0.2)
    
    ##
    # Monitor::_has_target() checks for crashes that happen in a range of ±5 lines around specified targets
    # if we count the ±1 range applied on Mist Wizard targets (see SemgrepParsing::_findings_to_targets())
    # total range of target related crash detection amounts to t±6 
    # + detects target related crashes happening around it due to evaluation order
    # + detects target related crashes but happening around it due to compilers's optimization ops
    # + save crash line to target distance for more detailed fuzzing campaign metrics
    ##
    def _has_target(self, st_line: str, targets: List[str]) -> bool:
        CRASH_TO_TARGET_RANGE = 5
        status = False

        for t in targets:
            filename, line = t.rsplit(":", 1)
            line = int(line)

            match = re.search(
                rf"{re.escape(filename)}:(\d+)",
                st_line
            )

            if match:
                crash_line = int(match.group(1))

                if abs(crash_line - line) <= CRASH_TO_TARGET_RANGE:
                    status = True
                    break

        return status

    def _check_test(self, harness_file: Path, harness_args: List[str], test_file: Path, env: Dict[str, str]) -> None:       
        input_src =  self._cctx.select('harness_input_src')

        match input_src:
            case 'stdin':
                stdin = open(test_file, "rb")
            case 'file':
                harness_args = [str(test_file) if arg == '@@' else arg for arg in harness_args]
                stdin = subprocess.DEVNULL  # prevents interactive blocking
            case _:
                raise MonitorError('Wrong harness input source.')
                
        logger.info(f'Checking testcase {test_file.parent}/{test_file.name} ...')

        try:
            result = subprocess.run(
                [str(harness_file), *harness_args],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=stdin,
                text=True,
                errors='ignore',
                timeout=2
            )
        except subprocess.TimeoutExpired as e:
            # FUTURE check timeouts too for target lines
            logger.warning(f'[TIMEOUT] {test_file}')
            return

        targets = self._cctx.select('targets_list')

        with self._lock:
            self.processed += 1
            if result.returncode != 0:
                lines = result.stderr.splitlines()
                for line in lines:
                    if self._has_target(line, targets):
                        logger.warning(f"[CRASH] {test_file}")
                        logger.info(line)
                        self.target_crashes += 1
                        dst: Path = self.target_crashes_dir / f"{uuid.uuid4().hex}_{test_file.parent.name}_{test_file.name}_mist:{self.target_crashes}"
                        shutil.copy(test_file, dst)
                        logger.info(f'Testcase saved to {self.target_crashes_dir}')
                        break

    def _poll_queue(self) -> None:
        queue_dir: Path = self._cctx.select('fuzzer_dir') / 'out' / 'queue'

        while not self._stop.is_set():
            fname = f"id:{self.next_queue_id:06d}"
            fpath: Path = queue_dir / fname

            if fpath.exists():
                self.pending.put(fpath)
                self.next_queue_id += 1

            time.sleep(0.1)

    def _poll_crashes(self) -> None:
        crashes_dir: Path = self._cctx.select('fuzzer_dir') / 'out' / 'crashes'
        next_id = 0

        while not self._stop.is_set():
            fname = f"id:{next_id:06d}"
            fpath: Path = crashes_dir / fname

            if fpath.exists():
                self.pending.put(fpath)
                next_id += 1

            time.sleep(0.1)

    def _process_pending(self) -> None:
        harness_file: Path = self._cctx.select('checker_harness_file')
        harness_args = self._cctx.select('harness_args')
        env = os.environ.copy()
        env['ASAN_OPTIONS'] = 'detect_leaks=0'

        while not self._stop.is_set():
            fpath = self.pending.get()
            self._check_test(harness_file, harness_args, fpath, env)
            logger.info('Done')

    def _poll_stats(self) -> None:
        stats_file: Path = self._cctx.select('fuzzer_dir') / 'out' / 'fuzzer_stats'
        curdist = NULL_DIST
        mindist = NULL_DIST
        maxdist = NULL_DIST
        dist_c = 0

        while not self._stop.is_set():
            try:
                with open(stats_file) as f:
                    for line in f:
                        if line.startswith("cur_distance"):
                            curdist = float(line.split(":", 1)[1].strip())
                        elif line.startswith("min_distance"):
                            mindist = float(line.split(":", 1)[1].strip())
                        elif line.startswith("max_distance"):
                            maxdist = float(line.split(":", 1)[1].strip())
            except FileNotFoundError:
                logger.info(f'{stats_file} does not exist.')
                pass

            with self._lock:
                self.distances[0] = curdist
                if curdist != NULL_DIST:
                    self.distance_history.append(curdist)
                    dist_c += 1
                if dist_c == 10:
                    d = " ".join(map(str, self.distance_history))
                    logger.info(f'distance history (10): {d}')
                    dist_c = 0
                if (self.distances[1] == NULL_DIST or (( mindist < self.distances[1] ) and ( mindist != NULL_DIST ))):
                    self.distances[1] = mindist
                if (self.distances[2] == NULL_DIST or (( maxdist > self.distances[2] ) and ( maxdist != NULL_DIST ))):
                    self.distances[2] = maxdist

            time.sleep(60)

    def _poll_fuzzer_status(self) -> None:
        while not self._stop.is_set():
            if not self.fuzzer_proc.is_running():
                self._stop.set()
                return

            time.sleep(1)
    
    def _observe(self) -> None:
        queue_dir: Path = self._cctx.select('fuzzer_dir') / 'out' / 'queue'

        logger.info("Waiting for queue directory...")

        while not queue_dir.exists():
            time.sleep(1)

        logger.info(f"Start monitoring queue: {queue_dir}")

        # [ producer 1 ]
        Thread(target=self._poll_queue, daemon=True).start()
        # [ producer 2 ]
        Thread(target=self._poll_crashes, daemon=True).start()
        # [ consumer ]
        Thread(target=self._process_pending, daemon=True).start()
        # [ stats ]
        Thread(target=self._poll_stats, daemon=True).start()
        # [ fuzzer status ]
        Thread(target=self._poll_fuzzer_status, daemon=True).start()        
        # [ ui ]
        Thread(target=self._ui_loop, daemon=True).start()

        while not self._stop.is_set():
            time.sleep(1)

        raise KeyboardInterrupt
    
    def _start_fuzzer(self) -> None:
        script: Path = self._cctx.select('fuzzer_exec_script_file')
        harness_file: Path = self._cctx.select('harness_file')
        term_em: Path | None = self._cctx.select('terminal_emulator')  

        # FUTURE support aflgo GUI in new terminal window for docker mist
        if IS_DOCKER_CONTAINER:
            subprocess.Popen(
                [str(script)], 
                stderr=subprocess.DEVNULL, 
                stdout=subprocess.DEVNULL, 
                stdin=subprocess.DEVNULL, 
                env={**os.environ, "AFL_NO_UI": "1"}
            )
        else:
            if term_em is None:
                raise MonitorError(f'No supported terminal emulator found. Tried: {", ".join(SUPPORTED_TERMINAL_EMULATORS)}.') 
            
            subprocess.Popen([
                    str(term_em),
                    *SUPPORTED_TERMINAL_EMULATORS[term_em.name], # terminal emulator options
                    str(script)
                ]
            )

        time.sleep(1) # wait for afl-fuzz to start

        for p in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'afl-fuzz' in p.info['name'] and str(harness_file) in p.info['cmdline']:
                self.fuzzer_proc = p
                break

        if self.fuzzer_proc is None:
            raise MonitorError('Could not start the afl-fuzz process.')  

    def spawn(self) -> None:
        subject_dir: Path = self._cctx.select('subject_dir')
        self.target_crashes_dir = subject_dir / 'target_crashes'
        seeds_dir: Path = self._cctx.select('seeds_dir')
        mist_dir: Path = self._cctx.select('mist_dir')
        log_file: Path = mist_dir / 'monitor.log'
        logmgr: LoggingManager = self._cctx.select('logging_manager')
        logmgr.use_file(log_file)

        self.target_crashes_dir.mkdir(exist_ok=True)
        try:
            os.mkfifo(self.mist_pipe, 0o600)
        except FileExistsError:
            pass 

        if str(seeds_dir) == '-':
            self._resume_prev_results(log_file)
        else:
            self.next_queue_id = sum(1 for _ in seeds_dir.iterdir())

        try:
            logger.info('Starting fuzzer...')
            self._start_fuzzer()
            self.times[SES_START_TIME] = time.time()
            logger.info('Starting observer...')
            self._observe()
        except (Exception, KeyboardInterrupt) as e:
            logger.info('Exiting...')
            self._stop.set()
            time.sleep(0.2) # Wait for threads to exit
            logger.info(f'next-queue-id: {self.next_queue_id}')
            logger.info(f'processed: {self.processed}')
            logger.info(f'min_distance: {self.distances[1]}')
            logger.info(f'max_distance: {self.distances[2]}')
            logger.info(f'target-crashes: {self.target_crashes}')
            logger.info(f'time: {self.times[CMP_ACC_TIME]+(time.time()-self.times[SES_START_TIME])}')

            if self.fuzzer_proc.is_running():
                self.fuzzer_proc.terminate() # SIGTERM
                try:
                    self.fuzzer_proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.fuzzer_proc.kill() # SIGKILL

            logmgr: LoggingManager = self._cctx.select('logging_manager')
            mist_log_file: Path = self._cctx.select('mist_dir') / 'mist.log'
            logmgr.use_console_and_file(mist_log_file)
            print()
            raise