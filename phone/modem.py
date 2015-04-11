#!/usr/bin/env python
import gammu
import sys

def to_be_enabled(func):
    def wrapper(self, *args, **kwargs):
        if not self.enabled: #If modem is not enabled
            if not self.enable(): #Tries to enable the modem
                return (False, "modem_disabled") #If failed, returns failure code
        return func(self, *args, **kwargs) #If everything's okay, returns call result of a desired function
    return wrapper

class ModemInterface():
    enabled = False

    def __init__(self):
        self.sm = gammu.StateMachine()
        self.sm.ReadConfig(Filename = "/etc/gammurc")
        self.enable()

    @to_be_enabled
    def disable(self):
        self.enabled = False
        return True

    def enable(self):
        try:
            self.sm.Init()
        except gammu.ERR_DEVICENOTEXIST:
            self.enabled = False
        else:
            self.enabled = True
        finally:
            return self.enabled

    def can_be_enabled():
        return True

    @to_be_enabled
    def send_message(self, number, text):
        message = {
            'Text': text,
            'SMSC': {'Location': 1},
            'Number': number,
        }
        try:
            self.sm.SendSMS(message)
        except gammu.ERR_UNKNOWN as e:
            return False    
        except gammu.ERR_DEVICENOTEXIST as e:
            self.disable()
            return False    
        else:
            return True


if __name__ == "__main__":
    pass
