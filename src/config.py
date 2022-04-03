import typing as t


class ConfigDiscord(t.Dict[str, t.Any]):
    token: str
    prefix: str
    guild_ids: t.List[int]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigDiscord, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Config(t.Dict[str, t.Any]):
    discord: ConfigDiscord

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(Config, self).__init__(*args, **kwargs)
        self.__dict__ = self
