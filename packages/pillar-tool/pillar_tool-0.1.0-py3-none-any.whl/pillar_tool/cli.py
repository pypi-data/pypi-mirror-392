import logging
from pathlib import Path
from secrets import token_hex

import click

from pillar_tool import pillar
from pillar_tool.defaults import defaults
from pillar_tool.format import formatters


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option(
    "--file",
    type=Path,
    show_default=True,
    default=defaults.pillar,
    help="Path to pillar file",
)
@click.option(
    "--output",
    type=click.Choice(formatters.keys()),
    default=defaults.formatter,
    show_default=True,
    help="How to format output",
)
@click.pass_context
def cli(ctx: click.Context, verbose, output, **kwargs):
    # Logging is in multiples of 10, so we multiply our verbosity
    # by the same multiple
    logging.basicConfig(level=logging.WARNING - verbose * 10)
    ctx.obj = kwargs
    ctx.obj["formatter"] = formatters[output]


@cli.command()
@click.argument("key")
@click.pass_context
def get(ctx, key):
    try:
        data = pillar.load(path=ctx.obj["file"])
        result = pillar.get(
            data=data,
            lookup=key,
        )
    except KeyError:
        click.echo("Error looking up", key)
    else:
        if isinstance(result, dict):
            click.echo(ctx.obj["formatter"](result))
        else:
            click.echo(formatters["pprint"](result))


@cli.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx, key, value: str):
    if value.isnumeric():
        value = int(value)
    try:
        data = pillar.load(path=ctx.obj["file"])
        old_value, new_value = pillar.set(data=data, lookup=key, value=value)
        pillar.write(path=ctx.obj["file"], data=data)
    except KeyError:
        click.echo("Error looking up", key)
    else:
        click.echo(f"Updated {old_value!r} to {new_value!r}")


@cli.command()
@click.argument("key")
@click.option("--length", default=32)
@click.pass_context
def rotate(ctx, key, length):
    value = token_hex()[:length]
    ctx.invoke(set, key=key, value=value)


@cli.command()
@click.pass_context
def list(ctx):
    data = pillar.load(path=ctx.obj["file"])
    click.echo(ctx.obj["formatter"](data))


@cli.command()
def config():
    click.echo(f"pillar    {defaults.pillar}")
    click.echo(f"formatter {defaults.formatter}")


if __name__ == "__main__":
    cli(obj={})
