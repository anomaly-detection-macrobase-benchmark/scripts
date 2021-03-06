import itertools
from operator import itemgetter
import argparse
from evaluation.common import load_execution_result, pr_auc
from utils.argparse import ArgParser
from utils.fs import load_csv, list_files
from utils.plots import marker_cycle, color_cycle, save_plot
import matplotlib.pyplot as plt
import os

arg_parser = ArgParser(
    description='''Evaluates algorithms robustness, time, memory when increasing dataset sizes''',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''Examples:''')
arg_parser.add_argument('result_dir', type=str, help='path to the directory with the benchmark result')
arg_parser.add_argument('--data-dir', type=str, help='path to the directory with the datasets')
arg_parser.add_argument('--label', metavar='COLUMN', dest='label_column_name', default='is_anomaly', type=str,
                        help='label column name if missing in the results (default is_anomaly)')
arg_parser.add_argument('--title', default='', type=str, help='title displayed on the plots')
arg_parser.add_argument('--scale', type=str, default='linear', help='plot axis scale, linear or log')
arg_parser.add_argument('--output-dir', type=str, help='path to the directory for saving plots')
arg_parser.add_argument('--plot-name', default='{dt}_{suptitle}_{name}', type=str,
                        help='name format of plot files, default "{dt}_{suptitle}_{name}"')
arg_parser.add_argument('--silent', action='store_true', help='do not show plots')
args = arg_parser.parse_args()

results_file_paths = [f for f in list_files(args.result_dir) if f.endswith('.json')]

execution_results = [load_execution_result(f, include_scores=True) for f in results_file_paths]
execution_results.sort(key=itemgetter('classifier'))

algorithm_results = {id: sorted(list(g), key=lambda x: len(x['scores']))
                     for id, g in itertools.groupby(execution_results, lambda item: item['classifier'])}


def has_training(group):
    return any(it['trainingTime'] > 0 for it in group)


fig = plt.figure(figsize=[14, 5])
plt.suptitle(args.title.format(name='Time'))

plt.subplot(1, 2, 1)
color = color_cycle()
marker = marker_cycle()
for alg_id, g in algorithm_results.items():
    if not has_training(g):
        next(color)
        next(marker)
        continue
    plt.plot([len(it['scores']) for it in g],
             [it['trainingTime'] for it in g],
             label=alg_id, color=next(color), marker=next(marker))
plt.legend(loc='upper left')
plt.xlabel('dataset size')
plt.ylabel('training time')
plt.yscale(args.scale)
plt.xscale(args.scale)

plt.subplot(1, 2, 2)
color = color_cycle()
marker = marker_cycle()
for alg_id, g in algorithm_results.items():
    plt.plot([len(it['scores']) for it in g],
             [it['classificationTime'] for it in g],
             label=alg_id, color=next(color), marker=next(marker))
plt.legend(loc='upper left')
plt.xlabel('dataset size')
plt.ylabel('classification time')
plt.yscale(args.scale)
plt.xscale(args.scale)

if args.output_dir:
    save_plot(fig, 'time', args.output_dir, name_format=args.plot_name)

fig = plt.figure(figsize=[7, 5])
plt.suptitle(args.title.format(name='Memory'))
color = color_cycle()
marker = marker_cycle()

for alg_id, g in algorithm_results.items():
    plt.plot([len(it['scores']) for it in g],
             [it['maxMemory'] / 1024 / 1024 for it in g],
             label=alg_id, color=next(color), marker=next(marker))
plt.legend(loc='upper left')
plt.xlabel('dataset size')
plt.ylabel('max memory usage, MB')
plt.yscale(args.scale)
plt.xscale(args.scale)

if args.output_dir:
    save_plot(fig, 'memory', args.output_dir, name_format=args.plot_name)

data_file_ids = {r['dataset'] for r in execution_results}
datasets = {id: load_csv(os.path.join(args.data_dir, id)) for id in data_file_ids}

if all([args.label_column_name in d for _, d in datasets.items()]):
    labels = {id: d[args.label_column_name].values for id, d in datasets.items()}

    fig = plt.figure(figsize=[7, 5])
    plt.suptitle(args.title.format(name='PR AUC'))
    color = color_cycle()
    marker = marker_cycle()

    for alg_id, g in algorithm_results.items():
        plt.plot([len(it['scores']) for it in g],
                 [pr_auc(it['scores'], labels[it['dataset']]) for it in g],
                 label=alg_id, color=next(color), marker=next(marker))
    plt.legend(loc='upper left')
    plt.xlabel('dataset size')
    plt.ylabel('PR AUC')
    plt.xscale(args.scale)

    if args.output_dir:
        save_plot(fig, 'auc', args.output_dir, name_format=args.plot_name)

if not args.silent:
    plt.show()
