#!/usr/bin/env python
"""
File: gt_kit.py
Description: GT file tools.
CreateDate: 2024/6/1
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
import click
from biofile_kit.gt_utils import gs, merge, stats, __version__
from pybioinformatic import Displayer
displayer = Displayer(__file__.split('/')[-1], version=__version__)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def gt_kit():
    """GT file tools."""
    pass


gt_kit.add_command(gs, 'gs')
gt_kit.add_command(merge, 'merge')
gt_kit.add_command(stats, 'stats')


if __name__ == '__main__':
    gt_kit()
