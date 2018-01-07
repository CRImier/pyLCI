import logging

import pydbus

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class OfonoBridge(object):
    """
    Generic util class to bridge between ZPUI and ofono backend through D-Bus
    """

    def __init__(self):
        super(OfonoBridge, self).__init__()
        self.ofono_bus = pydbus.SystemBus().get('org.ofono', '/')
