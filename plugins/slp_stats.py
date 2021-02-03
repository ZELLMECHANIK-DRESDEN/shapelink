"""Shape-Link plug-in that prints statistics to stdout"""
from shapelink import ShapeLinkPlugin


class StatsPlugin(ShapeLinkPlugin):
    def handle_event(self, event_data):
        """Handle a new event"""
        print("Event ID:", event_data.id)

        assert len(event_data.scalars) == len(
            self.registered_data_format.scalars)
        assert len(event_data.traces) == len(
            self.registered_data_format.traces)
        assert len(event_data.images) == len(
            self.registered_data_format.images)

        return False


info = {
    "class": StatsPlugin,
    "description": "A simple plugin that displays statistics",
    "name": "Statistics plugin",
    "version": "0.1.0",
}
