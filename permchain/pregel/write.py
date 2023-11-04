from __future__ import annotations

from typing import Any, Callable, Sequence

from langchain.schema.runnable import (
    Runnable,
    RunnableConfig,
    RunnablePassthrough,
)
from langchain.schema.runnable.utils import ConfigurableFieldSpec

from permchain.pregel.constants import CONFIG_KEY_SEND

TYPE_SEND = Callable[[Sequence[tuple[str, Any]]], None]


class ChannelWrite(RunnablePassthrough):
    channels: Sequence[tuple[str, Runnable]]
    """
    Mapping of write channels to Runnables that return the value to be written,
    or None to skip writing.
    """

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        *,
        channels: Sequence[tuple[str, Runnable]],
    ):
        super().__init__(func=self._write, afunc=self._awrite, channels=channels)

    @property
    def config_specs(self) -> Sequence[ConfigurableFieldSpec]:
        return [
            ConfigurableFieldSpec(
                id=CONFIG_KEY_SEND,
                name=CONFIG_KEY_SEND,
                description=None,
                default=None,
                annotation=TYPE_SEND,
            ),
        ]

    def _write(self, input: Any, config: RunnableConfig) -> None:
        write: TYPE_SEND = config["configurable"][CONFIG_KEY_SEND]

        values = [(chan, r.invoke(input, config)) for chan, r in self.channels]

        write([(chan, val) for chan, val in values if val is not None])

    async def _awrite(self, input: Any, config: RunnableConfig) -> None:
        write: TYPE_SEND = config["configurable"][CONFIG_KEY_SEND]

        values = [(chan, await r.ainvoke(input, config)) for chan, r in self.channels]

        write([(chan, val) for chan, val in values if val is not None])