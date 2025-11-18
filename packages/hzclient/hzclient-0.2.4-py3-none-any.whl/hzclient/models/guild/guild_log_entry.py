from typing import Optional, Literal
from pydantic import Field, AliasChoices

from hzclient.models.base import _Base


class GuildLogEntry(_Base):
  id: str
  timestamp: int

  sender: Optional[str] = Field(default=None, validation_alias=AliasChoices("character_from_name", "sender", "character_name"))

  # "Chat" style entries
  message: Optional[str] = None
  is_private: Optional[bool] = None
  is_officer: Optional[bool] = None

  # "System/event" style entries
  type: Optional[int] = None
  value1: Optional[str] = None
  value2: Optional[str] = None
  value3: Optional[str] = None

  @property
  def kind(self) -> Literal["chat", "event", "unknown"]:
    if self.message is not None:
      return "chat"
    if self.type is not None:
      return "event"
    return "unknown"

  @property
  def is_chat(self) -> bool:
    return self.kind == "chat"

  @property
  def is_event(self) -> bool:
    return self.kind == "event"
