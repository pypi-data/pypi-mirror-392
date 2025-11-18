from pybioinformatic.bed import Bed
from pybioinformatic.biomysql import BioMySQL
from pybioinformatic.blast import Blast
from pybioinformatic.decompressing_file import ungz
from pybioinformatic.fasta import Fasta
from pybioinformatic.fastq import Fastq
from pybioinformatic.genotype import GenoType
from pybioinformatic.gff import Gff
from pybioinformatic.gtf import Gtf
from pybioinformatic.sequence import Sequence, Nucleotide, Protein, Reads
from pybioinformatic.show_info import Displayer
from pybioinformatic.task_manager import TaskManager
from pybioinformatic.timer import Timer
from pybioinformatic.util import FuncDict, check_config
from pybioinformatic.vcf import VCF

from pybioinformatic.NGS import (
    check_cmds,
    check_R_packages,
    parse_sample_info,
    build_ref_index,
    GatkSNPCalling,
    Macs2PeakCalling,
    RNASeqAnalysisWithReference,
    LncRNAPredictor,
    LncRNATargetPredictor,
    LncRNAClassification
)

from pybioinformatic.biopandas import (
    display_set,
    read_file_as_df_from_stdin,
    merge_duplicate_indexes,
    filter_by_min_value,
    get_FPKM,
    get_TPM,
    dfs_to_excel,
    dataframe_to_str,
    interval_stat
)

from pybioinformatic.biomatplotlib import (
    set_custom_font,
    generate_unique_colors,
    format_xticks_by_kmg,
    rotate_ax_tick_labels
)

__version__ = '1.2.5'
__all__ = [
    'Bed',
    'Blast',
    'BioMySQL',
    'check_cmds',
    'check_R_packages',
    'parse_sample_info',
    'build_ref_index',
    'GatkSNPCalling',
    'Macs2PeakCalling',
    'RNASeqAnalysisWithReference',
    'LncRNAPredictor',
    'LncRNATargetPredictor',
    'LncRNAClassification',
    'ungz',
    'Fasta',
    'Fastq',
    'GenoType',
    'Gff',
    'Gtf',
    'Sequence',
    'Nucleotide',
    'Protein',
    'Reads',
    'Displayer',
    'Timer',
    'TaskManager',
    'VCF',
    'FuncDict',
    'check_config',
    'display_set',
    'read_file_as_df_from_stdin',
    'merge_duplicate_indexes',
    'filter_by_min_value',
    'get_TPM',
    'get_FPKM',
    'dfs_to_excel',
    'dataframe_to_str',
    'interval_stat',
    'generate_unique_colors',
    'set_custom_font',
    'format_xticks_by_kmg',
    'rotate_ax_tick_labels'
]
