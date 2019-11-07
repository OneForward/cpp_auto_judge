import os
import os.path as osp
from utils import chdir_wrap
import json
config = json.load(open('config.json'))
config_keys = sorted(config.keys())
labid, problems, scores = list(map(config.get, config_keys))


@chdir_wrap()
def move_redundant_files():
    os.chdir(f'junk/lab{labid}')
    if not osp.exists('tmp'):
        os.mkdir('tmp')

    fs = os.listdir()
    fs.sort(key=lambda f: osp.getmtime(f), reverse=True)

    S = set()
    for f in fs:
        if osp.isfile(f):
            sid = f[:13]
            if sid not in S:
                S.add(sid)
            else:
                print(f'{f} is redundant and thus moved')
                os.rename(f, f'tmp/{f}')


if __name__ == '__main__':
    move_redundant_files()
