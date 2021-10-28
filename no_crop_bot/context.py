class _Option:
    def __init__(self, name: str, option_type: type, default,
                 option_text: str):
        self.name = name
        self.type = option_type
        self.text = option_text
        self.default = default

    def __str__(self) -> str:
        return f'"{self.name}": {self.type}({self.default})'

    def __repr__(self) -> str:
        return f'<_Option(name="{self.name}", type={self.type}, default={self.default})>'


class UserData:
    settings = {
        'resize': _Option("Resize", bool, False,
                          "Do you want to resize image to 1080x1080?"),
        'auto_delete': _Option("Auto delete", bool, False,
                               "Should I delete messages, you send me?"),
        'blur': _Option("Blur", int, 0,
                        "Use blurred image instead of white canvas")
    }

    class Extra:
        settings_req_message_id = 'settings_req_message_id'
        settings_ack_message_id = 'settings_ack_message_id'
        setting_to_change = 'setting_to_change'
