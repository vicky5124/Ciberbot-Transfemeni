import json
import typing as t


class CustomDict(t.Dict[str, t.Any]):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(CustomDict, self).__init__(*args, **kwargs)
        mapping_proxy = args[0]
        self.classes = mapping_proxy['__annotations__']

        for name, value in kwargs.items():
            attr = self.__get_attr(name=name, value=value)
            self.__setattr__(name, attr)

    def __get_attr(self, *, name=None, value):
        type_ = type(value)
        if type_ in [str, float, int]:
            attr = value
        else:
            if not name or not isinstance(self.classes[name], type):
                if type_ == list:
                    attr = [self.__get_attr(value=i)
                            for i in value]
                else:  # if type_ == dict
                    attr = {key: self.__get_attr(value=dict_)
                            for key, dict_ in value.items()}
            else:  # if issubclass(clase, CustomDict)
                class_ = self.classes[name]
                attr = class_.init(value)
        return attr

    @classmethod
    def init(cls, data):
        return cls(cls.__dict__, **data)

    def __hash__(self):
        return hash(json.dumps(self.__dict__, sort_keys=True))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)
        return False


class ConfigDiscord(CustomDict):
    token: str
    prefix: str
    guild_ids: t.List[int]


class ConfigReactionRoles(CustomDict):
    message_id: int
    role_ids: t.List[int]
    emoji_names: t.List[str]


class ConfigNotifications(CustomDict):
    channel_id: int
    message: str
    cron: str
    probability: t.Optional[float]


class ConfigCommands(CustomDict):
    eval_timeout: float


class ConfigLavalink(CustomDict):
    host: str
    port: int
    password: str


class ConfigCassandra(CustomDict):
    hosts: t.List[str]
    port: int
    keyspace: str


class ConfigWelcome(CustomDict):
    guild_id: int
    channel_id: int
    headings: t.List[str]
    message: str


class Config(CustomDict):
    discord: ConfigDiscord
    reaction_roles: t.Dict[str, ConfigReactionRoles]
    notifications: t.List[ConfigNotifications]
    commands: ConfigCommands
    lavalink: ConfigLavalink
    cassandra: ConfigCassandra
    welcome: t.Dict[str, ConfigWelcome]
