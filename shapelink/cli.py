import click

from . import shapein_simulator


@click.group()
def main():
    pass


@click.command()
@click.argument('path')
def run_simulator(path):
    """Run a Shape-In simulator"""
    shapein_simulator.run(path)


main.add_command(run_simulator)
