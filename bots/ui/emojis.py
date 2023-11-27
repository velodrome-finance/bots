from typing import Sequence
from discord import Emoji


class Emojis:
    """Loads all custom emojis associated with current server and
    makes them available via get method"""

    def __init__(self, emojis: Sequence[Emoji]):
        """Load all custom emojis

        Args:
            emojis (Sequence[Emoji]): custom emojis attached to a server
        """
        self.emojis = {}
        for emoji in emojis:
            # based on: https://github.com/Rapptz/discord.py/issues/390
            self.emojis[emoji.name] = str(emoji)

    def get(self, name: str, fallback: str = "*") -> str:
        """Get custom emoji by name or return fallback string

        Args:
            name (str): name of the custom emoji to get
            fallback (str, optional): fallback value to return. Defaults to "*".

        Returns:
            str: _description_
        """
        return self.emojis[name] if name in self.emojis else fallback
