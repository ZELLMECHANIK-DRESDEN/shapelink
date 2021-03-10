
import dclab.definitions as dfn


def map_requested_features_to_defined_features(features):
	'''
	Map the flat list from plugin to list of 3 lists: sc, tr, im
	For example:
	input: 	["size_x", "size_y", "aspect"]
	output: [["size_x", "size_y", "aspect"], [], []]
	
	Parameters
	----------
	features : list
		A flat list which is mapped to features as defined in dclab.definitions

	'''

	sc_features, tr_features, im_features = [], [], []
	for feat in features:
		if dfn.feature_exists(feat, scalar_only=False):
			if dfn.feature_exists(feat, scalar_only=True):
				sc_features.append(feat)
			elif feat in dfn.FLUOR_TRACES:
				tr_features.append(feat)
			else:
				im_features.append(feat)
		else:
			raise ValueError("Invalid feature name '{}'".format(feat))

	mapped_features = list((sc_features, tr_features, im_features))
	return mapped_features
