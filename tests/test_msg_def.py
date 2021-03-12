
from shapelink.msg_def import message_ids


def test_message_ids_negative(message_ids=message_ids):
    for key in message_ids:
        assert message_ids[key] < 0, "Should be negative"


def test_message_ids_int(message_ids=message_ids):
    for key in message_ids:
        assert isinstance(message_ids[key], int), "Should be an int"
