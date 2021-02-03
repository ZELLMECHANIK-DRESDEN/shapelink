import importlib
import pathlib
import sys

import click

from . import shapein_simulator


@click.group()
def main():
    pass


@click.command()
@click.argument("path")
def run_simulator(path):
    """Run the Shape-In simulator using data from an RT-DC dataset"""
    shapein_simulator.start_simulator(path)


@click.command()
@click.argument("path")
@click.option("--with-simulator",
              help="Run the Shape-In simulator in the background "
                   + "using the RT-DC dataset specified (used for testing).")
def run_plugin(path, with_simulator=None):
    """Run a Shape-Link plugin file"""
    if with_simulator is not None:
        raise NotImplementedError("TODO")
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
