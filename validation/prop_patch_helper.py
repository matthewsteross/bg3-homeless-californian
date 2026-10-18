"""Test helper: remove prop-lifetime Spawn terms that the build already patched into the generated spell text."""
import re

_TEXT = re.compile(r';GROUND:Spawn\([0-9a-fA-F-]{36}, ,HC_PROP_LIFETIME_10T\)')
_BYTES = re.compile(rb';GROUND:Spawn\([0-9a-fA-F-]{36}, ,HC_PROP_LIFETIME_10T\)')


def unpatched(data):
    return _BYTES.sub(b'', data) if isinstance(data, bytes) else _TEXT.sub('', data)
