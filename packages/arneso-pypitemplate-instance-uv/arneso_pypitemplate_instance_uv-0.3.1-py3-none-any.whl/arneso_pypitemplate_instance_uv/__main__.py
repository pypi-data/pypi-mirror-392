"""Command-line interface."""

import click


@click.command()
@click.version_option()
def main() -> None:
    """Arneso Pypitemplate Instance Uv."""


if __name__ == "__main__":
    main(prog_name="arneso-pypitemplate-instance-uv")  # pragma: no cover
