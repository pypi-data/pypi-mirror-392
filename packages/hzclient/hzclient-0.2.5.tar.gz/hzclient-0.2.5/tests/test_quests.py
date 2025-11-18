def test_quests(state):
  assert isinstance(state.quests, list)
  assert len(state.quests) > 0
  assert state.quests[0].id == 260403