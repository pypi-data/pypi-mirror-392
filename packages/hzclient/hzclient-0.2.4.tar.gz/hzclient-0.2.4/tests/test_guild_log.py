def test_guild_log(state):
  assert state.guild_log.count() > 0


def test_msg(state):
  first = state.guild_log.all()[0]
  assert isinstance(first.message, str)
  assert first.is_officer is True
  assert first.message == "Hello, World!"
  assert first.sender == "Lucas"