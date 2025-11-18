import ruuid4
import re

UUID4_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

def test_uuid4_format():
    u = ruuid4.uuid4()
    assert isinstance(u, str)
    assert UUID4_REGEX.match(u)