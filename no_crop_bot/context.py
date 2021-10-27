class _Option:
    def __init__(self, option_id: str, name: str, option_type: type, default,
                 option_text: str):
        self.id = option_id
        self.name = name
        self.type = option_type
        self.text = option_text
        self.default = default


class UserData:
    settings = [
        _Option('resize', "Resize", bool, False,
                "Do you want to resize image to 1080x1080?"),
        _Option('auto_delete', "Auto delete", bool, False,
                "Should I delete messages, you send me?")
    ]

    class Extra:
        settings_message_id = "settings_message_id"
