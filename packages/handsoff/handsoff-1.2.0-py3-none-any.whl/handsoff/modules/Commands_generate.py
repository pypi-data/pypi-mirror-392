class Commands_generate:
    valid_params = {"host", "port", "user", "target", "file", "pem", "client", "server"}
    def __init__(self, settings: dict[str, str] = {}) -> None:
        self.settings = {}
        self.settings["port"] = "22"
        if(settings):
            for key, value in settings.items():
                if key in self.valid_params:
                    self.settings[key] = value            
    def set_parameters_(self, parameters: dict[str, str]) -> None:
        for key, value in parameters.items():
            if key in self.valid_params:
                self.settings[key] = value
    def get_parameters(self) -> dict[str, str]:
        return self.settings
    def _is_command_valid(self) -> bool:
        required = ["host", "user", "client"]
        return all(self.settings.get(k) for k in required)
    
    def pull(self, file: tuple[str, ...] = (), target: str = "") -> str:
        if(not self._is_command_valid()):
            raise ValueError("Command is not valid. You need at least HOST, USER, PORT, SERVER, CLIENT.")
        if(not target and not self.settings.get('server')):
            raise ValueError("Command is not valid. You need where to pull your data.")
        result: str = "scp" + " "
        result += f"-P {self.settings['port']}" + " "
        if(pem := self.settings.get("pem")):
            result += f"-i {pem}" + " "
        prefix = f"{self.settings['user']}@{self.settings['host']}:{target or self.settings.get('server')}"
        result += " ".join(map(
            lambda item: prefix + item, file
        )) + " "
        result += self.settings['client']
        return result
    def push(self, file: tuple[str, ...] = (), target: str = "") -> str:
        if(not self._is_command_valid()):
            raise ValueError("Command is not valid. You need at least HOST, USER, PORT, SERVER, CLIENT.")
        if(not target and not self.settings.get('server')):
            raise ValueError("Command is not valid. You need where to push your data.")
        result: str = "scp" + " "
        result += f"-P {self.settings['port']}" + " "
        if(pem := self.settings.get("pem")):
            result += f"-i {pem}" + " "
        result += " ".join(map(
            lambda item: self.settings['client'] + item, file
        )) + " "
        result += f"{self.settings['user']}@{self.settings['host']}:{target or self.settings.get('server')}"
        return result
