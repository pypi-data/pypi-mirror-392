def test_guild_log(state):
  assert state.guild_log.count() > 0


def test_msg(state):
  first = state.guild_log.all()[0]
  assert isinstance(first.message, str)
  assert first.is_officer is True
  assert first.message == "Hello, World!"
  assert first.sender == "Lucas"


def test_append_guild_chat_message_to_log(state):
  assert state.guild_log.count() == 4

  data = {
    "guild_chat_message": {
      "id": "1763142958_41088",
      "timestamp": 1763142958,
      "character_from_name": "Me",
      "message": "Test message",
      "is_private": 0,
      "is_officer": 0,
      "character_to_id": 0,
    }
  }

  state.update(data)

  assert state.guild_log.count() == 5
