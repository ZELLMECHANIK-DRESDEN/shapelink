import pathlib
import threading

from shapelink import shapein_simulator
from shapelink import ShapeLinkPlugin
from shapelink.shapelink_plugin import EventData

data_dir = pathlib.Path(__file__).parent / "data"


class ExampleShapeLinkPlugin(ShapeLinkPlugin):
    def choose_features(self):
        return list()

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


class ChooseFeaturesShapeLinkPlugin(ShapeLinkPlugin):
    def choose_features(self):
        sc_features = ["deform", "circ"]
        tr_features = ["fl2_pos"]
        im_features = ["image"]
        user_feats = list((sc_features, tr_features, im_features))
        return user_feats

    def handle_event(self, event_data: EventData) -> bool:
        return False


def test_run_plugin_with_user_defined_features():
    # create new thread for simulator
    th = threading.Thread(target=shapein_simulator.start_simulator,
                          args=(str(data_dir / "calibration_beads_47.rtdc"),
                                None, 0)
                          )
    # setup plugin
    p = ChooseFeaturesShapeLinkPlugin()
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
