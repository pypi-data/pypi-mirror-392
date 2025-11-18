from typing import Any, Dict, List
from pydantic import Field, model_validator
from ..base import _Base
from .guild_log_entry import GuildLogEntry


class GuildLog(_Base):
  entries: Dict[str, GuildLogEntry] = Field(default_factory=dict)

  @model_validator(mode="before")
  @classmethod
  def parse_guild_log(cls, v: Any) -> Any:
    """
    Accept raw mapping of {log_id: payload} and normalize it into
    {"entries": {log_id: {..., "id": log_id}}}
    so Pydantic can build GuildLogEntry instances.
    """
    if isinstance(v, dict) and "entries" not in v:
      # v is the raw guild_log object from the server
      return {
        "entries": {
          log_id: {"id": log_id, **payload}
          for log_id, payload in v.items()
        }
      }
    return v

  # ---- API helpers ----

  def all(self) -> List[GuildLogEntry]:
    """All entries sorted by timestamp ascending."""
    return sorted(self.entries.values(), key=lambda e: e.timestamp)

  def count(self) -> int:
    """Return the number of guild log entries."""
    return len(self.entries)

  def __iter__(self):
    """So you can do: for entry in game_state.guild_log"""
    return iter(self.all())
