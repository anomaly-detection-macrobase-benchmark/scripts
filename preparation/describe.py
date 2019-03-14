import argparse
from utils.argparse import ArgParser
import pandas as pd
from utils.fs import load_csv

arg_parser = ArgParser(
    description='''Prints dataset info''',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''Example:
describe.py original_datasets/shuttle-unsupervised-ad.csv
describe.py original_datasets/shuttle-unsupervised-ad.csv --label is_anomaly''')
arg_parser.add_argument('file', type=str, help='path to the CSV file')
arg_parser.add_argument('--label', metavar='label_column', dest='label_column_name', type=str, help='label column name')
args = arg_parser.parse_args()

df = load_csv(args.file)

print(df)
pd.set_option('display.max_columns', 500)
print(df.describe(include='all'))

if args.label_column_name:
    print('\nLabel column: ')
    label_column = df[args.label_column_name]
    print('Value    %')
    print(label_column.value_counts(normalize=True) * 100)