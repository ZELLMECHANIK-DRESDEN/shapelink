import pathlib
import threading
import pytest
import numpy as np
import dclab

from shapelink import shapein_simulator
from shapelink import ShapeLinkPlugin
from shapelink.shapelink_plugin import EventData

data_dir = pathlib.Path(__file__).parent / "data"
ds_test = dclab.new_dataset(data_dir / "calibration_beads_47.rtdc")


class ChooseFeaturesShapeLinkPlugin(ShapeLinkPlugin):
    """Checks if only the chosen features are transferred"""
    def __init__(self, *args, **kwargs):
        super(ChooseFeaturesShapeLinkPlugin, self).__init__(*args, **kwargs)

    def choose_features(self):
        user_feats = ["deform", "circ", "image"]
        return user_feats

    def handle_event(self, event_data: EventData) -> bool:
        """Check that the chosen features were transferred"""
        assert self.reg_features.scalars == ["deform", "circ"]
        assert self.reg_features.scalars != ["circ", "deform"]
        assert self.reg_features.traces == []
        assert self.reg_features.images == ["image"]

        return False


def test_run_plugin_with_user_defined_features():
    # create new thread for simulator
    th = threading.Thread(target=shapein_simulator.start_simulator,
                          args=(str(data_dir / "calibration_beads_47.rtdc"),
                                None, "tcp://localhost:6667", 0)
                          )
    # setup plugin
    p = ChooseFeaturesShapeLinkPlugin(bind_to='tcp://*:6667')
    # start simulator
    th.start()
    # start plugin
    for ii in range(49):
        p.handle_messages()


class FailChooseFeaturesShapeLinkPlugin(ShapeLinkPlugin):
    """Raises a ValueError because 'deformation' isn't a feature"""
    def __init__(self, *args, **kwargs):
        super(FailChooseFeaturesShapeLinkPlugin, self).__init__(
            *args, **kwargs)

    def choose_features(self):
        user_feats = ["deformation", "circ", "image"]
        return user_feats

    def handle_event(self, event_data: EventData) -> bool:
        """Check that the chosen features were transferred"""
        assert self.reg_features.scalars == ["deformation", "circ"]
        assert self.reg_features.traces == []
        assert self.reg_features.images == ["image"]

        return False


def test_run_plugin_with_bad_user_defined_features():
    # create new thread for simulator
    th = threading.Thread(target=shapein_simulator.start_simulator,
                          args=(str(data_dir / "calibration_beads_47.rtdc"),
                                None, "tcp://localhost:6667", 0)
                          )
    # setup plugin
    p = FailChooseFeaturesShapeLinkPlugin(bind_to='tcp://*:6667')
    # start simulator
    th.start()
    # start plugin
    with pytest.raises(ValueError):
        p.handle_messages()


class ChooseScalarFeaturesShapeLinkPlugin(ShapeLinkPlugin):
    """Checks if only the chosen features are transferred"""
    def __init__(self, *args, **kwargs):
        super(ChooseScalarFeaturesShapeLinkPlugin, self).__init__(
            *args, **kwargs)

    def choose_features(self):
        user_feats = ['area_cvx', 'area_msd', 'area_ratio', 'area_um',
                      'aspect', 'bright_avg', 'bright_sd', 'circ', 'deform',
                      'pos_x', 'pos_y', 'size_x', 'size_y',
                      'tilt', 'time', 'volume']
        return user_feats

    def handle_event(self, event_data: EventData) -> bool:
        """Check that the chosen scalar features were transferred"""
        for feat in event_data.scalars:
            assert isinstance(feat, float)

        return False


def test_run_plugin_with_user_defined_scalar_features():
    # create new thread for simulator
    th = threading.Thread(target=shapein_simulator.start_simulator,
                          args=(str(data_dir / "calibration_beads_47.rtdc"),
                                None, "tcp://localhost:6668", 0)
                          )
    # setup plugin
    p = ChooseScalarFeaturesShapeLinkPlugin(bind_to='tcp://*:6668')
    # start simulator
    th.start()
    # start plugin
    for ii in range(49):
        p.handle_messages()


class ChooseImageFeaturesShapeLinkPlugin(ShapeLinkPlugin):
    """Checks if only the chosen image features are transferred"""
    def __init__(self, *args, **kwargs):
        super(ChooseImageFeaturesShapeLinkPlugin, self).__init__(
            *args, **kwargs)

    def choose_features(self):
        user_feats = ["image", "contour", "mask", "index"]
        return user_feats

    def handle_event(self, event_data: EventData) -> bool:
        """Check that the chosen image features were transferred"""
        index = event_data.scalars[0]
        image, contour, mask = event_data.images

        # check the shape of the image features
        assert self.reg_features.images == ["image", "contour", "mask"]
        assert len(contour.shape) == 2, "should have two axes, x and y"
        assert contour.shape[-1] == 2, "final axis should be length 2"
        assert len(image.shape) == 2, "should be two axes, x and y"
        assert len(mask.shape) == 2, "should be two axes, x and y"

        image_known = ds_test["image"][0]
        contour_known = ds_test["contour"][0]
        mask_known = ds_test["mask"][0]

        # check that the data matches between before and after transfer
        if index == 1:  # dclab["index"] starts at 1
            assert np.allclose(image, image_known)
            assert np.allclose(contour, contour_known)
            assert np.allclose(mask, mask_known)

        return False


def test_run_plugin_with_user_defined_image_features():
    # create new thread for simulator
    th = threading.Thread(target=shapein_simulator.start_simulator,
                          args=(str(data_dir / "calibration_beads_47.rtdc"),
                                None, "tcp://localhost:6667", 0)
                          )
    # setup plugin
    p = ChooseImageFeaturesShapeLinkPlugin(bind_to='tcp://*:6667')
    # start simulator
    th.start()
    # start plugin
    for ii in range(49):
        p.handle_messages()


class ChooseTraceFeaturesShapeLinkPlugin(ShapeLinkPlugin):
    """All FLUOR_TRACES are transferred because "trace" is provided"""
    def __init__(self, *args, **kwargs):
        super(ChooseTraceFeaturesShapeLinkPlugin, self).__init__(
            *args, **kwargs)

    def choose_features(self):
        user_feats = ["deform", "circ", "image", "trace"]
        return user_feats

    def handle_event(self, event_data: EventData) -> bool:
        """Check that the chosen features were transferred"""
        assert self.reg_features.scalars == ["deform", "circ"]
        assert self.reg_features.traces == [
            "fl1_median", "fl1_raw", "fl2_median",
            "fl2_raw", "fl3_median", "fl3_raw"]
        assert self.reg_features.images == ["image"]

        return False


def test_run_plugin_with_user_defined_trace_features():
    # create new thread for simulator
    th = threading.Thread(target=shapein_simulator.start_simulator,
                          args=(str(data_dir / "calibration_beads_47.rtdc"),
                                None, "tcp://localhost:6668", 0)
                          )
    # setup plugin
    p = ChooseTraceFeaturesShapeLinkPlugin(bind_to='tcp://*:6668')
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
