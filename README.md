<p align="center">
  <img src="logo.png" alt="MIST logo" width="230">
</p>

<div align="center">Mist Instruments Sast Targets. A tool providing efficient Hybrid Application Security Testing (HAST).</div>
<br>
<br>

<strong>Smoothly transform static analysis findings into fuzzing campaigns.</strong>
<br>
MIST orchestrates the vulnerability analysis workflow, standardizing and automating the steps linking SAST and DAST, so that you can focus on security reasoning while it takes care of the analysis pipeline.
<br>
<br>
<div align="right">
    <strong>Designed to remain comparatively lightweight while maintaining competitive efficiency.</strong>
    <br> 
    MIST leverages technologies that can achieve results comparable to state-of-the-art <> approaches such as Symbolic Execution (SE) and semantic code analysis, maintaining considerably lower time and computational complexities.
</div>
<br>

<strong>For developers.</strong>
<br>
MIST can be employed as a modular, extensible and intuitive framework, to create new plugins and standalone tools.
The whole project is realeased under the Apache License 2.0, and its source code is freely available to inspect, study, modify, extend, and build upon, encouraging experimentation and further development.

<br>
<br>
<div align="center">
    <i>"Given enough eyeballs, all bugs are shallow"</i>
</div>
<br>

## Get Started

Clone and enter the repository:

```bash
git clone https://github.com/alessandroPalazzolo/mist.git
cd mist
```

#### MIST can run both as a local installation or in a Docker container.

- The local installation supports all features and is recommended for more in-depth and advanced use. However, when dealing with fuzz testing, some operations may directly affect the host system, so additional care is required.<br>
Some additional tweaking might be required based on your system configuration.

- The containerized version provides complete isolation from the host system, making it the safest option while providing a ready-to-use environment. Nonetheless, as documented in the relevant section, some features may be limited or behave differently due to Docker's isolation mechanisms. Docker is therefore recommended for testing MIST or trying it for the first time.

Below are the steps required for the **local installation**. See the [Docker](#run-mist-with-docker) section to run MIST in a container.

### MIST

Create and activate a virtual environment (unless you want a global install):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the python3 `mist` wheel with dependencies:

```bash
pip install -e .
```

### AFLGo

Mist leverages AFLGo directed greybox fuzzer for DAST. See more at https://github.com/aflgo/aflgo.

**Warning:** AFLGo build script will attempt to apply modifications on your host system, potentially affecting your existing compiler toolchain. The AFLGo [documentation](AFLGo/Readme.md) explains each action taken in depth, still, if you don't feel confident with it you might want to check the Docker [installation](#run-mist-with-docker).  

Build the fuzzer:

```bash
cd AFLGo
sudo ./build.sh
cd ..
```

You ideally only need this to make AFLGo work. If you encounter any issue refer to the official [documentation](AFLGo/Readme.md) for better support.

**Warning:** MIST only works with a slightly modified version of AFLGo, see more at [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md). For this reason you can provide a custom AFLGo version, but should only apply your edits on the one shipping with MIST.

### Semgrep

**Optional:** if you don't wish to use a global custom Semgrep installation you can skip this step!

MIST employs Semgrep capabilities for efficient SAST. See more at https://docs.semgrep.dev.  

Semgrep conveniently exposes a python package that can be installed with `pip install semgrep`, for this reason it is already included as a `mist` wheel dependency and should be locally installed.

If you wish to use a global `semgrep` installation you need to run:

```bash
pipx install semgrep
```
then proceed to edit your `$PATH` accordingly, so that `mist` sees it first.

### Finally...

You can now start exploring MIST by simply typing:
```bash
mist
```

## Run MIST with Docker

Seamlessly build and run MIST using Docker Compose.

Assuming that you are in the `mist/` root directory, run:

```bash
LOCAL_WORKSPACE=<path-to-your-workspace> docker compose run --rm mist 
```

Replace `<path-to-your-workspace>` with the path to the directory containing the systems you want to test (SUTs), this will bind it to the container.

If it's the first time you run it, Docker Compose will pull and build all the required assets (this might take a few minutes). After that, it will automatically start the container with `mist` running inside of it. You can use again the same command every time you want to start MIST.

**Warning:** Some MIST features may be limited or behave differently in Docker.

* **High performance fuzzing:** MIST optionally leverages the [afl-system-config](AFLGo/afl-2.57b/afl-system-config) script to reconfigure the host system to a high performance fuzzing state. The script requires elevated privileges and performs host-level system configurations, making it not suitable for a Docker container environment.

* **Split view of AFLGo and MIST Monitor UIs:** during fuzz time, by default, MIST launches [afl-fuzz](AFLGo/afl-2.57b/afl-fuzz.c) in a separate terminal window to provide its interactive UI alongside the MIST Monitor one. This functionality is not supported in Docker containers, resulting in a less informative runtime that can only show MIST relevant metrics.<br>
If you wish to get more insights on the fuzzer runtime you can access the `/<path-to-SUT>/obj-aflgo/out/fuzzer_stats` local file, with SUT being your current system under test.

## Test your MIST installation

Once installed, you can check if your MIST instance correctly works by testing it on a simple default SUT.

The SUT is provided in the [test-system](test-system) directory. Inside you'll find additional [documentation](test-system/README.md) on how to proceed.

Start your MIST instance and set your SUT to `./test-system`. The wizard will then guide you through the next steps.

## Contents

- `AFLGo/` is the aflgo source directory.
- `mist/` is the MIST source directory.
- `test-system/` contains the default system for testing MIST.
- `testcases/` contains a multitude of file samples used for fuzzing.
- `.gitignore`
- `Dockerfile` is the Docker configuration file for running MIST in a container.
- `LICENSE.txt` is the Apache 2.0 license file.
- `README.md`
- `THIRD_PARTY_NOTICES.md` keeps a log of included third-party packages with their related MIST modifications.
- `compose.yaml` is the Docker compose configuration file.
- `pyproject.toml` is the python configuration file used to install MIST sources.
- `logo.png` is MIST logo.

## License

Copyright © 2026 Alessandro Palazzolo.

MIST is distributed under the [Apache License 2.0](LICENSE.txt).
