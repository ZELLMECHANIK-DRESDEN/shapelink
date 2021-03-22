import pathlib

from shapelink import ShapeLinkPlugin
from shapelink.shapelink_plugin import EventData

data_dir = pathlib.Path(__file__).parent / "data"


class ExampleShapeLinkPlugin(ShapeLinkPlugin):
    def choose_features(self):
        return list()

    def handle_event(self, event_data: EventData) -> bool:
        return False


def test_default_port_and_IP(random_port=False):
    # setup plugin
    p = ExampleShapeLinkPlugin(random_port=random_port)
    assert p.port_address == "6666"
    assert p.ip_address == "tcp://*"


def test_random_IP(random_port=True):
    # setup plugin
    p = ExampleShapeLinkPlugin(random_port=random_port)
    assert p.ip_address == "tcp://*"
    assert isinstance(p.port_address, int)
    assert 49152 < p.port_address < 65536


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
