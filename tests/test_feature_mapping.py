
import pytest

from shapelink.feat_util import (
    map_requested_features_to_defined_features)


def test_basic_feature_mapping():

    user_feats = ["image", "deform", "trace", "area_cvx"]
    feats = map_requested_features_to_defined_features(user_feats)

    assert isinstance(feats, list)
    assert len(feats) == 3

    sc, tr, im = feats
    assert sc == ["deform", "area_cvx"]
    # assert tr == ["trace"]
    assert im == ["image", "trace"]

    flattened_feats = [i for sublist in feats for i in sublist]
    for u_f in user_feats:
        assert u_f in flattened_feats


def test_incorrect_feature_spelling_uppercase():

    user_feats = ["IMAGE"]
    with pytest.raises(ValueError):
        map_requested_features_to_defined_features(user_feats)


def test_incorrect_feature_spelling():

    user_feats = ["reform"]
    with pytest.raises(ValueError):
        map_requested_features_to_defined_features(user_feats)


def test_ancillary_feature():
    # need to exclude volume and other ancillary features

    # user_feats = ["volume"]
    # with pytest.raises(ValueError):
    #     map_requested_features_to_defined_features(user_feats)
    pass


def test_fluor_trace_feature():
    # need to include FLUOR_TRACES when a trace is asked for.
    # Shouldn't need "trace" to be given in user_feats

    # user_feats = ["fl1_median"]
    # feats = map_requested_features_to_defined_features(user_feats)
    # sc, tr, im = feats
    # assert tr == ["fl1_median"]
    pass


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
