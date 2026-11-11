#!/bin/bash
# Usage: port/map/decompile.sh <ghidra program name> <hex rva>...
# Decompiles the functions containing each RVA into $FM27_WORK_DIR/decomp/ (local only; see port/map/workdir.py).
set -e
W="${FM27_WORK_DIR:-$HOME/fm27-port-work}"
export JAVA_HOME=$(ls -d $W/tools/jdk-25*/Contents/Home)
S="$(cd "$(dirname "$0")/../ghidra_scripts" && pwd)"
prog=$1; shift
list=$(mktemp); printf '%s\n' "$@" > "$list"
rm -f $W/ghidra/fm27.lock $W/ghidra/fm27.lock~
GHIDRA_HEADLESS_MAXMEM=11G $W/tools/ghidra_12.2_PUBLIC/support/analyzeHeadless $W/ghidra fm27 -process "$prog" \
  -noanalysis -readOnly -scriptPath "$S" -postScript DecompileFunctions.java "$list" $W/decomp 2>&1 | grep -E 'DECOMP|ERROR' || true
rm -f "$list"
