#!/bin/bash
# Rebuild one species from its generator (tools/models/species/<sid>.py) into the mod resources.
# Usage (from tools/models): bash iter.sh <sid>      (Monster Hunter: python3 -I build_mh.py . <species> ../../src/main/resources tmp)
set -e
cd "$(dirname "$0")"
python3 -I build_model.py . "$1" ../../src/main/resources tmp
