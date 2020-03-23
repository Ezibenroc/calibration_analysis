import sys
import pandas
import os
from cashew import linear_regression as lr
from cashew import archive_extraction as ae


def compute_dgemm_reg_linear(df):
    df = df.copy()
    lr.compute_variable_products(df, 'mnk')
    reg = lr.compute_full_reg(df, 'duration', ['mnk'])
    total_flop = (2 * df['m'] * df['n'] * df['k']).sum()
    total_time = df['duration'].sum()
    reg['avg_gflops'] = total_flop / total_time * 1e-9
    reg['function'] = lr.get_unique(df, 'function')
    return reg


def compute_reg(archive_files):
    reg_list = []
    for filename in archive_files:
        df = ae.read_archive_csv_enhanced(filename, 'result.csv')
        df['cpu'] = 'all'
        reg = lr.regression(df, compute_dgemm_reg_linear)
        reg_list.append(pandas.DataFrame(reg))
    return pandas.concat(reg_list)


def main():
    if len(sys.argv) <= 2:
        sys.exit(f'Syntax: {sys.argv[0]} <output_file> <archive_file(s)>')
    reg = compute_reg(sys.argv[2:])
    reg.to_csv(sys.argv[1], index=False)


if __name__ == '__main__':
    main()
