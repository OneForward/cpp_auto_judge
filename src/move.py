from utils import *
import time 

def rm_one_child_dir(path):
    if not path.is_dir(): return
    children = list(path.iterdir())
    for f in children:
        rm_one_child_dir(f)
    if len(children) == 1:
        one_child = children[0]
        if one_child.is_file(): return 
        for grand_child in one_child.iterdir():
            # NOTE: currently shutil.move doesn't support Path
            # print(f'copy {grand_child} to {path}')
            shutil.move(str(grand_child), str(path))
        one_child.rmdir()

def check_zip(path):
    if not path.is_dir(): return
    for f in path.iterdir():
        if f.is_file() and f.suffix in ['.zip', '.rar']:
            print(f'extracting "{f}" to "{f.parent}"')
            p = subprocess.Popen(f'bc x -aoa -target:name "{f}" "{f.parent}"', stdout=open('日志.解压.txt', 'a')) 
            p.wait()
            os.remove(f)
        check_zip(f)

@chdir_wrap()
def move_redundant(over_written=False):
    # if over_written is False, only update new found archive

    origin    = junk_path
    work_dir  = origin.parent
    new_dir   = work_dir / (origin.name + '_new')
    redundant = origin / '冗余'
    naming_error = origin / '命名存在问题'

    for p in [new_dir, redundant, naming_error]:
        if not p.exists():
            p.mkdir()

    origin_fs = sorted(origin.iterdir(), key=lambda f: f.lstat().st_mtime, reverse=True)

    S = set()
    for f in origin_fs:
        if f.name in ['冗余', '命名存在问题']: continue

        sid = re.findall(r'\d{12}', f.name)
        if not sid or sid[0] not in sids:
            print(f'{f} 命名存在问题')
            os.rename(f, naming_error / f.name)
            continue

        sid = sid[0]
        if sid in S:
            os.rename(f, redundant / f.name)
            continue
        # new archive found
        S.add(sid)
        target_dir = new_dir / sid

        if target_dir.exists():
            # 是否覆写
            if not over_written: continue
            # 否则清空target dir
            shutil.rmtree(target_dir)
        
        target_dir.mkdir()
        if f.is_dir():
            shutil.copytree(f, target_dir)
        else:
            p = subprocess.Popen(f'bc x -aoa -target:auto "{f}" "{target_dir}"', stdout=open(work_dir / '日志.解压.txt', 'a'))
            p.wait() # 等待子进程完成

        rm_one_child_dir(target_dir)
        check_zip(target_dir)

            


if __name__ == '__main__':
    move_redundant()
