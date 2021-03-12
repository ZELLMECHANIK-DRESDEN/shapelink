
from shapelink.shapelink_plugin import EventData


def test_eventdata_attribute_types(EventData=EventData):

    e = EventData()
    assert isinstance(e.id, int), "Should be an int"
    assert isinstance(e.scalars, list), "Should be a list"
    assert isinstance(e.traces, list), "Should be a list"
    assert isinstance(e.images, list), "Should be a list"
