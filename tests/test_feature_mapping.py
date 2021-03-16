
import pytest

from shapelink.feat_util import (
    map_requested_features_to_defined_features)


def test_basic_feature_mapping():

    user_feats = ["image", "deform", "mask", "area_cvx"]
    feats = map_requested_features_to_defined_features(user_feats)

    assert isinstance(feats, list)
    assert len(feats) == 3

    sc, tr, im = feats
    assert sc == ["deform", "area_cvx"]
    # assert tr == ["trace"]
    assert im == ["image", "mask"]

    flattened_feats = [i for sublist in feats for i in sublist]
    for u_f in user_feats:
        assert u_f in flattened_feats


def test_basic_feature_mapping_with_traces():

    user_feats = ["image", "deform", "mask", "area_cvx", "trace/fl3_median"]
    feats = map_requested_features_to_defined_features(user_feats)

    assert isinstance(feats, list)
    assert len(feats) == 3

    sc, tr, im = feats
    assert sc == ["deform", "area_cvx"]
    assert tr == ["fl3_median"]
    assert im == ["image", "mask"]


def test_incorrect_feature_spelling_uppercase():

    user_feats = ["IMAGE"]
    with pytest.raises(ValueError):
        map_requested_features_to_defined_features(user_feats)


def test_incorrect_feature_spelling():

    user_feats = ["reform"]
    with pytest.raises(ValueError):
        map_requested_features_to_defined_features(user_feats)


def test_single_fluor_trace_feature():
    '''Check that a FLUOR_TRACES feature name is correctly mapped to the
    traces list. '''
    user_feats = ["fl1_median"]
    feats = map_requested_features_to_defined_features(user_feats)
    sc, tr, im = feats
    assert tr == ["fl1_median"]


def test_fluor_trace_feature_with_slash():
    '''Check that a FLUOR_TRACES feature name with the "trace/" prefix
    is correctly mapped to the traces list. '''
    user_feats = ["trace/fl1_median"]
    feats = map_requested_features_to_defined_features(user_feats)
    sc, tr, im = feats
    assert tr == ["fl1_median"]


def test_mix_fluor_traces_input():
    '''Check that a FLUOR_TRACES feature name with the "trace/" prefix
    is correctly mapped to the traces list. '''
    user_feats = ["trace/fl1_median", "fl2_raw"]
    feats = map_requested_features_to_defined_features(user_feats)
    sc, tr, im = feats
    assert tr == ["fl1_median", "fl2_raw"]


def test_all_fluor_trace_feature():
    '''Check that "trace" correctly returns all FLUOR_TRACES to the
    traces list. '''
    user_feats = ["trace"]
    feats = map_requested_features_to_defined_features(user_feats)
    sc, tr, im = feats
    assert tr == ["fl1_median", "fl1_raw", "fl2_median", "fl2_raw",
                  "fl3_median", "fl3_raw"]
