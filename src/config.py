import typing as t


class ConfigDiscord(dict[str, t.Any]):
    token: str
    prefix: str
    guild_ids: list[int]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(ConfigDiscord, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Config(dict[str, t.Any]):
    discord: ConfigDiscord

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(Config, self).__init__(*args, **kwargs)
        self.__dict__ = self
