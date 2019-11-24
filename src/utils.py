import os, re, json, glob, shutil 
import subprocess, collections, logging
import os.path as osp
import pandas as pd 
import pickle as pkl 
from pathlib import Path 
from pyunpack import Archive

# root/ src/ utils.py
file_path = Path(__file__)
src       = file_path.parent
root      = src.parent

config      = json.load(open(src / 'config.json', encoding='utf-8'))
config_keys = sorted(config.keys())
is_forced, labid, PROBLEMS, SCORES, junk_path = list(map(config.get, config_keys))
SCORES    = dict(zip(PROBLEMS, SCORES))
junk_path = root / junk_path
junk_new  = junk_path.parent / (junk_path.name + '_new')
lab_name  = junk_path.name 
lab       = root / lab_name
codes     = lab / 'codes'
reports   = lab / 'reports'
debug     = lab / 'debug'
cache     = lab / '.cache'
pkl_dir   = lab / '.cache' / 'pkls'

test_case     = root / 'test_case'
new_test_case = lab  / 'test_case'

sid_snames  = open(root / 'sid_snames.txt', encoding='utf-8').read().splitlines()
sids_forced = open(root / 'sid_forced.txt', encoding='utf-8').read().splitlines()
sid_snames  = { sid: sname for sid, sname in (sid_sname.split()  for sid_sname in sid_snames) }
sids        = list(sid_snames.keys())
logger_ids  = [ '拷贝', '编译', '测试', '打分']
default_work_dir = root

SEPARATORS  = ['=========\n']

异常json     = lab / '异常.json' 
if is_forced: 
    异常json = lab / '异常_forced.json'

for p in [lab, codes, reports, debug, cache, pkl_dir, junk_new, new_test_case]:
    if not p.exists():
        p.mkdir()
        
for js in [异常json]:
    if not js.exists():
        json.dump({}, open(js, 'w'))


def chdir_wrap(path=default_work_dir):
    def wrapper(f):
        def call(*args, **kwargs):
            workdir = os.getcwd()
            os.chdir(path)
            rst = f(*args, **kwargs)
            os.chdir(workdir)
            return rst 
        return call 
    return wrapper

def pprint_errors():
    errors = json.load(open(异常json))
    keys = ['提交异常', '未提交']
    for key, sid_list in errors.items():
        new_list = [{sid: sid_snames[sid]} for sid in sid_list ]
        errors[key] = new_list 
    json.dump(errors, open(lab / '异常pprint.json' , 'w'), indent=4, ensure_ascii=False)
    print(json.dumps(errors, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    print('0', os.getcwd())
    @chdir_wrap()
    def f(x, y):
        print(os.getcwd())
        return x + y

    print(2, f(1, 2))
    print(3, os.getcwd())
