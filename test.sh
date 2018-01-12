#!/bin/bash

set -euo pipefail

find ui/tests/ -maxdepth 1 -name '*.pyc' -delete

test -d ui/tests/__pycache__ && rm -rf ui/tests/__pycache__

python -B -m pytest --doctest-modules -v --doctest-ignore-import-errors --ignore=output/drivers --ignore=input/drivers --ignore=apps/hardware_apps/ --ignore=apps/example_apps/fire_detector --ignore=apps/test_hardware
