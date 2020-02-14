import requests
import pandas
import io
import logging
import plotnine
plotnine.options.figure_size = (12, 8)
from plotnine import *

# Setting up a logger
logger = logging.getLogger('non_regression_tests')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def get(url):
    '''
    Download a CSV file at the specified URL and load it into a dataframe.
    '''
    data = requests.get(url)
    if data.status_code != 200:
        raise ValueError(f'Could not download the CSV file, got an error {data.status_code}')
    df = pandas.read_csv(io.BytesIO(data.content))
    logger.info(f'Downloaded a dataframe with {len(df)} rows and {len(df.columns)} columns')
    return df


def format(df):
    '''
    Apply various formating on the given dataframe (e.g., datetime parsing).
    '''
    df['timestamp'] = pandas.to_datetime(df['start_time'], unit='s')
    return df


def filter(df, **kwargs):
    '''
    Filter the dataframe according to the given named parameters.

    Example:
    filter(df, cluster='dahu')
    '''
    for key, value in kwargs.items():
        if key not in df.columns:
            raise ValueError(f'Cannot filter on {key}, missing column')
        df = df[df[key] == value]
    logger.info(f'Filtered the dataframe, there remains {len(df)} rows')
    return df


def filter_latest(df):
    '''
    Keep only the most recent run for each node of the dataframe.
    '''
    df = df.copy()
    all_nodes = [(cluster, node) for _, (cluster, node) in df[['cluster', 'node']].drop_duplicates().iterrows()]
    for cluster, node in all_nodes:
        mask = (df['cluster'] == cluster) & (df['node'] == node)
        last_run = df[mask]['start_time'].max()
        df.drop(df[mask & (df['start_time'] < last_run)].index, inplace=True)
    logger.info(f'Filtered the dataframe, there remains {len(df)} rows')
    return df


def plot_latest_distribution(df):
    col = 'avg_gflops'
    min_f = df[col].min()
    max_f = df[col].max()
    cluster = df['cluster'].unique()
    assert len(cluster) == 1
    cluster = cluster[0]
    df = filter_latest(df)
    median = df[col].median()
    title = f'Distribution of the latest runs made on the cluster {cluster}\nMedian performance of {median:.2f} Gflop/s'
    return ggplot(df) +\
            aes(x=col) +\
            geom_histogram(binwidth=0.5, alpha=0.5) +\
            theme_bw() +\
            geom_vline(xintercept=median) +\
            expand_limits(x=(min_f, max_f)) +\
            xlab('Average performance (Gflop/s)') +\
            ylab('Number of CPU') +\
            ggtitle(title)


def select_last_n(df, n=10):
    selection = df.tail(n=n)
    if len(df) < n:
        selection = pandas.DataFrame(columns=df.columns)
    return selection


def mark_weird(df, select_func=select_last_n, nb_sigma=2, col='avg_gflops'):
    df = df.copy()
    NAN = float('NaN')
    df['mu'] = NAN
    df['sigma'] = NAN
    for i in range(0, len(df)):
        row = df.iloc[i]
        candidates = df[(df['node'] == row['node']) & (df['cpu'] == row['cpu']) & (df['timestamp'] < row['timestamp'])]
        selected = select_func(candidates)[col]
        df.loc[df.index[i], ('mu', 'sigma')] = selected.mean(), selected.std()
    df['low_bound']  = df['mu'] - df['sigma']*nb_sigma
    df['high_bound'] = df['mu'] + df['sigma']*nb_sigma
    df['weird'] = (df[col] - df['mu']).abs() > nb_sigma*df['sigma']
    df.loc[df['mu'].isna(), 'weird'] = 'NA'
    return df


def plot_evolution_node(df, col):
    return ggplot(df) +\
            aes(x='timestamp', y=col, color='weird') +\
            geom_point() +\
            scale_color_manual({
                'NA': '#AAAAAA',
                True: '#FF0000',
                False: '#00FF00'}) +\
            theme_bw() +\
            geom_ribbon(aes(ymin='low_bound', ymax='high_bound'), color='grey', alpha=0.2) +\
            facet_wrap('cpu', labeller='label_both')


def plot_evolution_cluster(df, col):
    cluster = df['cluster'].unique()
    assert len(cluster) == 1
    cluster = cluster[0]
    for node in sorted(df['node'].unique()):
        plot = plot_evolution_node(df[df['node'] == node], col) +\
                ggtitle(f'Evolution of the node {cluster}-{node}')
        print(plot)
