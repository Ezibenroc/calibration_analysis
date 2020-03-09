import time
import sys
import asyncio


async def run(cmd):
    '''
    From https://docs.python.org/3/library/asyncio-subprocess.html
    '''
    print(cmd)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()


async def run_notebook(cluster, parameter):
    src_notebook = './G5K_non-regression-test.ipynb'
    dst_notebook = f'/tmp/{cluster}_{parameter}.ipynb'
    await run(f'papermill {src_notebook} {dst_notebook} -p cluster {cluster} -p factor {parameter}')
    return dst_notebook


async def convert_notebook(filename):
    assert filename.endswith('.ipynb')
    dstname = filename[:-len('.ipynb')] + '.html'
    await run(f'jupyter nbconvert {filename} --output {dstname}')
    return dstname


async def process_notebook(cluster, parameter):
    tmp_file = await run_notebook(cluster, parameter)
    return await convert_notebook(tmp_file)


async def process_all(clusters, parameters):
    await asyncio.gather(*[
        process_notebook(clust, param)
        for clust in clusters
        for param in parameters
    ])


def main(cluster_list=None):
    clusters = [
        'dahu',
        'yeti',
        'troll',
        'paravance',
        'parasilo',
        'grisou',
        'gros',
        'ecotype',
        'chiclet',
        'chetemi',
    ]
    if cluster_list is not None:
        diff = set(cluster_list) - set(clusters)
        if len(diff) > 0:
            sys.exit(f'Unknown clusters: {", ".join(diff)}')
        clusters = list(cluster_list)
    parameters = [
        'avg_gflops',
        'mean_frequency',
        'mean_temperature'
    ]
    t = time.time()
    asyncio.run(process_all(clusters, parameters))
    t = time.time() - t
    print(f'Processed {len(clusters)} clusters for {len(parameters)} parameters in {t:.2f} seconds')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        cluster_list = sys.argv[1:]
    else:
        cluster_list = None
    main(cluster_list)
