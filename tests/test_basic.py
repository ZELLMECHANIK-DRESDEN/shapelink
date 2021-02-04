import pathlib
import threading

from shapelink import shapein_simulator
from shapelink import ShapeLinkPlugin
from shapelink.shapelink_plugin import EventData

data_dir = pathlib.Path(__file__).parent / "data"


class ExampleShapeLinkPlugin(ShapeLinkPlugin):
    def handle_event(self, event_data: EventData) -> bool:
        return False


def test_run_plugin_with_simulator():
    # create new thread for simulator
    th = threading.Thread(target=shapein_simulator.start_simulator,
                          args=(str(data_dir / "calibration_beads_47.rtdc"),
                                ["deform", "area_um"],
                                0)
                          )
    # setup plugin
    p = ExampleShapeLinkPlugin()
    # start simulator
    th.start()
    # start plugin
    for ii in range(49):
        p.handle_messages()


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
