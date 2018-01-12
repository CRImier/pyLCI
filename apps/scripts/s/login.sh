#!/bin/bash

set -euo pipefail

USERNAME="username"
PASSWORD="password"
WEBPAGE="rbt2.wifi.cs.rtu.lv/rtu_web.html"

curl $WEBPAGE -Lv --data "username=$USERNAME&key=$PASSWORD&fname=wba_login"
exit $?
