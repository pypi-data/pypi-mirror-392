from hzclient.state import GameState

def test_clear_state():
  state = GameState()

  state.user.premium_currency = 500
  state.character.name = "TestChar"
  assert state.user.premium_currency == 500
  assert state.character.name == "TestChar"
  state.clear()

  assert state.user.premium_currency == 0
  assert state.character.name == ""
