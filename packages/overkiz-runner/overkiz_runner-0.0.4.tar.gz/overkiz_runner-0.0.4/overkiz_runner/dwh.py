from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState
from datetime import datetime, timezone
from pyoverkiz.models import Command


def get_dwh_values(device):
    return {
        "min-showers": device.states[
            OverkizState.CORE_MINIMAL_SHOWER_MANUAL_MODE
        ].value,
        "max-showers": device.states[
            OverkizState.CORE_MAXIMAL_SHOWER_MANUAL_MODE
        ].value,
        "is-absence-on": device.states[
            OverkizState.MODBUSLINK_DHW_ABSENCE_MODE
        ].value
        != OverkizCommandParam.OFF,
    }


async def execute(client, device, command: str):
    if command == "stop":
        utcnow = datetime.now(timezone.utc)

        start_date = {
            "month": utcnow.month,
            "hour": utcnow.hour,
            "year": utcnow.year,
            "weekday": utcnow.weekday(),
            "day": utcnow.day,
            "minute": utcnow.minute,
            "second": utcnow.second,
        }
        end_date = start_date.copy()
        end_date["year"] += 1

        await client.execute_commands(
            device.id,
            [
                Command(
                    OverkizCommand.SET_DATE_TIME,
                    [start_date],  # type: ignore
                ),
                Command(
                    OverkizCommand.SET_ABSENCE_START_DATE,
                    [start_date],  # type: ignore
                ),
                Command(
                    OverkizCommand.SET_ABSENCE_END_DATE,
                    [end_date],  # type: ignore
                ),
                Command(
                    OverkizCommand.SET_ABSENCE_MODE, [OverkizCommandParam.PROG]
                ),
            ],
            "setting absence on",
        )
    elif command in {"set-to-min", "set-to-max"}:
        state = get_dwh_values(device)
        if command == "set-to-min":
            nb_showers = state["min-showers"]
        else:
            nb_showers = state["max-showers"]

        label = f"setting showers to {nb_showers}"
        commands = [
            Command(OverkizCommand.SET_EXPECTED_NUMBER_OF_SHOWER, [nb_showers])
        ]
        if state["is-absence-on"]:
            wake_cmd = Command(
                OverkizCommand.SET_ABSENCE_MODE, [OverkizCommandParam.OFF]
            )
            commands.insert(0, wake_cmd)
            label = "awake and " + label
        await client.execute_commands(device.id, commands, label)

        await client.execute_commands(
            device.id,
            [
                Command("refreshNumberControlShowerRequest"),
                Command("refreshExpectedNumberOfShower"),
            ],
            f"refresh for ({label})",
        )
