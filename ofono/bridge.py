import logging
import os
from time import sleep

import pydbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from helpers import Singleton, setup_logger

DBusGMainLoop(set_as_default=True)  # has to be called first

logger = setup_logger(__name__, 'debug')
logging.basicConfig(level=logging.DEBUG)


class OfonoBridge(object):
    """
    Generic util class to bridge between ZPUI and ofono backend through D-Bus
    """

    def __init__(self):
        super(OfonoBridge, self).__init__()

        bus = pydbus.SystemBus()
        manager = bus.get('org.ofono', '/')
        modem_path = manager.GetModems()[0][0]

        if modem_path != '/sim900_0':
            raise ValueError("Default modem should be '/sim900_0', was '{}'".format(modem_path))

        # self.start()  #todo: check if it's the suitable place to do it

    def start(self):
        self.power_on()
        self._init_messages()
        self._listen_messages()

    @property
    def _bus(self):
        # lil hack so we always have an up-to-date bus
        return pydbus.SystemBus().get('org.ofono', '/sim900_0')

    @property
    def message_manager(self):
        return self._get_dbus_interface('MessageManager')

    def _get_dbus_interface(self, name):
        ''.startswith('org.ofono')
        full_name = name if name.startswith('org.ofono') else 'org.ofono.{}'.format(name)
        if full_name in self._bus.GetProperties()['Interfaces']:
            return self._bus[full_name]

    def power_on(self):
        if self._bus.GetProperties()["Powered"]:
            logger.info("Modem already powered up !")
        else:
            logger.info("Powering up modem...")
            try:
                self._bus.SetProperty("Powered", pydbus.Variant('b', True))
                sleep(2)  # Let the modem some time to initialize
            except Exception:
                logger.error("Couldn't power up the modem !")

    def power_off(self):
        self._bus.SetProperty("Powered", pydbus.Variant('b', False))

    def send_sms(self, to, content):  # todo : untested
        self.message_manager.SendMessage(to, content)
        print("Sending", to, content)
        ConversationManager().on_new_message_sent(to, content)

    @staticmethod
    def on_message_received(message, details, path=None, interface=None):  # todo : untested
        logger.info("Got message with path {}".format(path))
        ConversationManager().on_new_message_received(message, details)

    def _listen_messages(self):
        logger.info("Connecting to dbus callbacks")
        self.message_manager.IncomingMessage.connect(self.on_message_received)
        self.message_manager.ImmediateMessage.connect(self.on_message_received)

    def _init_messages(self):
        self.message_manager.SetProperty("UseDeliveryReports", pydbus.Variant('b', True))


class ConversationManager(Singleton):
    """
    Singleton dedicated to conversations. Logs every message sent and received in a flat file
    for any given phone number
    """

    def __init__(self):
        super(ConversationManager, self).__init__()
        self.folder = os.path.expanduser("~/.phone/sms/")  # todo: store as a constant somewhere
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

    def on_new_message_sent(self, to, content):
        logger.info("Sent message to '{}'".format(to))
        self._write_log(to, self._format_log(content, from_me=True))

    def on_new_message_received(self, content, details):
        origin = details['Sender']
        logger.info("Received message from'{}'".format(origin))
        self._write_log(origin, self._format_log(content, from_me=True))

    def _write_log(self, phone_number, log):
        with open(self._get_log_path(phone_number), 'a+') as log_file:
            log_file.write(log)

    def _get_log_path(self, phone_number):
        file_name = "{}.txt".format(phone_number)
        return os.path.join(self.folder, file_name)

    @staticmethod
    def _format_log(content, from_me=True):
        start_char = '>' if from_me else '<'
        return "{prefix}\t{msg}\n".format(prefix=start_char, msg=content)


def main():
    ofono = OfonoBridge()
    ofono.start()
    mainloop = GLib.MainLoop()  # todo : own thread
    try:
        mainloop.run()
    except KeyboardInterrupt:
        # ofono.power_off()  # todo: can't be powered back up after we power it off once
        logger.info("Exiting...")


if __name__ == '__main__':
    main()
