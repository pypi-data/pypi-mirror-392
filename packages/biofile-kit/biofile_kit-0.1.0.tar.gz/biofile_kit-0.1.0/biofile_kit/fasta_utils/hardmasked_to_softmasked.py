#!/usr/bin/env python
"""
File: hardmasked_to_softmasked.py
Description: Change hard masked to soft masked.
CreateDate: 2025/7/9
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Union
from io import TextIOWrapper
import click
from pybioinformatic import Fasta, Sequence, Displayer

displayer = Displayer(__file__.split('/')[-1], version='0.0.0')


def main(
    no_masked: Union[str, TextIOWrapper],
    hard_masked: Union[str, TextIOWrapper],
    line_width: int,
    output_file: TextIOWrapper = None
):
    with Fasta(hard_masked) as fa1:
        for ret in fa1.hard_mask_to_soft_mask(non_masked=no_masked):
            ID, softmask_seq = ret
            seq = Sequence(seq_id=ID, sequence=softmask_seq)
            click.echo(seq.display_set(line_width), output_file)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('no_masked', nargs=1, metavar='<no masked fasta|stdin>', type=click.File('r'), required=True)
@click.argument('hard_masked', nargs=1, metavar='<hard masked fasta|stdin>', type=click.File('r'), required=True)
@click.option('-w', '--line-width', 'line_width',
              metavar='<int>', type=int, default=60, show_default=True,
              help='line width when outputting FASTA format (0 for no wrap).')
@click.option('-o', '--output-file', 'output_file',
              metavar='<file|stdout>', type=click.File('w'),
              help='Output file, stdout by default.')
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def run(no_masked, hard_masked, line_width, output_file):
    """Change hard masked to soft masked."""
    main(no_masked, hard_masked, line_width, output_file)


if __name__ == '__main__':
    run()
