import shutil

import numpy as np

from shapelink import ShapeLinkPlugin

# We use the terminal width to make sure a line doesn't get cluttered
# with prints from a previous line.
TERMINAL_WIDTH = shutil.get_terminal_size((80, 20))[0]


class RollingMeansPlugin(ShapeLinkPlugin):
    """Displays a rolling mean of a few scalar features"""
    def __init__(self, *args, **kwargs):
        super(RollingMeansPlugin, self).__init__(*args, **kwargs)
        self.window_size = 100
        self.scalar_data = {}

    def after_register(self):
        print(" Preparing for transmission")
        for feat in self.hdf5_names.scalars:
            self.scalar_data[feat] = np.zeros(self.window_size) * np.nan

    def after_transmission(self):
        print("\n End of transmission\n")

    def handle_event(self, event_data):
        """Handle a new event"""
        window_index = event_data.id % self.window_size
        for ii, feat in enumerate(self.hdf5_names.scalars):
            self.scalar_data[feat][window_index] = event_data.scalars[ii]
        # print the first three features to stdout
        msgs = [" Rolling means: "]
        num_prints = min(3, len(self.hdf5_names.scalars))
        for ii in range(num_prints):
            feat = self.hdf5_names.scalars[ii]
            msgs.append("{}: {:.3g}".format(feat,
                                            np.mean(self.scalar_data[feat])))
        line = "  ".join(msgs)
        if len(line) < TERMINAL_WIDTH:
            line += " " * (TERMINAL_WIDTH - len(line))
        print(line, end="\r", flush=True)

        return False


info = {
    "class": RollingMeansPlugin,
    "description": "Display the rolling mean of a few scalar features",
    "name": "Rolling Means",
    "version": "0.1.0",
}
