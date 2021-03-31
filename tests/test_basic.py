import pathlib
import threading
import re

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
                                "tcp://localhost:6666", 0)
                          )
    # setup plugin
    p = ExampleShapeLinkPlugin()
    # start simulator
    th.start()
    # start plugin
    for ii in range(49):
        p.handle_messages()
    th.join()


def test_run_plugin_with_verbose_start_simulator(capsys):
    # create new thread for simulator
    th = threading.Thread(target=shapein_simulator.start_simulator,
                          args=(str(data_dir / "calibration_beads_47.rtdc"),
                                ["deform", "area_um"],
                                "tcp://localhost:6666", 1)
                          )
    # print statements from verbose `start_simulator`
    verbose_str_1 = r"Opened dataset mm-hdf5_.* calibration_beads - M1\n"
    verbose_str_2 = r"Send event data:\n"
    verbose_str_3 = r"Simulation event rate: .* Hz\n" + \
                    r"Simulation time: .* s\n"

    # setup plugin
    p = ExampleShapeLinkPlugin()
    # start simulator
    th.start()
    # start plugin
    iterations = range(51)
    for ii in iterations:
        p.handle_messages()
        # collect verbose print statements for checking
        captured = capsys.readouterr()
        if ii == 0:
            match = re.match(verbose_str_1, captured.out)
        elif ii == 2:
            match = re.match(verbose_str_2, captured.out)
        elif ii == 50:
            match = re.match(verbose_str_3, captured.out)
        else:
            match = re.match('', '')
        assert captured.out == match.group()
    th.join()


def test_run_plugin_with_verbose_plugin(capsys):
    # create new thread for simulator
    th = threading.Thread(target=shapein_simulator.start_simulator,
                          args=(str(data_dir / "calibration_beads_47.rtdc"),
                                ["deform", "area_um"],
                                "tcp://localhost:6666", 0)
                          )
    # print statements from verbose plugin
    verbose_str_1 = " Init Shape-Link\n" + \
                    " Bind to: .*\n"
    verbose_str_2 = " Registered data container formats:\n" + \
                    " scalars: .*\n" + \
                    " traces: .*\n" + \
                    " images: .*\n" + \
                    " image_shape: .*\n"

    # setup plugin
    p = ExampleShapeLinkPlugin(verbose=True)
    # start simulator
    th.start()
    # start plugin
    for ii in range(49):
        p.handle_messages()
        # collect verbose print statements for checking
        captured = capsys.readouterr()
        if ii == 0:
            match = re.match(verbose_str_1, captured.out)
        elif ii == 1:
            match = re.match(verbose_str_2, captured.out)
        else:
            match = re.match('', '')
        assert captured.out == match.group()
    th.join()


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
