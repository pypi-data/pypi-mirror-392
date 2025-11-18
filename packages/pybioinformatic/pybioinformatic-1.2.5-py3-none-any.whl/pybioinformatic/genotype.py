"""
File: genotype.py
Description: Instantiate a GT file object.
CreateDate: 2023/10/26
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Union, List, Tuple
from typing_extensions import Literal
from functools import partial
from io import TextIOWrapper
from os import getcwd, name, makedirs
from os.path import abspath
from warnings import filterwarnings
from collections import defaultdict
from re import sub
from tqdm import tqdm
from natsort import natsort_key
from numpy import nan
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from pandas import Series, DataFrame, read_table, read_csv, read_excel, concat
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from seaborn import heatmap, clustermap
from click import echo
from pybioinformatic.task_manager import TaskManager
from pybioinformatic.biopandas import read_file_as_df_from_stdin, interval_stat
from pybioinformatic.biomatplotlib import set_custom_font
filterwarnings("ignore")


# =====================================================================================================================#
# NOTICE:                                                                                                              #
# The "__check_hom" and "__get_all_allele" functions cannot be defined in the "GenoType" class.                        #
# Because the "GenoType.parallel_stat_MHM" method runs with multiprocessing,                                           #
# the subprocess cannot call the private method of the "GenoType" class.                                               #
# =====================================================================================================================#
def __check_hom(row: Series) -> Series:
    """Check which samples are homozygous genotypes at specific loci."""
    genotype_set = {'AT', 'TA',
                    'AG', 'GA',
                    'AC', 'CA',
                    'GC', 'CG',
                    'GT', 'TG',
                    'CT', 'TC'}
    data = [str(value) not in genotype_set and '/' not in str(value) and str(value) != ''
            for value in row]
    return Series(data, row.index)


def __get_all_allele(row: Series) -> str:
    """Get all allele at specified loci."""
    all_allele = ''
    ref = row[0]
    for value in row[1:]:
        if '/' in str(value):
            left, right = str(value).split('/')[0], str(value).split('/')[1]
            if 'ins' in left:
                all_allele += 'I'
            elif 'del' in left:
                all_allele += 'D'
            elif left == '-':
                all_allele += ref[0]
            else:
                all_allele += left[0]
            if 'ins' in right:
                all_allele += 'I'
            elif 'del' in right:
                all_allele += 'D'
            elif right == '-':
                all_allele += ref[0]
            else:
                all_allele += right[0]
        elif 'ins' in str(value):
            all_allele += 'II'
        elif 'del' in str(value):
            all_allele += 'DD'
        elif str(value) == '-':
            all_allele += ref[0] * 2
        else:
            value = str(value).replace('*', 'U')
            all_allele += value
    return all_allele


def __allele_sort(allele: str) -> str:
    if '/' in allele:
        return '/'.join(sorted(allele.split('/')))
    elif 'ins' in allele or 'del' in allele:
        return allele
    else:
        return ''.join(sorted(allele))


def allele_sort(df: DataFrame) -> DataFrame:
    snp_ref = df.iloc[:, :4]
    sorted_allele = df.iloc[:, 4:].applymap(__allele_sort, na_action='ignore')
    df = snp_ref.join(sorted_allele)
    return df


def filter_mendelian_errors(df: DataFrame, parents: List[str], offsprings: List[str] = None) -> Tuple[DataFrame, DataFrame]:
    def get_offspring_probable_gt(row: Series) -> Series:
        if len(row) == 6:  # 提供了2个亲本
            row['probable_gt1'] = row.iloc[4][0] + row.iloc[5][0]
            row['probable_gt2'] = row.iloc[4][0] + row.iloc[5][1]
            row['probable_gt3'] = row.iloc[4][1] + row.iloc[5][0]
            row['probable_gt4'] = row.iloc[4][1] + row.iloc[5][1]
        else:  # 仅提供了1个亲本
            row['probable_gt1'] = row.iloc[4][0]
            row['probable_gt2'] = row.iloc[4][1]
        return row

    def filter_snp(row: Series) -> Series:
        num_correct_gt = len([i for i in row.index if 'probable_gt' in i])
        if num_correct_gt == 4:
            correct_gt = list(row[-num_correct_gt:])
            if all([gt in correct_gt for gt in row[4:-num_correct_gt]]):
                return row[:-num_correct_gt]
            else:
                return Series()
        elif num_correct_gt == 2:
            correct_gt = set(row[-num_correct_gt:])
            if all([set(gt) & correct_gt for gt in row[4:-num_correct_gt]]):
                return row[:-num_correct_gt]
            else:
                return Series()
        else:
            return Series()

    # 等位基因排序
    df = allele_sort(df)
    # 拆解亲本和子代基因型并过滤孟德尔错误
    loci_info = df.columns.tolist()[:4]
    samples = df.columns.tolist()[4:]
    if offsprings is None:  # 如果不提供子代样本名
        offsprings = list(set(samples) - set(parents))  # 默认将除了亲本以外的样本都视为子代
    offsprings.sort(key=natsort_key)
    if 0 < len(parents) <= 2:
        parents_gt = allele_sort(df.loc[:, loci_info + parents].apply(get_offspring_probable_gt, axis=1))
        num_probable_gt = len(parents) * 2
        offspring_gt = concat(
            objs=[
                df.loc[:, loci_info + offsprings],
                parents_gt.iloc[:, -num_probable_gt:]
            ],
            axis=1
        ).apply(filter_snp, axis=1).dropna()
    else:
        echo(f"\033[31mError: Invalid number of parents: {len(parents)}.\033[0m", err=True)
        exit()

    pass_df = df.loc[offspring_gt.index].reset_index(drop=True)  # 符合孟德尔遗传的位点
    filtered_df = df.loc[~df.index.isin(offspring_gt.index)].reset_index(drop=True)  # 不符合孟德尔遗传的位点

    return pass_df, filtered_df


def stat_MHM(df: DataFrame) -> DataFrame:
    """
    Calculate MissRate, HetRate, and MAF (MHM) from specified DataFrame.
    The top 4 columns of DataFrame must be SNP ID, chromosome, position, and reference sequence info respectively,
    and the header of DataFrame is not None.
    """
    snp_ref = df.iloc[:, :4]
    # Calculate MissRate
    sample_num = len(df.columns.tolist()) - 4
    df['MissRate(%)'] = df.isnull().sum(axis=1) / sample_num * 100
    # Calculate HetRate
    df.fillna('', inplace=True)  # fill NA
    df['HetRate(%)'] = df.iloc[:, 4:-1].apply(lambda row: (1 - __check_hom(row).sum() / (row != '').sum()) * 100, axis=1)
    # Calculate MAF
    df['all_gt'] = df.iloc[:, 3:-2].apply(lambda row: __get_all_allele(row), axis=1)
    df['total'] = df['all_gt'].apply(len)
    df['A'] = df['all_gt'].str.count('A') / df['total']
    df['G'] = df['all_gt'].str.count('G') / df['total']
    df['C'] = df['all_gt'].str.count('C') / df['total']
    df['T'] = df['all_gt'].str.count('T') / df['total']
    df['D'] = df['all_gt'].str.count('D') / df['total']
    df['I'] = df['all_gt'].str.count('I') / df['total']
    df['U'] = df['all_gt'].str.count('U') / df['total']
    df['MAF'] = df.loc[:, ['A', 'G', 'C', 'T', 'D', 'I', 'U']].apply(lambda row: sorted(row, reverse=True)[1], axis=1)
    # Output results
    df = df.loc[:, ['MissRate(%)', 'HetRate(%)', 'MAF']]
    merge = snp_ref.join(df)
    return merge


def genotype_phenotype_analysis(
    genotype: Series,
    trait: DataFrame,
    trait_name: str,
    mark_sample_list: list = None,
    out_path: str = '.'
) -> Series:
    makedirs(out_path, exist_ok=True)
    site_id = genotype['ID']
    df = genotype[4:].to_frame('Genotype')
    df = concat([df, trait[trait_name]], axis=1)
    df.index.name = 'Sample'

    # 使用statsmodels进行ANOVA
    model = ols(f'{trait_name} ~ C(Genotype)', data=df).fit()
    anova_results = anova_lm(model)
    F = anova_results['F'][0]
    p_value = anova_results['PR(>F)'][0]

    i = 0
    x_tick_labels = []
    for gt, grouped_df in df.groupby('Genotype'):
        df.loc[df.Genotype == gt, 'x'] = i

        plt.boxplot(
            x=grouped_df[trait_name],
            positions=[i],
            medianprops={'color': 'black'}
        )

        plt.scatter(
            x=[i for _ in range(len(grouped_df[trait_name]))],
            y=grouped_df[trait_name]
        )

        x_tick_labels.append(gt)
        i += 1

    if mark_sample_list:
        mark_sample_df = df.loc[mark_sample_list].sort_values(by=trait_name)
        mark_sample_df['Diff'] = mark_sample_df[trait_name].diff()
        mark_sample_df.fillna(0, inplace=True)
        mark_sample_df.loc[mark_sample_df.Diff < 1, 'dy'] = mark_sample_df['Diff'].max() / 10
        mark_sample_df.loc[mark_sample_df.Diff >= 1, 'dy'] = -mark_sample_df['Diff'].max() / 10
        plt.scatter(
            x='x',
            y=trait_name,
            c='r',
            data=mark_sample_df
        )

        for sample in mark_sample_list:
            arrow_x = mark_sample_df.loc[sample]['x']
            arrow_y = mark_sample_df.loc[sample][trait_name]
            dy = mark_sample_df.loc[sample]['dy']
            plt.arrow(
                x=arrow_x,
                y=arrow_y,
                dx=0.3,
                dy=dy,
                linestyle='--',
                linewidth=0.6,
                color='r',
                width=0,
                head_width=0
            )

            plt.text(
                x=arrow_x + 0.31,
                y=arrow_y + dy,
                s=sample,
                fontsize=6,
                color='r'
            )

    plt.xticks(range(len(x_tick_labels)), x_tick_labels)
    title = plt.title(f'site: {site_id}\ntrait: {trait_name}\nF: {F:.3f}  p value: {p_value:.4f}')
    title.set_linespacing(1.5)  # 1.5倍行间距
    plt.savefig(f'{out_path}/{site_id}_{trait_name}.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'{out_path}/{site_id}_{trait_name}.pdf', dpi=150, bbox_inches='tight')
    plt.cla()

    result = Series(
        data=[site_id, trait_name, F, p_value],
        index=['ID', 'Trait', 'F', 'P_value']
    )
    return result


class GenoType:
    """
    Standard genotype file object.
    """

    def __init__(self, path: Union[str, TextIOWrapper]):
        self.name = abspath(path) if isinstance(path, str) else abspath(path.name)
        self.__open = open(path) if isinstance(path, str) else path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.__open.close()
        except AttributeError:
            pass

    def to_dataframe(
        self,
        sheet: Union[str, int, List[Union[str, int]]] = 0,
        index_col: Union[int, str] = None,
        sort_allele: bool = True
    ) -> DataFrame:
        try:  # read from text file
            if 'gz' in self.name:
                df = read_csv(self.name, sep='\t', index_col=index_col)
            else:
                df = read_csv(self.__open, sep='\t', index_col=index_col)
        except UnicodeDecodeError:  # read from Excel file
            df = read_excel(self.name, sheet, index_col=index_col)
        if index_col:
            df.sort_index(key=natsort_key, inplace=True)  # sort by index
        else:
            df.sort_values([df.columns[1], df.columns[2]], key=natsort_key, inplace=True)  # sort by values
        if sort_allele:
            df = allele_sort(df)
        return df

    def to_dataframes(
        self,
        sheet: Union[str, int, List[Union[str, int]]] = 0,
        index_col: Union[int, str] = None,
        chunk_size: int = 10000
    ) -> DataFrame:
        if 'stdin' in self.name:  # read from stdin
            dfs = read_file_as_df_from_stdin(chunk_size=chunk_size, index_col=index_col)
        elif self.name.endswith('gz'):  # read from compressed text (xx.gz) file
            dfs = read_table(self.name, chunksize=chunk_size, index_col=index_col)
        else:
            try:  # read from text file
                dfs = read_table(self.__open, chunksize=chunk_size, index_col=index_col)
            except UnicodeDecodeError:  # read from Excel file
                echo('\033[33mWarning: Excel file cannot be processed in chunks.\033[0m', err=True)
                return self.to_dataframe(sheet, index_col)
        return dfs

    def filter_mendelian_errors(
        self,
        parents: List[str],
        offsprings: List[str] = None,
        num_processing: int = 1
    ) -> Tuple[DataFrame, DataFrame]:
        dfs = self.to_dataframes()
        params = ((df, parents, offsprings) for df in dfs)  # Index of DataFrame is 0, 1, 2, ...
        tkm = TaskManager(num_processing=num_processing, params=params)
        rets = tkm.parallel_run_func(filter_mendelian_errors)
        t = [i.get() for i in rets]  # [(pass_df, filtered_df), (), ...]

        pass_dfs = [i[0] for i in t]
        pass_df = concat(pass_dfs)
        pass_df.sort_values(pass_df.columns.tolist()[1:3], inplace=True, key=natsort_key)
        pass_df.reset_index(drop=True, inplace=True)

        filtered_dfs = [i[1] for i in t]
        filtered_df = concat(filtered_dfs)
        filtered_df.sort_values(filtered_df.columns.tolist()[1:3], inplace=True, key=natsort_key)
        filtered_df.reset_index(drop=True, inplace=True)

        return pass_df, filtered_df

    def filter_allele(self, min_alleles: int, max_alleles: int) -> DataFrame:
        df = self.to_dataframe(index_col=0)
        sub_df = df.iloc[:, 3:]
        combined = (
            sub_df
            .fillna('')  # 将NaN替换为空字符串
            .stack()  # 展开为多级索引Series
            .groupby(level=0)  # 按原始行索引分组
            .agg(''.join)  # 连接所有字符串
        )
        result = (
            combined
            .apply(lambda s: ''.join(sorted(set(s))))  # 去重并排序
            .rename('combined')  # 重命名结果列
        )
        df = concat([df, result], axis=1)
        columns = df.columns.tolist()[:-1]
        filtered_df = df.loc[(df.combined.str.len() <= max_alleles) & (df.combined.str.len() >= min_alleles), columns]
        filtered_df.sort_index(inplace=True)
        return filtered_df

    def parallel_stat_MHM(self, num_processing: int = 1) -> DataFrame:
        """Calculate the MissRate, HetRate and MAF (MHM) of SNP sites from GT files parallely."""
        dfs = self.to_dataframes()
        params = ((df,) for df in dfs)  # Index of DataFrame is 0, 1, 2, ...
        tkm = TaskManager(num_processing=num_processing, params=params)
        ret = tkm.parallel_run_func(stat_MHM)
        stat_dfs = [i.get() for i in ret]
        # Merge results of each multiprocessing
        stat_df = concat(stat_dfs)
        stat_df.sort_values(stat_df.columns.tolist()[1:3], inplace=True, key=natsort_key)
        stat_df.fillna(0, inplace=True)
        return stat_df

    def merge(
        self, other,
        how: Literal['inner', 'outer'],
        sheet1: Union[str, int, List[Union[str, int]]] = None,
        sheet2: Union[str, int, List[Union[str, int]]] = None
    ) -> DataFrame:
        df1 = self.to_dataframe(sheet=sheet1)
        df1[df1.columns[1]] = df1[df1.columns[1]].astype(str)
        df1[df1.columns[2]] = df1[df1.columns[2]].astype(str)
        df1['tmp'] = df1[df1.columns[1]] + '_' + df1[df1.columns[2]] + '_' + df1[df1.columns[3]]
        df1.set_index('tmp', drop=True, inplace=True)
        df1 = df1.iloc[:, 4:]

        df2 = other.to_dataframe(sheet=sheet2)
        df2[df2.columns[1]] = df2[df2.columns[1]].astype(str)
        df2[df2.columns[2]] = df2[df2.columns[2]].astype(str)
        df2['tmp'] = df2[df2.columns[1]] + '_' + df2[df2.columns[2]] + '_' + df2[df2.columns[3]]
        df2.set_index('tmp', drop=True, inplace=True)
        df2 = df2.iloc[:, 4:]

        merge = df1.join(other=df2, how=how)
        samples = merge.columns.tolist()
        samples.sort(key=natsort_key)
        merge = merge.loc[:, samples]
        merge.insert(0, 'Chr', [i.split('_')[0] for i in merge.index.tolist()])
        merge.insert(1, 'Pos', [i.split('_')[1] for i in merge.index.tolist()])
        merge.insert(2, 'Ref', [i.split('_')[2] for i in merge.index.tolist()])
        merge.index.name = 'ID'
        merge.rename(index=lambda i: '_'.join(i.split('_')[:2]), inplace=True)
        merge.fillna('NA', inplace=True)
        merge.sort_index(key=natsort_key, inplace=True)
        return merge

    @staticmethod
    def __draw_gs_heatmap(
        consistency_df: DataFrame,
        cmap: str = "crest",
        output_path: str = getcwd(),
        font_name: str = 'Arial'
    ) -> None:
        # Set font and dpi.
        dpi = 300
        if len(consistency_df) <= 40:
            font_size = 8
        elif 40 < len(consistency_df) <= 100:
            font_size = 6
        elif 100 < len(consistency_df) <= 150:
            font_size = 4
        else:
            font_size = 1
            dpi = 1000
        if name == 'nt':
            plt.rcParams['font.family'] = font_name
        else:
            set_custom_font(font_name)
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['font.size'] = font_size
        # Set figure attributions.
        plt.figure(figsize=(15, 10))
        # Plot heatmap.
        ax = heatmap(
            data=consistency_df,
            cmap=cmap,
            linecolor='w',
            linewidths=0.5,
            xticklabels=True,
            yticklabels=True,
            cbar_kws={'shrink': 0.4}
        )
        plt.tick_params('both', length=0)  # Set scale length.
        # Set color bar ticks and ticks label.
        min_gs = consistency_df.min(numeric_only=True).min() + 1
        max_gs = consistency_df.max(numeric_only=True).max()
        min_value = int(min_gs)
        max_value = int(max_gs)
        step = int((max_value - min_value) / 10)
        step = 1 if step == 0 else step
        cbar = ax.collections[0].colorbar
        cbar_ticks = [i for i in range(min_value, max_value + step, step) if i <= 100]
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels(cbar_ticks, fontsize=8)
        cbar.ax.tick_params(width=0.3)
        # # Save figure.
        plt.savefig(f'{output_path}/Consistency.heatmap.pdf', bbox_inches='tight', dpi=dpi)

    @staticmethod
    def __draw_gs_cluster_heatmap(
        consistency_df: DataFrame,
        cmap: str = "vlag",
        output_path: str = getcwd(),
        font_name: str = 'Arial'
    ) -> None:
        dpi = 300
        if len(consistency_df) <= 40:
            font_size = 8
        elif 40 < len(consistency_df) <= 100:
            font_size = 6
        elif 100 < len(consistency_df) <= 150:
            font_size = 4
        else:
            font_size = 1
            dpi = 1000
        if name == 'nt':
            plt.rcParams['font.family'] = font_name
        else:
            set_custom_font(font_name)
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['font.size'] = font_size
        for i in range(len(consistency_df.columns)):
            consistency_df.iloc[i, i] = 100
            for j in range(i + 1, len(consistency_df.columns)):
                consistency_df.iloc[i, j] = consistency_df.iloc[j, i]
        ax = clustermap(
            data=consistency_df,
            cmap=cmap,
            xticklabels=True    ,
            yticklabels=True,
            dendrogram_ratio=(0.1, 0.1),  # tree diagram percentage
            cbar_pos=(0.999, 0.6, 0.03, 0.3)  # cbar pos
        )
        ax.savefig(f'{output_path}/Consistency.cluster.heatmap.pdf', bbox_inches='tight', dpi=dpi)

    def self_compare(
        self, other,
        sheet1: Union[str, int, List[Union[str, int]]] = None,
        sheet2: Union[str, int, List[Union[str, int]]] = None,
        output_path: str = getcwd()
    ) -> None:
        """Genotype consistency of different test batches in a single sample."""
        # Read in gt.
        df1 = self.to_dataframe(sheet1, index_col=0, sort_allele=False)
        df1[df1.columns[0]] = df1[df1.columns[0]].astype(str)
        df1[df1.columns[1]] = df1[df1.columns[1]].astype(str)
        df1['tmp'] = df1[df1.columns[0]] + '_' + df1[df1.columns[1]] + '_' + df1[df1.columns[2]]
        df1.set_index('tmp', drop=True, inplace=True)
        df2 = other.to_dataframe(sheet2, index_col=0, sort_allele=False)
        df2[df2.columns[0]] = df2[df2.columns[0]].astype(str)
        df2[df2.columns[1]] = df2[df2.columns[1]].astype(str)
        df2['tmp'] = df2[df2.columns[0]] + '_' + df2[df2.columns[1]] + '_' + df2[df2.columns[2]]
        df2.set_index('tmp', drop=True, inplace=True)
        # Check whether the two GT files contain the same loci.
        if df1.index.tolist() != df2.index.tolist():
            echo('\033[31mError: The two GT file loci to be compared are inconsistent.\033[0m', err=True)
            exit()
        # Calculate genotype consistency of each sample under different test batches.
        samples = set(df1.columns[3:]) & set(df2.columns[3:])
        data = []
        with tqdm(total=len(samples), unit='sample') as pbar:
            for sample in samples:
                NA_site = set(df1[sample][df1[sample].isnull()].index) | set(df2[sample][df2[sample].isnull()].index)
                NA_num = len(NA_site)
                series1 = df1[sample][~df1[sample].isnull()]
                series2 = df2[sample][~df2[sample].isnull()]
                IdenticalCount = series1.eq(series2).sum()
                TotalCount = len(df1) - NA_num
                GS = IdenticalCount / TotalCount * 100
                data.append([sample, IdenticalCount, NA_num, TotalCount, GS])
                pbar.update(1)
        bins = range(0, 105, 5)  # Set the consistency statistics interval.
        sample_consistency = DataFrame(data, columns=['SampleName', 'IdenticalCount', 'NaCount', 'TotalCount', 'GS(%)'])
        sample_consistency.sort_values('SampleName', key=natsort_key, inplace=True)
        sample_consistency.fillna(0.000, inplace=True)
        interval_stat_df = interval_stat(ser=sample_consistency['GS(%)'], bins=bins, precision=0, name='Count')
        # Write results to output file.
        sample_consistency.to_csv(f'{output_path}/Sample.consistency.xls', sep='\t', index=False)
        interval_stat_df.to_csv(f'{output_path}/Interval.stat.xls', sep='\t', header=False)

    def compare(
        self, other,
        sheet1: Union[str, int, List[Union[str, int]]] = None,
        sheet2: Union[str, int, List[Union[str, int]]] = None,
        cmap: str = "crest",
        output_path: str = getcwd(),
        font_name: str = 'Arial'
    ) -> None:
        """
        Calculate genotype consistency.
        """
        # Step1: Read GT file as DataFrame.
        df1 = self.to_dataframe(sheet1)  # index = 0, 1, 2, ...
        df2 = other.to_dataframe(sheet2)  # index = 0, 1, 2, ...
        # Step2: Select the site intersection of two GT files.
        left_on = df1.columns[0]
        right_on = df2.columns[0]
        merge = df1.merge(df2, left_on=left_on,  # index = 0, 1, 2, ...
                          right_on=right_on)  # Avoid inconsistency between the two GT file ID fields
        # Step3: Calculate genotype consistency.
        df1_sample_num = len(df1.columns.tolist()) - 4
        left_sample_range = list(range(4, 4 + df1_sample_num))
        if df1.columns[0] == df2.columns[0]:
            right_sample_range = list(range(len(df1.columns) + 3, len(merge.columns)))
        else:
            right_sample_range = list(range(len(df1.columns) + 4, len(merge.columns)))
        consistency_df = DataFrame()
        sample_pair = set()
        data = []
        with tqdm(total=len(left_sample_range), unit='sample') as pbar:  # Show process bar
            for index1 in left_sample_range:
                gt1 = merge.iloc[:, index1]
                gt1_NA = set(gt1[gt1.isnull()].index)
                gt1.name = sub(r'_x\b', '', gt1.name)
                pbar.set_description(f'Processing {gt1.name}')
                for index2 in right_sample_range:
                    gt2 = merge.iloc[:, index2]
                    gt2_NA = set(gt1[gt2.isnull()].index)
                    NA_site_index = gt1_NA | gt2_NA
                    NA_num = len(NA_site_index)
                    TotalCount = len(merge) - NA_num
                    gt2.name = sub(r'_y\b', '', gt2.name)
                    gt1 = gt1[~gt1.isnull()]
                    gt2 = gt2[~gt2.isnull()]
                    IdenticalCount = gt1.eq(gt2).sum()
                    GS = 0.00 if TotalCount == 0 else '%.2f' % (IdenticalCount / TotalCount * 100)
                    data.append([gt1.name, gt2.name, IdenticalCount, NA_num, TotalCount, GS])
                    if gt1.name != gt2.name:
                        if (f'{gt1.name}-{gt2.name}' not in sample_pair) and \
                                (f'{gt2.name}-{gt1.name}' not in sample_pair):
                            consistency_df.loc[gt2.name, gt1.name] = GS
                            sample_pair.add(f'{gt1.name}-{gt2.name}')
                            sample_pair.add(f'{gt2.name}-{gt1.name}')
                    else:
                        consistency_df.loc[gt1.name, gt2.name] = ''
                pbar.update(1)
        header = ['Sample1', 'Sample2', 'IdenticalCount', 'NaCount', 'TotalCount', 'GS(%)']
        fmt1 = DataFrame(data, columns=header)
        fmt1.sort_values(['Sample1', 'GS(%)', 'Sample2'], key=natsort_key, inplace=True, ascending=[True, False, True])
        fmt1.to_csv(f'{output_path}/Sample.consistency.fmt1.xls', sep='\t', index=False)
        # Step4: Draw consistency heatmap.
        consistency_df.to_csv(f'{output_path}/Sample.consistency.fmt2.xls', sep='\t', na_rep='')
        self.__draw_gs_heatmap(
            consistency_df=read_table(f'{output_path}/Sample.consistency.fmt2.xls', index_col=0),
            cmap=cmap,
            output_path=output_path,
            font_name=font_name
        )
        # Step5: Draw consistency cluster heatmap.
        self.__draw_gs_cluster_heatmap(
            consistency_df=read_table(f'{output_path}/Sample.consistency.fmt2.xls', index_col=0),
            cmap=cmap,
            output_path=output_path,
            font_name=font_name
        )
        # Step6: Output GT file of test sample.
        right_sample_range.insert(0, 0)  # Only output site ID
        right_sample_range.insert(1, len(df1.columns) + 2)
        test_sample_gt_df = merge.iloc[:, right_sample_range]
        test_sample_gt_df.rename(columns=lambda i: sub(r'_[xy]\b', '', str(i)), inplace=True)
        test_sample_gt_df.sort_values(merge.columns[0], key=natsort_key, inplace=True)
        test_sample_gt_df.to_csv(f'{output_path}/Compare.GT.xls', sep='\t', index=False, na_rep='NA')

    def find_min_distinguishing_snps(self) -> DataFrame:
        """
        Find the smallest set of SNP loci that can distinguish all samples.
        """
        df = self.to_dataframe(index_col=0, sort_allele=True)
        non_sample_columns = ['Chrom', 'Position', 'Ref']
        sample_columns = [col for col in df.columns if col not in non_sample_columns]
        # 只保留样本列
        genotype_matrix = df[sample_columns].values

        # 初始化等价类（初始所有样本在同一类）
        equivalence_classes = [set(range(len(sample_columns)))]
        selected_snps = []

        # 当存在包含多个样本的等价类时继续
        while any(len(eq) > 1 for eq in equivalence_classes):
            best_snp = None
            best_gain = -1
            best_new_classes = None

            # 遍历所有SNP位点
            for snp_idx in range(len(df)):
                if snp_idx in selected_snps:
                    continue

                # 创建新的等价类划分
                new_classes = []

                # 对每个现有等价类进行细分
                for eq in equivalence_classes:
                    # 按当前SNP的基因型细分
                    subgroups = defaultdict(set)
                    for sample_idx in eq:
                        genotype = genotype_matrix[snp_idx, sample_idx]
                        subgroups[genotype].add(sample_idx)

                    # 添加非空子组
                    for subgroup in subgroups.values():
                        if subgroup:
                            new_classes.append(subgroup)

                # 计算信息增益（减少的未区分样本对数）
                current_undistinguished = sum(len(eq) * (len(eq) - 1) // 2 for eq in equivalence_classes)
                new_undistinguished = sum(len(eq) * (len(eq) - 1) // 2 for eq in new_classes)
                gain = current_undistinguished - new_undistinguished

                # 选择增益最大的SNP
                if gain > best_gain:
                    best_gain = gain
                    best_snp = snp_idx
                    best_new_classes = new_classes

            # 如果没有找到增益的SNP，停止
            if best_gain <= 0:
                break

            # 添加最佳SNP并更新等价类
            selected_snps.append(best_snp)
            equivalence_classes = best_new_classes

        min_snps = df.iloc[selected_snps][non_sample_columns + sample_columns]
        min_snps.sort_index(key=natsort_key, inplace=True)
        return min_snps

    def draw_genotype_heatmap(
        self,
        genotype_colors: List[str] = None,
        font_name: str = 'Arial',
        out_file: str = 'genotype_heatmap.pdf'
    ) -> None:
        if genotype_colors is None:
            genotype_colors = ['#2c7bb6', '#ffffbf', '#d7191c']
        plt.rcParams['pdf.fonttype'] = 42
        if name == 'nt':
            plt.rcParams['font.family'] = font_name
        else:
            set_custom_font(font_name)

        # 1. 读取基因型数据
        df = self.to_dataframe(index_col=0, sort_allele=True)

        # 2. 数据预处理
        # 提取样本列（排除元数据列）
        df.sort_index(key=natsort_key, inplace=True)
        sorted_samples = df.columns.tolist()[3:]
        sorted_samples.sort(key=natsort_key)
        df = df.loc[:, ['Chrom', 'Position', 'Ref'] + sorted_samples]
        sample_columns = [col for col in df.columns if col not in ['Chrom', 'Position', 'Ref']]
        # 创建基因型矩阵
        genotype_matrix = df[sample_columns]

        # 3. 基因型编码（将基因型转换为数值）
        def encode_genotype(gt, ref):
            """将基因型编码为数值"""
            if gt == ref + ref:  # 参考纯合子
                return 0
            elif ref in gt and len(set(gt)) == 2:  # 杂合子
                return 1
            elif ref not in gt:  # 变异纯合子
                return 2
            else:  # 缺失或未知
                return nan

        # 创建编码矩阵
        encoded_matrix = DataFrame(index=genotype_matrix.index, columns=genotype_matrix.columns)

        for idx in genotype_matrix.index:
            ref = df.loc[idx, 'Ref']  # 获取当前SNP的参考等位基因
            for col in genotype_matrix.columns:
                gt = genotype_matrix.loc[idx, col]
                encoded_matrix.loc[idx, col] = encode_genotype(gt, ref)

        encoded_matrix = encoded_matrix.astype(float)
        if len(sample_columns)  > len(df) and len(sample_columns) > 50:
            encoded_matrix = encoded_matrix.T  # 转置矩阵，使样本在Y轴

        # 4. 创建自定义颜色映射
        genotype_cmap = ListedColormap(genotype_colors)

        # 5. 使用Seaborn绘制静态热图并添加基因型文本
        plt.figure(figsize=(10, 8))  # 增大图形尺寸以容纳文本

        # 创建热图
        ax = heatmap(
            encoded_matrix,
            cmap=genotype_cmap,
            cbar_kws={
                'ticks': [-0.5, 0.5, 1.5],
                'boundaries': [-1, 0, 1, 2],
                'shrink': 0.2,  # 缩小比例 (0.0-1.0)
                'aspect': 15  # 颜色条宽高比 (宽度/高度)
            },
            linewidths=0.5,
            linecolor='lightgray',
            vmin=-0.5,
            vmax=2.5,
            annot=False,  # 不使用seaborn的注释，而是自定义
            fmt="",
            square=True
        )

        # 设置颜色条标签
        cbar = ax.collections[0].colorbar
        cbar.set_ticklabels(['Ref Homo', 'Hetero', 'Alt Homo'], fontsize=8)
        # cbar.set_label('Genotype Category', fontsize=12)

        # 添加基因型文本
        if len(sample_columns)  > len(df) and len(sample_columns) > 50:
        # 注意：由于我们转置了矩阵，需要调整索引
            for i, sample in enumerate(encoded_matrix.index):  # i: 样本索引 (Y轴)
                for j, snp in enumerate(encoded_matrix.columns):  # j: SNP索引 (X轴)
                    # 获取原始基因型
                    gt = genotype_matrix.loc[snp, sample]  # 注意索引顺序

                    # 获取当前单元格的编码值
                    cell_val = encoded_matrix.iloc[i, j]

                    # 根据背景色选择文本颜色
                    # 黄色背景用黑色文本，其他用白色文本
                    text_color = 'black' if cell_val == 1 else 'white'

                    # 添加文本
                    plt.text(
                        j + 0.5,  # x位置（单元格中心）
                        i + 0.5,  # y位置（单元格中心）
                        gt,  # 基因型文本
                        ha='center',
                        va='center',
                        color=text_color,
                        fontsize=6
                    )
        else:
            # 添加基因型文本（不转置版本）
            # i: SNP索引 (行/Y轴), j: 样本索引 (列/X轴)
            for i, snp in enumerate(encoded_matrix.index):  # 遍历每个SNP（行）
                for j, sample in enumerate(encoded_matrix.columns):  # 遍历每个样本（列）
                    # 获取原始基因型
                    gt = genotype_matrix.loc[snp, sample]

                    # 获取当前单元格的编码值
                    cell_val = encoded_matrix.iloc[i, j]

                    # 根据背景色选择文本颜色
                    # 黄色背景用黑色文本，其他用白色文本
                    text_color = 'black' if cell_val == 1 else 'white'

                    # 添加文本
                    plt.text(
                        j + 0.5,  # x位置（单元格中心，列位置）
                        i + 0.5,  # y位置（单元格中心，行位置）
                        gt,  # 基因型文本
                        ha='center',
                        va='center',
                        color=text_color,
                        fontsize=6
                    )

        # 添加标题和标签
        if len(sample_columns)  > len(df) and len(sample_columns) > 50:
            plt.xlabel('SNP Positions', fontsize=10, labelpad=15)
            plt.ylabel('Samples', fontsize=10, labelpad=15)
        else:
            plt.xlabel('Samples', fontsize=10, labelpad=15)
            plt.ylabel('SNP Positions', fontsize=10, labelpad=15)

        # 旋转SNP标签以提高可读性
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.yticks(fontsize=8)

        plt.tight_layout()  # 优化布局
        plt.savefig(out_file, dpi=300, bbox_inches='tight')

    def filter_multi_group_genotypes(self, groups: List[List[str]]) -> DataFrame:
        """
        Based on the provided sample classification information,
        select the loci where the genotypes within the group are consistent
        but the genotypes between groups are not.
        """
        df = self.to_dataframe(index_col=0, sort_allele=True)
        # 提取所有列并处理缺失值
        all_columns = [col for group in groups for col in group]
        df_clean = df.dropna(subset=all_columns).copy()

        # 检查每个分组内部一致性
        group_conditions = []
        for group in groups:
            group_cond = df_clean[group].nunique(axis=1) == 1
            group_conditions.append(group_cond)

        all_group_cond = concat(group_conditions, axis=1).all(axis=1)

        # 为每组创建代表值列
        rep_cols = []
        for i, group in enumerate(groups):
            rep_col = f'rep_{i}'
            df_clean[rep_col] = df_clean[group[0]]
            rep_cols.append(rep_col)

        # 严格检查组间互异性（两两比较）
        distinct_cond = Series(True, index=df_clean.index)
        n_groups = len(groups)

        for i in range(n_groups):
            for j in range(i + 1, n_groups):
                # 检查每组与其他组是否不同
                distinct_cond = distinct_cond & (df_clean[rep_cols[i]] != df_clean[rep_cols[j]])

        # 组合条件
        result = df_clean[all_group_cond & distinct_cond]
        return result.drop(columns=rep_cols)

    def genotype_phenotype_analysis(
        self,
        trait_file: str,
        trait_name: str,
        font_name: str = 'Arial',
        out_path: str = '.',
        mark_sample_list: List[str] = None
    ) -> None:
        """对单个表型性状进行基因型分组分析，即分析不同基因型间样本表型值差异是否显著"""
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['font.size'] = 8
        if name == 'nt':
            plt.rcParams['font.family'] = font_name
        else:
            set_custom_font(font_name)
        trait_df = read_csv(trait_file, sep='\t').groupby('ID').mean()
        ret = self.to_dataframe(index_col=None, sort_allele=False).apply(
            partial(
                genotype_phenotype_analysis,
                trait=trait_df,
                trait_name=trait_name,
                mark_sample_list=mark_sample_list,
                out_path=out_path
            ),
            axis=1
        )
        ret.to_csv(f'{out_path}/site_sig_stats.xls', sep='\t', na_rep='NA', index=False)
