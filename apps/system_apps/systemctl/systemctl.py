from helpers import setup_logger
from pydbus import SystemBus

from operator import itemgetter

logger = setup_logger(__name__, "warning")

# See D-Bus documentation here:
#     https://www.freedesktop.org/wiki/Software/systemd/dbus/

bus = SystemBus()
systemd = bus.get(".systemd1")

def list_units(unit_filter_field = None, unit_filter_values = []):
    units = []

    unit_params = ["name", "description", "load", "active", "sub", "follower", "unit_object_path", "job_queued", "job_type", "job_object_path"]
    additional_params = ["basename", "unit_type"]

    if unit_filter_field and unit_filter_field not in unit_params+additional_params:
        logger.error("Set unit_filter_field '{}' not one of '{}'".format(unit_filter_field, available_unit_filter_fields))
        return False

    for unit in systemd.ListUnits():
        unit_dict = {}
        assert (len(unit) == len(unit_params)), "Can't unpack the unit list - wrong number of arguments!"
        for i, param in enumerate(unit_params):
            unit_dict[param] = unit[i]

        unit_dict["basename"], unit_dict["unit_type"] = unit_dict["name"].rsplit('.', 1)

        if unit_filter_field is None or unit_dict[unit_filter_field] in unit_filter_values:
            units.append(unit_dict)

    units = sorted(units, key=itemgetter('name'))

    return units


def action_unit(action, unit):
    # See D-Bus documentation (linked above) for argument explanation
    job = False

    try:
        if action is "start":
            job = systemd.StartUnit(unit, "fail")
        elif action is "stop":
            job = systemd.StopUnit(unit, "fail")
        elif action is "restart":
            job = systemd.RestartUnit(unit, "fail")
        elif action is "reload":
            job = systemd.ReloadUnit(unit, "fail")
        elif action is "reload-or-restart":
            job = systemd.ReloadOrRestartUnit(unit, "fail")
        else:
            logger.error("Unknown action '{}' attempted on unit '{}'".format(action, unit))
    except Exception as e:
        logger.exception("Exception while trying to run '{}' on unit '{}'".format(action, unit))

    return job

if __name__ == "__main__":
    units_loaded = list_units('load', ['loaded'])
    units_active = list_units('active', ['active'])
    units_sub    = list_units('sub', ['sub'])

    for unit in units_loaded:
        print(unit["name"])

    for unit in units_active:
        print(unit["name"])

    for unit in units_sub:
        print(unit["name"])
