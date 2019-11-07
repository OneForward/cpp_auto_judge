import os
import os.path as osp
import glob, shutil, re
from utils import chdir_wrap
import json

config = json.load(open('config.json'))
config_keys = sorted(config.keys())
labid, problems, scores = list(map(config.get, config_keys))


@chdir_wrap()
def recommend_cpp():
    lab = f'lab{labid}'
    lines = open('{lab}/优秀代码.txt'.format(lab=lab)).read().split()
    sids = open('sid_snames.txt', encoding='utf-8').read().splitlines()
    for sid in sids:
        for line in lines:
            if line and line in sid:
                print(sid)


    for f in glob.glob(f'{lab}/codes/*/*.*') + \
             glob.glob(f'{lab}/reports/*.*'):
        for line in lines:
            if line and line in f:
                fname = osp.basename(f)
                fname_no_ext = osp.splitext(fname)[0]
                fname_no_ext = re.findall(r'(\d*)_.*', fname_no_ext)[0]
                fpath = lab + '/优秀代码/' + fname_no_ext
                if not osp.exists(fpath):
                    os.makedirs(fpath)
                f2 =  fpath + '/' + fname
                shutil.copy2(f, f2)
                # print('copying from {f} to {f2}'.format(f=f, f2=f2))

if __name__ == '__main__':
    recommend_cpp()