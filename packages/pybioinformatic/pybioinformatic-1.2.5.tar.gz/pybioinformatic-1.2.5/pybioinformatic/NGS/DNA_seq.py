"""
File: DNA_seq.py
Description: DNA-seq analysis pipeline module.
CreateDate: 2025/4/18
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Dict
from os import makedirs
from os.path import abspath
from shutil import which
from pybioinformatic.NGS.base import NGSAnalyser
from pybioinformatic.util import FuncDict
from pybioinformatic.fasta import Fasta


class GatkSNPCalling(NGSAnalyser):
    """
    Variant calling pipeline using GATK tools.

    This class implements a complete pipeline for SNP calling using GATK's HaplotypeCaller, GenotypeGVCFs,
    and VariantFiltration tools. It handles the generation of GVCF and VCF files, applies filtering to
    variants, and integrates with other NGS analysis steps such as read alignment and quality control.

    Parameters:
        read1 (str): Path to the first paired-end FASTQ file.
        read2 (str): Path to the second paired-end FASTQ file.
        ref_genome (str): Path to the reference genome FASTA file.
        output_path (str): Directory where output files will be stored.
        num_threads (int): Number of threads to use for parallel processing. Default is 10.
        sample_name (str): Name of the sample being analyzed. If not provided, it will be inferred.
        exe_path_dict (Dict[str, str]): Dictionary mapping tool names to their executable paths.
    """
    def __init__(
        self,
        read1: str,
        read2: str,
        ref_genome: str,
        output_path: str,
        num_threads: int = 10,
        sample_name: str = None,
        exe_path_dict: Dict[str, str] = None
    ):
        super().__init__(read1, read2, ref_genome, output_path, num_threads, sample_name, exe_path_dict)
        self.variant_path = f'{self.output_path}/03.variant/{self.sample_name}'
        self.gvcf = f"{self.variant_path}/{self.bwa_mem_map30_markdup_bam.split('/')[-1]}.gvcf.gz"
        self.vcf = f"{self.variant_path}/{self.bwa_mem_map30_markdup_bam.split('/')[-1]}.vcf.gz"
        self.filtered_vcf = f"{self.variant_path}/{self.bwa_mem_map30_markdup_bam.split('/')[-1]}.filtered.vcf.gz"

    def run_HaplotypeCaller(
        self,
        bam_file: str = None,
        out_gvcf: str = None,
        **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        makedirs(self.variant_path, exist_ok=True)
        bam_file = abspath(bam_file) if bam_file else self.bwa_mem_map30_markdup_bam
        out_gvcf = abspath(out_gvcf) if out_gvcf else self.gvcf
        cmd = (f'{gatk} HaplotypeCaller '
               f'-ERC GVCF '
               f'-I {bam_file} '
               f'-R {self.ref_genome} '
               f'-O {out_gvcf}')
        return self.other_options(cmd, other_options) if other_options else cmd

    def run_GenotypeGVCFs(
        self,
        gvcf_file: str = None,
        out_vcf: str = None,
        **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        makedirs(self.variant_path, exist_ok=True)
        gvcf_file = abspath(gvcf_file) if gvcf_file else self.gvcf
        out_vcf = abspath(out_vcf) if out_vcf else self.vcf
        cmd = (
            f'{gatk} GenotypeGVCFs '
            f'-R {self.ref_genome} '
            f'-V {gvcf_file} '
            f'-O {out_vcf}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def run_VariantFiltration(
        self,
        filter_expression: str = 'QD < 2.0 || MQ < 40.0 || FS > 60.0 || SOR > 3.0',
        vcf_file: str = None,
        out_vcf: str = None,
        **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        makedirs(self.variant_path, exist_ok=True)
        vcf_file = abspath(vcf_file) if vcf_file else self.vcf
        out_vcf = abspath(out_vcf) if out_vcf else self.filtered_vcf
        cmd = (
            f'{gatk} VariantFiltration '
            f'--filter-name  "HARD_TO_VALIDATE" '
            f'--filter-expression "{filter_expression}" '
            f'-R {self.ref_genome} '
            f'-V {vcf_file} '
            f'-O {out_vcf}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def pipeline(
        self,
        fastp_options: Dict[str, str] = None,
        bwa_mem_options: Dict[str, str] = None,
        map_q: int = 30
    ) -> str:
        if fastp_options is None:
            fastp_options = {
                    '-j': f'{self.qc_path}/{self.sample_name}.fastp.json',
                    '-h': f'{self.qc_path}/{self.sample_name}.fastp.html'
                }
        if bwa_mem_options is None:
            bwa_mem_options = {}
        cmds = (
            f'{self.run_fastp(**fastp_options)}\n\n'
            f'{self.run_bwa_mem(**bwa_mem_options)}\n\n'
            f'{self.filter_reads_by_mapQ(bam_file=None, out_bam=None, map_q=map_q)}\n\n'
            f'{self.mark_duplicates()}\n\n'
            f'{self.stats_depth()}\n\n'
            f'{self.run_HaplotypeCaller()}\n\n'
            f'{self.run_GenotypeGVCFs()}\n\n'
            f'{self.run_VariantFiltration()}'
        )
        return cmds


class Macs2PeakCalling:
    """
    Manages the peak calling process using MACS2 for ChIP-Seq data analysis.
    """
    _exe_set = {'macs2'}

    def __init__(
        self,
        ChIP_read1: str,
        ChIP_read2: str,
        Input_read1: str,
        Input_read2: str,
        ref_genome: str,
        output_path: str,
        num_threads: int = 10,
        sample_name: str = None,
        exe_path_dict: Dict[str, str] = None
    ):
        self.ref_genome = abspath(ref_genome)
        self.sample_name = sample_name
        self.output_path = abspath(output_path)
        self.num_threads = num_threads
        if exe_path_dict is None:
            exe_path_dict = {}
        self.exe_path_dict = FuncDict(
            {
                k: which(v)
                for k, v in exe_path_dict.items()
                if k in self._exe_set and which(v) is not None
            }
        )

        self.ChIP_NGSAnalyser = NGSAnalyser(
            read1=abspath(ChIP_read1),
            read2=abspath(ChIP_read2),
            ref_genome=abspath(ref_genome),
            output_path=output_path,
            num_threads=num_threads,
            sample_name=sample_name,
            exe_path_dict=exe_path_dict
        )

        self.Input_NGSAnalyser = NGSAnalyser(
            read1=abspath(Input_read1),
            read2=abspath(Input_read2),
            ref_genome=abspath(ref_genome),
            output_path=output_path,
            num_threads=num_threads,
            sample_name=sample_name,
            exe_path_dict=exe_path_dict
        )

        self.qc_path = f'{self.output_path}/01.QC/{self.sample_name}'
        self.mapping_path = f'{self.output_path}/02.mapping/{self.sample_name}'
        self.peaks_path = f'{self.output_path}/03.peaks/{self.sample_name}'

        self.ChIP_read1_clean = f'{self.qc_path}/{self.sample_name}_ChIP_1_clean.fq.gz'
        self.ChIP_read2_clean = f'{self.qc_path}/{self.sample_name}_ChIP_2_clean.fq.gz'
        self.ChIP_fastp_json = f'{self.qc_path}/{self.sample_name}_ChIP.fastp.json'
        self.ChIP_fastp_html = f'{self.qc_path}/{self.sample_name}_ChIP.fastp.html'

        self.Input_read1_clean = f'{self.qc_path}/{self.sample_name}_Input_1_clean.fq.gz'
        self.Input_read2_clean = f'{self.qc_path}/{self.sample_name}_Input_2_clean.fq.gz'
        self.Input_fastp_json = f'{self.qc_path}/{self.sample_name}_Input.fastp.json'
        self.Input_fastp_html = f'{self.qc_path}/{self.sample_name}_Input.fastp.html'

        self.ChIP_bowtie2_markdup_bam = f'{self.mapping_path}/{self.sample_name}_ChIP.bt2.markdup.sort.bam'
        self.ChIP_bowtie2_markdup_filtered_bam = f'{self.mapping_path}/{self.sample_name}_ChIP.bt2.markdup.sort.filtered.bam'

        self.Input_bowtie2_markdup_bam = f'{self.mapping_path}/{self.sample_name}_Input.bt2.markdup.sort.bam'
        self.Input_bowtie2_markdup_filtered_bam = f'{self.mapping_path}/{self.sample_name}_Input.bt2.markdup.sort.filtered.bam'

    @staticmethod
    def other_options(cmd: str, other_options: dict):
        other_options = ' '.join([f'{k} {v}' for k, v in other_options.items()])
        cmd += f' {other_options}'
        return cmd

    def run_fastp(self, **other_options) -> str:
        ChIP_qc_other_options = {
                '-j': self.ChIP_fastp_json,
                '-h': self.ChIP_fastp_html
            }
        if other_options:
            ChIP_qc_other_options.update(other_options)
        ChIP_qc_cmd = self.ChIP_NGSAnalyser.run_fastp(
            read1_clean=self.ChIP_read1_clean,
            read2_clean=self.ChIP_read2_clean,
            **ChIP_qc_other_options
        )

        Input_qc_other_options = {
                '-j': self.Input_fastp_json,
                '-h': self.Input_fastp_html
            }
        if other_options:
            Input_qc_other_options.update(other_options)
        Input_qc_cmd = self.Input_NGSAnalyser.run_fastp(
            read1_clean=self.Input_read1_clean,
            read2_clean=self.Input_read2_clean,
            **Input_qc_other_options
        )

        cmd = f'{ChIP_qc_cmd}\n{Input_qc_cmd}'
        return cmd

    def run_bowtie2(self, **other_options) -> str:
        ChIP_mapping_cmd = self.ChIP_NGSAnalyser.run_bowtie2(
            read1_clean=self.ChIP_read1_clean,
            read2_clean=self.ChIP_read2_clean,
            markdup=True,
            out_bam=self.ChIP_bowtie2_markdup_bam,
            **other_options
        )
        Input_mapping_cmd = self.Input_NGSAnalyser.run_bowtie2(
            read1_clean=self.Input_read1_clean,
            read2_clean=self.Input_read2_clean,
            markdup=True,
            out_bam=self.Input_bowtie2_markdup_bam,
            **other_options
        )
        cmd = f'{ChIP_mapping_cmd}\n{Input_mapping_cmd}'
        return cmd

    def filter_reads(self, **other_options) -> str:
        ChIP_filter_cmd = self.ChIP_NGSAnalyser.filter_reads_by_samtools(
            bam_file=self.ChIP_bowtie2_markdup_bam,
            out_bam=self.ChIP_bowtie2_markdup_filtered_bam,
            **other_options
        )
        Input_filter_cmd = self.Input_NGSAnalyser.filter_reads_by_samtools(
            bam_file=self.Input_bowtie2_markdup_bam,
            out_bam=self.Input_bowtie2_markdup_filtered_bam,
            **other_options
        )
        cmd = f'{ChIP_filter_cmd}\n{Input_filter_cmd}'
        return cmd

    def run_macs2(
        self,
        genome_size: int = None,
        ChIP_bam: str = None,
        Input_bam: str = None,
        **other_options
    ) -> str:
        macs2 = which(self.exe_path_dict['macs2'])
        makedirs(self.peaks_path, exist_ok=True)
        ChIP_bam = abspath(ChIP_bam) if ChIP_bam else self.ChIP_bowtie2_markdup_filtered_bam
        Input_bam = abspath(Input_bam) if Input_bam else self.Input_bowtie2_markdup_filtered_bam
        if genome_size is None:
            with Fasta(self.ref_genome) as fa:
                genome_size = fa.get_size()
        cmd = (
            f'{macs2} callpeak '
            f'-t {ChIP_bam} '
            f'-c {Input_bam} '
            f'-g {genome_size} '
            f'-n {self.sample_name} '
            f'--outdir {self.peaks_path}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def pipeline(
        self,
        fastp_options: Dict[str, str] = None,
        bowtie2_options: Dict[str, str] = None,
        samtools_filter_reads_options: Dict[str, str] = None,
        macs2_callpeak_options: Dict[str, str] = None
    ) -> str:
        if fastp_options is None:
            fastp_options = {}

        if bowtie2_options is None:
            bowtie2_options = {
                '--very-sensitive': '',
                '--no-mixed': '',
                '--no-discordant': '',
                '-k': '10',
                '-tq': '',
                '-X': '1000',
                '-L': '25'
            }

        if samtools_filter_reads_options is None:
            samtools_filter_reads_options = {
                '-bF': '1804',
                '-f': '2',
                '-q': '20',
                '-e': "'[NM] <= 2'"
            }

        if macs2_callpeak_options is None:
            macs2_callpeak_options = {}

        cmds = (
            f'{self.run_fastp(**fastp_options)}\n\n'
            f'{self.run_bowtie2(**bowtie2_options)}\n\n'
            f'{self.filter_reads(**samtools_filter_reads_options)}\n\n'
            f'{self.run_macs2(**macs2_callpeak_options)}'
        )

        return cmds
