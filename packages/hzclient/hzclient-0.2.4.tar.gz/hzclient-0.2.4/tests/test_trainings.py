def test_trainings(state):
  assert isinstance(state.trainings, list)
  assert len(state.trainings) > 0
  assert state.trainings[0].id == 50633

  state.update({
    "trainings": []
  })
  assert len(state.trainings) == 0