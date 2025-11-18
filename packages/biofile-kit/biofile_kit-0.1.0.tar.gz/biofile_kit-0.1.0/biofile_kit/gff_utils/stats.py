#!/usr/bin/env python
"""
File: stats.py
Description: Summarize the information of various features in the GFF file.
CreateDate: 2025/7/25
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Union
from io import TextIOWrapper
import click
from pybioinformatic import Gff, Displayer

displayer = Displayer(__file__.split('/')[-1], version='0.1.0')


def main(
    gff_file: Union[str, TextIOWrapper],
    output_file: TextIOWrapper = None
):
    with Gff(gff_file) as gff:
        for ret in gff.summary():
            click.echo(ret, output_file)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('gff_file', metavar='<gff|stdin>', type=click.File('r'), required=True)
@click.option('-o', '--output-file', 'output_file',
              metavar='<file|stdout>', type=click.File('w'),
              help='Output file, stdout by default.')
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def run(gff_file, output_file):
    """Summarize the information of various features in the GFF file."""
    main(gff_file, output_file)


if __name__ == '__main__':
    run()
