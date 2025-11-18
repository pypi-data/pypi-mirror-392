#!/usr/bin/env python
"""
File: vcf_tools.py
Description: Vcf file tools.
CreateDate: 2025/7/19
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from io import TextIOWrapper
import click
from pybioinformatic import Displayer
from biofile_kit.vcf_utils import vcf2gt, __version__

displayer = Displayer(__file__.split('/')[-1], version=__version__)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def vcf_tools():
    """Vcf file tools."""
    pass


vcf_tools.add_command(vcf2gt, 'vcf2gt')


if __name__ == '__main__':
    vcf_tools()
