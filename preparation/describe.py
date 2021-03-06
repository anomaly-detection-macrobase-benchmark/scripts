import os
import argparse
from utils.argparse import ArgParser
from utils.datasets import load_stats
import pandas as pd
from utils.fs import load_csv

arg_parser = ArgParser(
    description='''Prints dataset info''',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''Example:
describe.py example_datasets/shuttle-unsupervised-ad.csv
describe.py example_datasets
describe.py example_datasets/shuttle-unsupervised-ad.csv --label is_anomaly''')
arg_parser.add_argument('path', type=str, help='path to the CSV file or dir with CSV files')
arg_parser.add_argument('--no-contents', action='store_true', help='do not print element values (head, tail)')
arg_parser.add_argument('--label', metavar='label_column', dest='label_column_name', default='is_anomaly', type=str, help='label column name (default is_anomaly)')
args = arg_parser.parse_args()


def describe(file_path):
    df = load_csv(file_path)

    has_label = args.label_column_name in df

    stats = load_stats(df, args.label_column_name if has_label else None)

    pd.set_option('display.max_columns', 500)
    pd.options.display.float_format = '{:.6f}'.format

    print('%d rows, %d columns %s' % (stats.row_count, stats.column_count,
                                      '(not counting the label column)' if has_label else ''))

    if not args.no_contents:
        print(df)
    print(stats.columns)

    if has_label:
        print('\nLabel column: ')
        label_column = df[args.label_column_name]
        print('Value    %')
        print(label_column.value_counts(normalize=True) * 100)


if os.path.isdir(args.path):
    file_paths = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.csv')]
    file_paths = sorted(file_paths, key=lambda f: os.path.getmtime(f))
    for file_path in file_paths:
        print(os.path.relpath(file_path, args.path))
        describe(file_path)
        print()
else:
    describe(args.path)
