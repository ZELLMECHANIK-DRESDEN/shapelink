import shutil

from shapelink import ShapeLinkPlugin

# We use the terminal width to make sure a line doesn't get cluttered
# with prints from a previous line.
TERMINAL_WIDTH = shutil.get_terminal_size((80, 20))[0]


class VerifyAspectRatioPlugin(ShapeLinkPlugin):
    """Check if the aspect ratio is correctly calculated.
    Shows a user how to choose features"""
    def __init__(self, *args, **kwargs):
        super(VerifyAspectRatioPlugin, self).__init__(*args, **kwargs)

    def after_register(self):
        print(" Preparing for transmission")

    def after_transmission(self):
        print("\n End of transmission\n")

    def choose_features(self):
        user_feats = ["size_x", "size_y", "aspect"]
        return user_feats

    def handle_event(self, event_data):
        """Handle a new event"""

        size_x, size_y, aspect = event_data.scalars
        calc_aspect = size_x / size_y
        calc_aspect = round(calc_aspect, 3)
        aspect = round(aspect, 3)
        assert calc_aspect == aspect

        print("Live Calc Aspect: {}, Orig Aspect: {}".format(
            calc_aspect, aspect
        ))

        return False


info = {
    "class": VerifyAspectRatioPlugin,
    "description": "Check if the aspect ratio is correctly calculated."
                   "Shows a user how to choose features.",
    "name": "Verify Aspect Ratio",
    "version": "0.1.0",
}
