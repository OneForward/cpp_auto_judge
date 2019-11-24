import os, pickle, re 
import os.path as osp 
import subprocess, psutil , time 

class AutoJudge(object):
    """
    批改一份代码, 包括编译、测试、打分与评论错误等操作

    Parameters
    ----------
        code_dir   : 代码所在文件夹
        ouput_dir  : 编译、测试、打分过程产生的文件的保存路径
        finput     : 输入测例的文件路径
        fanswer    : 测例答案的文件路径
        separators : 输入测例的分隔符，默认以换行符分隔

    Methods
    ---------
        self.compile()           : 编译代码
        self.running_test_case() : 测试测例
        self.check_answers()     : 检查测例输出是否为正确答案
        self.errors(prob_name)   : 评论错误情况
        self.process(fullscore=100, per_case=.05, per_build=.25):
            完成所有代码的编译、测试、打分操作。默认分数配比为 编译 25% 代码 25% 测例 50%
            fullscore 是该问题的满分, per_case=.05 是指一个测例分数默认占 5%
            per_build=.25 是指编译错误扣分 25%
        self.load(pkl_path):
        self.save(pkl_path):
                pkl_path 是 pathlib.Path 类型，以文件形式加载或保存AutoJudge对象

    Properties
    ---------
        self.build_failed : 是否编译成功
        self.TLE          : 运行超时的测例列表
        self.WA           : 答案错误的测例列表
        self.time         : 运行测例的时间列表
        self.memory       : 运行测例的内存列表
		self.score        : 代码分数

    TODO
    ---------
        提供更多的编译接口
    """
    def __init__(self, code_dir, ouput_dir, finput, fanswer, separators=None):
        super(AutoJudge, self).__init__()
        self.ouput_dir    = ouput_dir
        self.finput       = finput
        self.fanswer      = fanswer
        self.debug        = ouput_dir / 'debug'
        self.cache        = ouput_dir / '.cache'
        self.test_case    = ouput_dir / '.cache' / 'test_case'
        
        for p in [self.cache, self.test_case, self.debug]:
            if not p.exists():
                p.mkdir()

        # 将 finput 中的测例分行写成若干个文件
        cases = open(self.finput).read()
        if separators is None: separators = []
        for sep in separators:
            if sep in cases:
                cases = cases.split(sep) 
                break
        else: cases = cases.splitlines() 

        cases       = [ case for case in cases if case ] # 删除空白
        self.cases  = cases 
        self.fcases = [self.test_case / f'{finput.stem}_case_{i+1}{finput.suffix}'  
                                            for i, case in enumerate(cases)]
        for i, fcase in enumerate(self.fcases):
            open(fcase, 'w').write(cases[i])

        self.reset(code_dir)

    def reset(self, code_dir):
        # reset 函数 用于避免多次覆写 fcases 
        if code_dir is None: return
        
        cpps = list(code_dir.glob('*.cpp'))
        if len(cpps) == 1:
            cpp = cpps[0]
        else:
            cpp = code_dir / 'main.cpp'

        # 覆写 该份 code 的相关数据
        self.fdir         = code_dir
        self.fname        = code_dir.name
        self.cpp          = cpp 
        self.TLE          = []
        self.WA           = []
        self.time         = [0] * len(self.cases)
        self.memory       = [0] * len(self.cases)
        self.output       = [''] * len(self.cases)
        self.exe          = self.debug / f'{self.fname}.exe'
        self.build_failed = False
        self.STATE        = 'INIT'

    @classmethod
    def load_pkl(cls, pkl_path):
        if pkl_path is not None and pkl_path.exists():
            return pickle.load(open(pkl_path, 'rb'))

    def load(self, pkl_path):
        if pkl_path is not None and pkl_path.exists():
            self.__dict__.update(pickle.load(open(pkl_path, 'rb')).__dict__)

    def save(self, pkl_path):
        pickle.dump(self, open(pkl_path, 'wb'))

    def compile(self):

        exec_gbk = f"g++ -std=c++14 -w -I{self.fdir} -finput-charset=GBK -fexec-charset=GBK {self.cpp} -o {self.debug / self.fname}"
        exec_gbk_utf = f"g++ -std=c++14 -w -I{self.fdir} -fexec-charset=GBK {self.cpp} -o {self.debug / self.fname}"
        
        if  os.system(exec_gbk) and os.system(exec_gbk_utf):
            self.build_failed = True

    def running_test_case(self):
        
        ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')

        for i, fcase in enumerate(self.fcases):
            
            try:
                fin, fout = open(fcase), open(self.cache / 'out.txt', 'w')
                st = time.time()
                p  = subprocess.Popen(str(self.exe) , stdin=fin, stdout=fout)
                pp = psutil.Process(p.pid)

                self.memory[i]  = pp.memory_info()

                p.wait(timeout=1)

                self.time[i]   = (time.time() - st ) * 1000
                self.output[i] = ILLEGAL_CHARACTERS_RE.sub('', open(self.cache / 'out.txt').read())
                
            except UnicodeDecodeError:
                print(f'{self.fname}对测例{i+1}\tOut.txt can not read\t{self.cases[i]}')
                
            except subprocess.TimeoutExpired:
                p.kill()   
                self.time[i] = (time.time() - st ) * 1000
                self.TLE.append(i)
                self.output[i] = 'TimeLimitedError'
                print(f'{self.fname}对测例{i+1}\tTimeLimitedError\t{self.cases[i]}')

    def __is_answer(self, subList, S):
        # 判断 sublist 中的元素是不是都在 S 中且呈 递增 的位置
        S = ''.join(S.lower().split())   
        current_pos = 0
        for s in subList:
            current_pos = S.find(s.lower(), current_pos) + 1
            if current_pos == 0 : return False
        return True

    def check_answers(self):

        answers = open(self.fanswer, encoding='utf-8').readlines()
        for i, ans in enumerate(answers):
            if i not in self.TLE and not self.__is_answer(ans.split(), self.output[i]):
                self.WA.append(i)
            

    def process(self, fullscore=100, per_case=.05, per_build=.25):
       
        if self.STATE in ['INIT', 'BUILD FAILED']:

            self.compile()
            
            if self.build_failed: 
                self.STATE = 'BUILD FAILED'
                self.score = 0
            else:
                if self.STATE == 'BUILD FAILED':
                    self.STATE = 'REBUILD PASS'
                else:
                    self.STATE = 'BUILD PASS'

        if self.STATE in ['BUILD PASS', 'REBUILD PASS']:

            self.running_test_case()
            self.check_answers()
            
            self.score = fullscore * (1 - len(self.TLE + self.WA) * per_case)

            if self.STATE == 'REBUILD PASS':
                self.score -= fullscore * per_build
            
            self.STATE = 'FINISH'
                

    def __list2str(self, wrong_cases):
        # 将列表变为可读性好的格式，如[1,2,3,4, 10] -> 1-4、10
        W = sorted([x+1 for x in wrong_cases])
        start, end, out = -1, -1, []
        for i, x in enumerate(W):
            if x == end+1:
                end += 1
            else:
                if 0 < i:
                    out.append((start, end))
                start = end = x 
            if i == len(W)-1:
                out.append((start, end))
        outstr = []
        for st, ed in out:
            if st == ed:
                outstr.append(str(st))
            else:
                outstr.append(f'{st}-{ed}')
        return '、'.join(outstr)

    def errors(self, prob_name) :
        
        if self.STATE == 'BUILD FAILED':
            return f'{prob_name}：编译错误'

        s = []
        if self.TLE:
            s.append(f'{prob_name}测例{self.__list2str(self.TLE)}: 运行异常')
        if self.WA  :
            s.append(f'{prob_name}测例{self.__list2str(self.WA)}: 运行错误')
        return '\n'.join(s)

