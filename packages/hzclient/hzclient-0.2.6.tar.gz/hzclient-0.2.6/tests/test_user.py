from hzclient.models import User

def test_user_model(state):
  state.user = User(id=123, session_id="abc", premium_currency=50)
  assert state.user.id == 123
  assert state.user.session_id == "abc"
  assert state.user.premium_currency == 50

  state.user.premium_currency += 50
  assert state.user.premium_currency == 100

  state.update({"user": {"premium_currency": 200}})
  assert state.user.premium_currency == 200
  assert state.user.id == 123 # unchanged
  assert state.user.session_id == "abc" # unchanged