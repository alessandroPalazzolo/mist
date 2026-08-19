# AFLGo modifications for Mist

Mist includes a modified version of AFLGo.

Original project:
https://github.com/aflgo/aflgo

## Modifications

- `afl-fuzz.c`: Lightly modified queue and crashes entries naming conventions and input distance management.

These modifications are required for integration with Mist. Each modification is delimited by comments: "custom mist START" and "custom mist END".