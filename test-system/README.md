# A simple application to test MIST

This directory contains a single-file C application that can be used to check if MIST is working after installation, or for generic testing.

The file `test.c` contains an obvious Buffer Overflow vulnerability at line 11. That code location should trigger `semgrep` scanner and be used as a target for the AFLGo fuzzer.

After selecting `test-system` to be your System Under Test (SUT), MIST will prompt you for configurations step by step. Below, if needed, are the default answers you should provide to some of the prompts for a quick test:

<br>

| MIST prompt | User answer | Comment |
|---|---|---|
| Use a custom AFLGo build: | default | |
| Already have file with findings? | No | This will trigger `semgrep scan`. |
| Select results: | test.c:11 | After the scan it should appear among findings, select with spacebar and press `Enter`. If there are no findings you can press `Enter` and follow the wizard to define the target manually. |
| Enter preparation commands to set up the build system: | empty | Delete the default commands proposed by MIST, press `Esc` and press `Enter`. |
| Enter the SUT build commands: | $CC $ADDITIONAL ../test.c -o test | Press `Esc` and then `Enter` to send the answer. |
| Want to provide a seeds directory? | No | Mind that default is set to Yes. |
| Path to harness file | /default/test | Complete the default path shown by appending `/test` to it. |
| Select the harness input source: | stdin |  |
| Enter args/flags for harness: | empty ||
| * Apply custom system config for fuzzing performance: | default (No) | You'll see this step only on local installations. Not supported on Docker containers. |
|  |||

<br>

**Info:** when User answer is set to `default` it means you should select the default answer proposed by MIST by simply pressing `Enter`.

Eventually MIST should render its own Monitor metrics and, if running on a local installation, the AFLGo UI in a separate terminal window. This means you are running correctly and ready to experiment!
