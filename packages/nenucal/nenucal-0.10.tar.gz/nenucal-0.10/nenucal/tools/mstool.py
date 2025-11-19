"""
mstool

Command-line utilities for MeasurementSets.

Currently implemented:
- concat: concatenate multiple MS in time into a single MS using casacore TAQL.
"""

import os
import click
from casacore.tables import taql

from nenucal import __version__

t_dir = click.Path(exists=True, file_okay=False)


def build_taql_concat_query(msfiles, output_ms):
    """
    Build the TAQL query string:
      select from ['A.MS','B.MS',...] giving 'OUT.MS' AS PLAIN
    """
    quoted_inputs = ",".join(f"'{p}'" for p in msfiles)
    quoted_output = f"'{output_ms}'"
    return f"select from [{quoted_inputs}] giving {quoted_output} AS PLAIN"


@click.group()
@click.version_option(__version__)
def main():
    """
    MeasurementSet utilities.

    Example usage:
      mstool concat /net/node101/.../SW03_T001.MS /net/node102/.../SW03_T002.MS out_concat.MS
    """
    pass


@main.command("concat")
@click.argument("ms_ins", nargs=-1, type=t_dir)
@click.argument("ms_out")
def concat(ms_ins, ms_out):
    """
    Concatenate MeasurementSets in time using casacore TAQL.

    MS_INS: one or more input MeasurementSets (directories).
    MS_OUT: output MeasurementSet (path to new directory).
    """
    if len(ms_ins) < 2:
        raise click.ClickException("Need at least two MS inputs to concatenate.")

    out_abs = os.path.abspath(ms_out)
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)

    query = build_taql_concat_query(ms_ins, out_abs)
    click.echo("Running TAQL query:")
    click.echo(query)

    taql(query)

    if not os.path.isdir(out_abs):
        raise click.ClickException(f"TAQL finished but output MS not found: {out_abs}")

    click.echo(f"Done. Output MS: {out_abs}")


if __name__ == "__main__":
    main()
