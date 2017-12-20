import logging

import pydbus

from apps.personal.contacts.address_book import AddressBook
from apps.personal.contacts.vcard_converter import VCardContactConverter

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class OfonoBridge(object):
    """
    Generic util class to bridge between ZPUI and ofono backend through D-Bus
    """

    def __init__(self):
        super(OfonoBridge, self).__init__()
        self.ofono_bus = pydbus.SystemBus().get('org.ofono', '/')  # todo : trycatch

    def get_sim_contacts(self):
        # type: () -> list
        # returns the contacts list stored on the default sim-card
        vcard_string = self.ofono_bus['Phonebook'].Import(timeout=100)  # todo : test this
        return VCardContactConverter.from_string(vcard_string)

    def import_sim_phonebook(self):
        address_book = AddressBook()
        for contact in self.get_sim_contacts():
            address_book.add_contact(contact)
        address_book.save_to_file()
