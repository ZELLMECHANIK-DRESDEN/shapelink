import importlib
import pathlib
import sys
import threading

import click

from . import shapein_simulator


@click.group()
def main():
    pass


@click.command()
@click.argument("path")
@click.option("--features", "-f",
              help="Comma-separated list of features to send by the "
                   + "Shape-In simulator; Defaults to all innate features. "
                   + "A list of valid feature names can be found in "
                   + "the dclab docs (Advanced Usage -> Notation).")
def run_simulator(path, features=None):
    """Run the Shape-In simulator using data from an RT-DC dataset file

    Example usage::

       shape-link run-simulator --features image,deform /path/to/data.rtdc
    """
    if features is not None:
        features = [f.strip() for f in features.split(",")]
    shapein_simulator.start_simulator(path, features)


@click.command()
@click.argument("path")
@click.option("--with-simulator", "-w",
              help="Run the Shape-In simulator in the background "
                   + "using the RT-DC dataset specified (used for testing).")
@click.option("--features", "-f",
              help="Comma-separated list of features to send by the "
                   + "Shape-In simulator; Defaults to all innate features. "
                   + "A list of valid feature names can be found in "
                   + "the dclab docs (Advanced Usage -> Notation).")
def run_plugin(path, with_simulator=None, features=None):
    """Run a Shape-Link plugin file

    Example usages::

        # run a plugin
        shape-link run-plugin plugins/slp_rolling_mean.py
        # run a plugin with a simulator thread (for plugin testing)
        shape-link run-plugin -w data.rtdc -f image,deform slp_rolling_mean.py


    """
    if with_simulator is not None:
        if features is not None:
            features = [f.strip() for f in features.split(",")]
        th = threading.Thread(target=shapein_simulator.start_simulator,
                              args=(with_simulator, features, 0))
        th.start()
    else:
        if features is None:
            raise ValueError("the '--features' option can only be used in "
                             + "conjunction with the '--with-simulator' flag!")
    path = pathlib.Path(path)
    # insert the plugin directory to sys.path so we can import it
    sys.path.insert(-1, str(path.parent))
    plugin = importlib.import_module(path.stem)
    # undo our path insertion
    sys.path.pop(0)
    # run the plugin
    click.secho("Running Shape-Link plugin '{}'...".format(path.stem),
                bold=True)
    p = plugin.info["class"]()
    while True:
        p.handle_messages()


main.add_command(run_simulator)
main.add_command(run_plugin)
