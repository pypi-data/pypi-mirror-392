from datetime import datetime

from overkiz_runner import utils
from overkiz_runner.configuration import conf


def print_device_states(devices):
    for device in devices:
        if device.id != conf.appliance:
            continue

        for state in sorted(device.states, key=lambda s: s.name):
            print(device.id, end=" ")
            if utils.is_overkiz_date(state):
                print(
                    state.name,
                    "=>",
                    utils.overkiz_date_to_str(state.value),
                    flush=True,
                )
            else:
                print(state.name, "=>", state.value, flush=True)


def print_event(event):
    dt = datetime.now().replace(microsecond=0)
    ts = datetime.fromtimestamp(event.timestamp / 1000)
    if event.device_states:
        for state in event.device_states:
            print(
                dt.isoformat(),
                f"({ts.replace(microsecond=0).isoformat()})",
                event.device_url,
                state.name,
                "=>",
                state.value,
                flush=True,
            )
        return
    print(
        dt.isoformat(),
        f"({ts.replace(microsecond=0).isoformat()})",
    )
    for key in sorted(dir(event)):
        if key.startswith("_") or key in {
            "setupoid",
            "timestamp",
            "owner_key",
            "old_state",
        }:
            continue
        value = getattr(event, key)
        if not value or (key, value) == (
            "failure_type",
            "NO_FAILURE",
        ):
            continue
        if key == "new_state":
            print(" -", "state:", end=" ")
            if hasattr(event, "old_state"):
                print(event.old_state, "=>", end=" ")
            print(value)
        else:
            print(" -", key, ":", value)
    print(flush=True)
