from helpers import setup_logger
from pydbus import SystemBus

logger = setup_logger(__name__, "warning")

# See D-Bus documentation here:
#     https://www.freedesktop.org/wiki/Software/systemd/dbus/

bus = SystemBus()
systemd = bus.get(".systemd1")

def list_units(unit_filter_field = None, unit_filter_values = []):
    units = []

    for unit in systemd.ListUnits():
        name, description, load, active, sub, follower, unit_object_path, job_queued, job_type, job_object_path = unit

        basename, unit_type = name.rsplit('.', 1)

        if unit_filter_field is None or locals()[unit_filter_field] in unit_filter_values:
            units.append({
                "name": name,
                "basename": basename,
                "type": unit_type,
                "description": description,
                "load": load,
                "active": active,
                "sub": sub,
                "follower": follower,
                "unit_object_path": unit_object_path,
                "job_queued": job_queued,
                "job_type": job_type,
                "job_object_path": job_object_path
            })

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
            logger.warning("Unknown action '{}' attempted on unit '{}'".format(action, unit))
    except Exception as e:
        logger.error("Exception while trying to run '{}' on unit '{}'".format(action, unit))
        logger.exception(e)

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
