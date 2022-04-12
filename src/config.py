import typing as t


class ConfigDiscord(t.Dict[str, t.Any]):
    token: str
    prefix: str
    guild_ids: t.List[int]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigDiscord, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ConfigColorRoles(t.Dict[str, t.Any]):
    message_id: int
    role_ids: t.List[int]
    emoji_names: t.List[str]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigColorRoles, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ConfigReactionRoles(t.Dict[str, t.Any]):
    color_roles: ConfigColorRoles

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


class Config(t.Dict[str, t.Any]):
    discord: ConfigDiscord
    reaction_roles: ConfigReactionRoles
    notifications: t.List[ConfigNotifications]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(Config, self).__init__(*args, **kwargs)
        self.__dict__ = self
