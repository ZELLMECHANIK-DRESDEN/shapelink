

# Allow only real RT-DC features
def check_for_allowed_features(feat_list):
    for feat in feat_list:
        if feat not in features_allowed:
            raise ValueError(
                "'{}' is not an allowed feature. Check "
                "https://dclab.readthedocs.io/en/stable/sec_av_notation.html "
                "for information on allowed features.".format(feat))

# just use feature_exists(name, scalar_only=False)