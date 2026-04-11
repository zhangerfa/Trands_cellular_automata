"""Command-line interface for TCA."""

import click


@click.group()
def main() -> None:
    """Traffic Cellular Automata simulation framework CLI."""
    pass


if __name__ == "__main__":
    main()
