from hzclient import CONSTANTS, TEXT_CONSTANTS


def test_constants():
  assert "quest_energy_refill_amount" in CONSTANTS


def test_text_constants():
  assert "guild/event/member_joined" in TEXT_CONSTANTS