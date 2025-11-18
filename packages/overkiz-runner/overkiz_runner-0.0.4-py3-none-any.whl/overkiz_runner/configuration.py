from the_conf import TheConf

conf = TheConf(
    {
        "source_order": ["cmd", "files"],
        "config_files": [
            "~/.config/overkiz.json",
            "/etc/overkiz/overkiz.json",
        ],
        "parameters": [
            {
                "type": "list",
                "credentials": [
                    {"username": {"type": str, "no_cmd": True}},
                    {"password": {"type": str, "no_cmd": True}},
                    {"servertype": {"type": str, "no_cmd": True}},
                ],
            },
            {
                "type": "list",
                "gateways": [
                    {"id": {"type": str, "no_cmd": True}},
                    {"token": {"type": str, "no_cmd": True}},
                    {"port": {"type": int, "no_cmd": True}},
                    {"ip": {"type": str, "no_cmd": True}},
                ],
            },
            {"watch": [{"interval": {"default": 2}}]},
            {"appliance": {"type": str, "required": True}},
            {
                "command": {
                    "type": str,
                    "required": True,
                    "among": [
                        "set-to-min",
                        "set-to-max",
                        "stop",
                        "listen-events",
                        "show-states",
                    ],
                }
            },
        ],
    }
)
