import click

from .app import run


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option("--account", "-a", type=click.STRING, help="Account id for trading", default=None, show_default=True)
@click.option(
    "--acc_file",
    "-f",
    default=".env",
    type=click.STRING,
    help="env file with live accounts configuration data",
    show_default=True,
)
@click.option(
    "--paths",
    "-p",
    multiple=True,
    default=["../", "~/projects/"],
    type=click.STRING,
    help="Live accounts configuration file",
)
# @click.option("--jupyter", "-j", is_flag=True, default=False, help="Run strategy in jupyter console", show_default=True)
@click.option("--testnet", "-t", is_flag=True, default=False, help="Use testnet for trading", show_default=True)
@click.option("--paper", "-p", is_flag=True, default=False, help="Use paper trading mode", show_default=True)
def main(filename: str, account: str, acc_file: str, paths: list, testnet: bool, paper: bool):
    run()


if __name__ == "__main__":
    main()
