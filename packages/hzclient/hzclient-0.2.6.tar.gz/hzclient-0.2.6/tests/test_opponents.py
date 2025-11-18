def test_opponents(state):
  state.update({
    "leaderboard_characters": [
      {
        "id": 123,
        "name": "Opponent1"
      }
    ]
  })
  assert isinstance(state.opponents, list)
  assert len(state.opponents) == 1

  state.update({
    "opponent": {
      "id": 456,
      "name": "Opponent2"
    }
  })

  assert len(state.opponents) == 2

  state.update({
    "opponent": {
      "id": 123,
      "stat_total_strength": 123
    }
  })

  assert state.opponents[0].stat_total_strength == 123


def test_opponent_simulation(state):
  char = {'id': 1, 'stat_total_strength': 100, 'stat_total_stamina': 100, 'stat_total_critical_rating': 50, 'stat_total_dodge_rating': 50}
  state.update({
    "character": char,
    "opponent": char
  })
  opponent = state.opponents[-1]
  assert opponent.id == 1
  assert opponent.stat_total_strength == 100

  result = opponent.get_win_chance(state.character)
  assert 0.4 <= result <= 0.6
