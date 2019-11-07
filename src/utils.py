import os
from pathlib import Path 

def chdir_wrap(path=Path(__file__).parent.parent):
    def wrapper(f):
        def call(*args, **kwargs):
            workdir = os.getcwd()
            os.chdir(path)
            rst = f(*args, **kwargs)
            os.chdir(workdir)
            return rst 
        return call 
    return wrapper

if __name__ == '__main__':
    print('0', os.getcwd())
    @chdir_wrap()
    def f(x, y):
        print(os.getcwd())
        return x + y

    print(2, f(1, 2))
    print(3, os.getcwd())
