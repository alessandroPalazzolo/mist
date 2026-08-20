# MIST

Mist Instruments Sast Targets. A tool providing efficient Hybrid Application Security Testing (HAST).

#### Smoothly transform static analysis findings into fuzzing campaigns.
MIST orchestrates the vulnerability analysis workflow, standardizing and automating the steps linking SAST and DAST, so that you can focus on security reasoning while it takes care of the analysis pipeline.

#### Designed to remain comparatively lightweight while maintaining competitive efficiency. 
MIST leverages technologies that can achieve results comparable to state-of-the-art approaches such as Symbolic Execution (SE) and semantic code analysis, maintaining considerably lower time and computational complexities.

#### For developers.
MIST can be employed as a modular, extensible and intuitive framework, to create new plugins and standalone tools.
The whole project is realeased under the Apache License 2.0, and its source code is freely available to inspect, study, modify, extend, and build upon, encouraging experimentation and further development.

<br>
<i>"Given enough eyeballs, all bugs are shallow"</i>

<br>

## Get Started

Clone and enter the repository:
```bash
git clone https://github.com/alessandroPalazzolo/mist.git
cd mist
```
Before running you need to set the right environment and build its components.

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

Build the fuzzer:

```bash
cd AFLGo
sudo ./build.sh
cd ..
```

You ideally only need this to make AFLGo work. If you encounter any issue refer to the official [documentation](AFLGo/Readme.md) for better support.

**Warning:** MIST only works with a slightly modified version of AFLGo, see more at [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md). For this reason you can provide a custom AFLGo version, but you should only edit the one shipping with MIST.

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

## License

Copyright © 2026 Alessandro Palazzolo.

MIST is distributed under the [Apache License 2.0](LICENSE.txt).