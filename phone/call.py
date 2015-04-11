#!/usr/bin/env python

import gammu
import sys

sm = gammu.StateMachine()
sm.ReadConfig(Filename = "/etc/gammurc")
sm.Init()
sm.DialVoice('26700716')
