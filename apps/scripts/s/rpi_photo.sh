#!/bin/bash

set -euo pipefail

DATE=$(date +"%Y-%m-%d_%H%M%S")
raspistill -o /root/photos/image_$DATE.jpg -hf -vf -n -t 30
exit $?
