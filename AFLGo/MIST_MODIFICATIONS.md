# AFLGo modifications for MIST

MIST includes a modified version of AFLGo.

Original project:
https://github.com/aflgo/aflgo

## Modifications

- `afl-fuzz.c`: lightly modified queue and crashes entries naming conventions and input distance management.

- `afl-system-config`: newfile added from AFL++. Source: https://github.com/AFLplusplus/AFLplusplus

These modifications are required for integration with MIST. Each modification is delimited by comments: "custom mist START" and "custom mist END".