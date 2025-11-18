import hzclient.models.ad_info as admod

def _freeze(monkeypatch, t: int | float):
  monkeypatch.setattr(admod, "time", lambda: t)

def test_ad_info(monkeypatch, state):
  assert state.ad_info is not None

  # After login
  base_ts = state.ad_info.ts_last_update__2
  _freeze(monkeypatch, base_ts)

  remaining_cooldown_2 = state.ad_info.remaining_cooldown(2)
  assert remaining_cooldown_2 != 0 # should be in cooldown after login

  _freeze(monkeypatch, base_ts + remaining_cooldown_2 + 1)
  assert state.ad_info.remaining_cooldown(2) <= 0 # cooldown should be over


  # Start of test
  _freeze(monkeypatch, base_ts)
  assert state.ad_info.remaining_cooldown(1) == 0

  state.ad_info.watch_ad(1)
  remaining_cooldown_1 = state.ad_info.remaining_cooldown(1)
  assert remaining_cooldown_1 > 0 # should be in cooldown (after watching ad)
  assert state.ad_info.ts_last_update__1 == base_ts # timestamp should not change yet

  _freeze(monkeypatch, base_ts + remaining_cooldown_1 + 1)
  assert state.ad_info.remaining_cooldown(1) <= 0 # cooldown should be over