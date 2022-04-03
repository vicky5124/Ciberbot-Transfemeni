import typing as t

import lightbulb

from src.main import CiberBot


class Context(lightbulb.Context):
    @property
    def bot(self) -> CiberBot:
        return t.cast(CiberBot, self.app)


class Plugin(lightbulb.Plugin):
    @property
    def bot(self) -> CiberBot:
        return t.cast(CiberBot, self.app)
