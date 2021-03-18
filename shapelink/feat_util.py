
import dclab.definitions as dfn


def map_requested_features_to_defined_features(features):
    """Map the flat list from plugin to list of 3 lists: sc, tr, im

    For example::

        input: 	["size_x", "size_y", "aspect"]
        output: [["size_x", "size_y", "aspect"], [], []]

    Parameters
    ----------
    features : list
        A flat list of strings which is mapped to features as defined
        in the `dclab.definitions` module.
    """
    sc_features, tr_features, im_features = [], [], []
    for feat in features:
        # deal with Fluorescence trace feature names
        if feat in dfn.FLUOR_TRACES:
            tr_features.append(feat)
        elif feat.startswith("trace/"):
            fluor_name = feat.split("/")[-1]
            if fluor_name in dfn.FLUOR_TRACES:
                tr_features.append(fluor_name)
        elif feat == "trace":
            for fluor_name in dfn.FLUOR_TRACES:
                tr_features.append(fluor_name)
        # deal with Scalar feature names
        elif dfn.feature_exists(feat, scalar_only=True):
            sc_features.append(feat)
        # deal with non-scalar features (excl. traces)
        elif dfn.feature_exists(feat, scalar_only=False):
            im_features.append(feat)
        else:
            raise ValueError("Invalid feature name '{}'".format(feat))

    mapped_features = list((sc_features, tr_features, im_features))
    return mapped_features
