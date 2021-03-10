
import dclab.definitions as dfn


def map_requested_features_to_defined_features(features):
	'''
	Map the input flat list from plugin to list of 3 lists: sc, tr, im
	input: 	["size_x", "size_y", "aspect"]
	output: [["size_x", "size_y", "aspect"], [], []]
	'''

	sc_features, tr_features, im_features = [], [], []
	for feat in features:
		dfn.feature_exists(feat, scalar_only=False)

		if dfn.feature_exists(feat, scalar_only=True):
			sc_features.append(feat)
		elif feat in dfn.FLUOR_TRACES:
			tr_features.append(feat)
		else:
			im_features.append(feat)
	mapped_features = list((sc_features, tr_features, im_features))
	return mapped_features
