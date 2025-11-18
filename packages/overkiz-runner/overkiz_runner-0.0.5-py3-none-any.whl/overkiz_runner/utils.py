from pyoverkiz.enums import OverkizState


def is_overkiz_date(state: OverkizState) -> bool:
    if "Date" not in state.name:
        return False
    if isinstance(state.value, dict):
        return False
    return True


def overkiz_date_to_str(value) -> str:
    final = ""
    for keys in (
        ("year", "month", "day"),
        ("weekday",),
        ("hour", "minute", "second"),
    ):
        strg = map(str, (value[key] for key in keys))
        final += ":".join(strg)
        final += " "
    return final.strip()
