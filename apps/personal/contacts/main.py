import argparse
import logging
import pickle
import os
import vobject

ZPUI_HOME = "~/.zpui/"
SAVE_FILENAME = "contacts.pickle"


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class AddressBook(Singleton):
    def __init__(self):
        # todo : encrypt ?
        self._contacts = []
        self.load_from_file()

    @property
    def contacts(self):
        # type: () -> list
        return self._contacts

    def add_contact(self, contact, auto_merge=False):
        pass  # todo : remove

    def load_from_file(self):
        self._contacts = pickle.load(self.get_save_file_path())

    def save_to_file(self):
        pickle.dump(self._contacts, self.get_save_file_path())

    @staticmethod
    def get_save_file_path():
        return os.path.join(os.path.expanduser(ZPUI_HOME), SAVE_FILENAME)


class Contact(object):
    def __init__(self):
        self.name = []
        self.name = []
        self.address = []
        self.telephone = []
        self.email = []
        self.url = []
        self.note = []
        self.org = []
        self.photo = []
        self.title = []


class VCardContactConverter(object):
    vcard_mapping = {
        'fn': 'name',
        'n': 'name',
        'adr': 'address',
        'tel': 'telephone',
        'email': 'email',
        'url': 'url',
        'note': 'note',
        'org': 'org',
        'photo': 'photo',
        'title': 'title'
    }

    @staticmethod
    def to_zpui_contact(v_contact):
        # type: (vobject.base.Component) -> Contact
        contact = Contact()
        for key in v_contact.contents.keys():
            if key not in VCardContactConverter.vcard_mapping: continue
            attr = getattr(contact, VCardContactConverter.vcard_mapping[key])
            assert type(attr) == list
            attr += [v.value for v in v_contact.contents[key]]
        return contact

    @staticmethod
    def parse_vcard_file(file_path):
        # type: (str) -> list
        file_content = VCardContactConverter.read_file_content(file_path)
        contacts = [c for c in vobject.readComponents(file_content, ignoreUnreadable=True)]
        logging.info("Found {} contact in file {}", len(contacts), file_path)
        return contacts

    @staticmethod
    def read_file_content(file_path):
        with open(file_path, 'r') as f:
            file_content = f.read()
            return file_content

    @staticmethod
    def from_vcards(contact_card_files):
        # type: (list) -> list
        contacts = []
        for file_path in contact_card_files:
            contacts += VCardContactConverter.parse_vcard_file(file_path)
        logging.info("finished : {} contacts loaded", len(contacts))
        return [VCardContactConverter.to_zpui_contact(c) for c in contacts]


def find_contact_files(folder):
    # type: (str) -> list(str)
    home = os.path.expanduser(folder)
    if not os.path.exists(home):
        os.mkdir(home)
    contact_card_files = [os.path.join(home, f) for f in os.listdir(home) if f.lower().endswith("vcf")]
    return contact_card_files


def load_vcf(folder):
    # type: (str) -> None
    contact_card_files = find_contact_files(folder)
    contacts = VCardContactConverter.from_vcards(contact_card_files)

    address_book = AddressBook()
    for contact in contacts:
        address_book.add_contact(contact)
    address_book.save_to_file()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--src-folder', dest='src_folder', action='store', metavar="DIR",
                        help='Folder to read vcard from')
    arguments = parser.parse_args()

    load_vcf(arguments.src_folder)
