"""Command-line interface."""

import click


@click.command()
@click.version_option()
def main() -> None:
    """SSB Libtest3."""


if __name__ == "__main__":
    main(prog_name="ssb-libtest3")  # pragma: no cover
