#!/usr/bin/env python
"""
File: telomere_finder.py
Description: Telomere check.
CreateDate: 2025/3/3
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from io import StringIO, TextIOWrapper
from os.path import exists
from shutil import which
from pandas import read_table
from natsort import natsort_key
import click
from pybioinformatic import Fasta, TaskManager, dataframe_to_str, Displayer

displayer = Displayer(__file__.split('/')[-1], version='0.1.0')


def main(
    fasta_file: str,
    telomere_motif: str = 'CCCTAAA',
    telomere_range: int = 10000,
    min_interval: int = 0,
    max_interval: int = 100,
    output_file: TextIOWrapper = None
):
    seqkit = which('seqkit')
    bedtools = which('bedtools')
    samtools = which('samtools')
    tkm = TaskManager(num_processing=1)

    cmd = f'{samtools} faidx {fasta_file}'
    tkm.echo_and_exec_cmd(cmd=cmd, show_cmd=True, pipe=False)

    bed_a = r'''awk -F'\t' '{print $1"\t0\t%s\n"$1"\t"$2-%s"\t"$2}' %s''' % (
    telomere_range, telomere_range, f'{fasta_file}.fai')
    bed_b = f'{seqkit} locate -ip {telomere_motif} {fasta_file} --bed'
    cmd = f'{bedtools} intersect -a <({bed_a}) -b <({bed_b}) -c'
    stdout, stderr = tkm.echo_and_exec_cmd(cmd, show_cmd=True, pipe=True)
    if stderr:
        click.echo(stderr, err=True)
    count_df = read_table(StringIO(stdout), header=None, names=['Chromosome', 'Start', 'End', 'MotifCount'])
    count_df['Start'] += 1
    count_df = count_df.astype(str)
    count_df['ID'] = count_df.Chromosome + '_' + count_df.Start + '_' + count_df.End
    count_df.set_index(keys='ID', drop=True, inplace=True)

    pattern = '%s(?:[AGCT]{%s,%s}%s)*' % (telomere_motif, min_interval, max_interval, telomere_motif)
    l = []
    with Fasta(fasta_file) as fa:
        for nucl in fa.parse(parse_id=True):
            upstream_seq = nucl[:telomere_range]
            upstream_seq.id = f'{nucl.id}_1_{telomere_range}'
            downstream_seq = nucl[nucl.len - telomere_range:]
            downstream_seq.id = f'{nucl.id}_{nucl.len - telomere_range + 1}_{nucl.len}'
            upstream = upstream_seq.find_motif(pattern, only_forward=False, ignore_case=True)
            downstream = downstream_seq.find_motif(pattern, only_forward=False, ignore_case=True)
            telomere = upstream + '\n' + downstream
            l.append(telomere)
    loc_df = read_table(
        StringIO('\n'.join(l)),
        header=None,
        index_col=0,
        names=['ID', 'TelomereStart', 'TelomereEnd', 'Strand', 'Motif', 'Sequence']
    )
    loc_df.index = [i.split(' ')[0] for i in loc_df.index]
    loc_df.index.name = 'ID'

    merge_df = loc_df.join(other=count_df, how='left')
    merge_df['Start'] = merge_df['Start'].astype('Int32')
    merge_df['End'] = merge_df['End'].astype('Int32')
    merge_df['End'] = merge_df['Start'] + merge_df['TelomereEnd'] - 1
    merge_df['Start'] += merge_df['TelomereStart'] - 1
    merge_df['Start'] = merge_df['Start'].astype('Int32')
    merge_df['End'] = merge_df['End'].astype('Int32')
    merge_df['Length'] = merge_df.Sequence.str.len()
    merge_df['Length'] = merge_df['Length'].fillna(0)
    merge_df['Length'] = merge_df['Length'].astype('Int32')
    merge_df.reset_index(inplace=True)

    max_indices = merge_df.groupby(by='ID')['Length'].idxmax()
    filter_df = merge_df.loc[max_indices]
    filter_df = filter_df.loc[:, ['ID', 'Chromosome', 'Start', 'End', 'Strand', 'Motif', 'MotifCount', 'Length', 'Sequence']]
    filter_df = filter_df.astype(object)
    filter_df.fillna('NA', inplace=True)
    filter_df.sort_values(by='ID', key=natsort_key, inplace=True)
    filter_df = dataframe_to_str(filter_df, index=False, header=True)
    click.echo(filter_df, output_file)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('fasta_file', metavar='<fasta>', nargs=1, required=True)
@click.option('-r', '--region', 'telomere_range',
              metavar='<int>', type=int, default=10000, show_default=True,
              help='The range of telomeres at the both ends of chromosomes.')
@click.option('-m', '--telomere-motif', 'telomere_motif',
              metavar='<str>', default='CCCTAAA', show_default=True,
              help='Telomere motif sequence. Reference url for telomere motifs of different species: '
                   'https://telomerase.us/sequences_telomere.html.')
@click.option('-min', '--min-interval', 'min_interval',
              metavar='<int>', type=int, default=0, show_default=True,
              help='Minimum interval of telomere motif.')
@click.option('-max', '--max-interval', 'max_interval',
              metavar='<int>', type=int, default=100, show_default=True,
              help='Maximum interval of telomere motif.')
@click.option('-o', '--output-file', 'output_file',
              metavar='<file|stdout>', type=click.File('w'),
              help='Output file, stdout by default.')
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def run(fasta_file, telomere_range, telomere_motif, min_interval, max_interval, output_file):
    """
    Search telomere sequences whose motif is CCCTAAA/TTTAGGG ("-m, --telomere-motif" option),
    and the minimum interval of the motif is 0 bp ("-min, --min-interval" option),
    the maximum interval of the motif is 100 bp (-max, --max-interval),
    at the both ends of each chromosome within a 10kb range ("-r, --region" option).
    """
    main(
        fasta_file=fasta_file,
        telomere_motif=telomere_motif,
        telomere_range=telomere_range,
        min_interval=min_interval,
        max_interval=max_interval,
        output_file=output_file
    )


if __name__ == '__main__':
    run()
