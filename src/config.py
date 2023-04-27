import typing as t


class ConfigDiscord(t.Dict[str, t.Any]):
    token: str
    prefix: str
    guild_ids: t.List[int]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigDiscord, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ConfigReactionRoles(t.Dict[str, t.Any]):
    message_id: int
    role_ids: t.List[int]
    emoji_names: t.List[str]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigReactionRoles, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ConfigNotifications(t.Dict[str, t.Any]):
    channel_id: int
    message: str
    cron: str

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigNotifications, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ConfigCommands(t.Dict[str, t.Any]):
    eval_timeout: float

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigCommands, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ConfigLavalink(t.Dict[str, t.Any]):
    host: str
    port: int
    password: str

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigLavalink, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ConfigCassandra(t.Dict[str, t.Any]):
    hosts: t.List[str]
    port: int
    keyspace: str

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigCassandra, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ConfigWelcome(t.Dict[str, t.Any]):
    guild_id: int
    channel_id: int
    headings: t.List[str]
    message: str

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigWelcome, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Config(t.Dict[str, t.Any]):
    discord: ConfigDiscord
    reaction_roles: t.Dict[str, ConfigReactionRoles]
    notifications: t.List[ConfigNotifications]
    commands: ConfigCommands
    lavalink: ConfigLavalink
    cassandra: ConfigCassandra
    welcome: t.Dict[str, ConfigWelcome]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(Config, self).__init__(*args, **kwargs)
        self.__dict__ = self
