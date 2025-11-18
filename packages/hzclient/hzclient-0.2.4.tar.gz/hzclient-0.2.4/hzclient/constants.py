from curl_cffi import requests
import zlib
import json
from .exceptions import ConstantError

CONSTANTS = {}
TEXT_CONSTANTS = {}

def decode_constants(data):
  try:
    decompressed = zlib.decompress(data, -zlib.MAX_WBITS)
  except zlib.error:
    decompressed = zlib.decompress(data)

  utf_str = decompressed.decode('utf-8')
  return json.loads(utf_str)


init_constants_called = False
def init_constants(*, debug: bool = False):
  global init_constants_called
  if init_constants_called:
    return
  init_constants_called = True

  url = "https://hz-static-2.akamaized.net/assets/data/constants_json.data"
  r = requests.get(url, timeout=10, impersonate="chrome")
  r.raise_for_status()
  CONSTANTS.update(decode_constants(r.content))
  if not CONSTANTS:
    raise ConstantError("Failed to initialize constants.")
  if debug:
    with open('tests/data/constants.json', 'w', encoding='utf-8') as f:
      json.dump(CONSTANTS, f, ensure_ascii=False, indent=4)


init_text_constants_called = False
def init_text_constants(locale="en_GB", *, debug: bool = False):
  global init_text_constants_called
  if init_text_constants_called:
    return
  init_text_constants_called = True

  url = f"https://hz-static-2.akamaized.net/assets/i18n/{locale}/text.data"
  r = requests.get(url, timeout=10, impersonate="chrome")
  r.raise_for_status()
  TEXT_CONSTANTS.update(decode_constants(r.content))
  if not TEXT_CONSTANTS:
    raise ConstantError("Failed to initialize text constants.")
  if debug:
    with open(f'tests/data/text_{locale}.json', 'w', encoding='utf-8') as f:
      json.dump(TEXT_CONSTANTS, f, ensure_ascii=False, indent=4)
