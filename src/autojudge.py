import os, pickle, re 
import os.path as osp 
import subprocess, psutil , time 

class AutoJudgeSingle(object):
    """
        code_dir : 代码所在文件夹
        ouput_dir: 编译、测试、打分过程产生的文件的保存路径

        
        对代码 code 在 finput 的若干个测例下，对照 fanswer, 给出得分
        一次只改一份代码

    """
    def __init__(self, code_dir, ouput_dir, finput, fanswer, is_forced=False, sids_forced=None):
        super(AutoJudgeSingle, self).__init__()
        self.ouput_dir    = ouput_dir
        self.finput       = finput
        self.fanswer      = fanswer
        self.is_forced    = is_forced
        self.sids_forced  = sids_forced
        self.debug        = ouput_dir / 'debug'
        self.cache        = ouput_dir / '.cache'
        self.test_case    = ouput_dir / '.cache' / 'test_case'
        
        for p in [self.cache, self.test_case, self.debug]:
            if not p.exists():
                p.mkdir()

        # 将 finput 中的测例分行写成若干个文件

        seps  = ['=========\n']
        cases = open(self.finput).read()
        found_seps = False
        for sep in seps:
            if sep in cases:
                cases = cases.split(sep) 
                found_seps = True
                break
        if not found_seps: cases = cases.split('\n')

        cases       = [ case for case in cases if case ] # 删除空白
        
        self.cases  = cases 
        self.fcases = [self.test_case / f'{finput.stem}_case_{i+1}{finput.suffix}'  
                                            for i, case in enumerate(cases)]
        for i, fcase in enumerate(self.fcases):
            open(fcase, 'w').write(cases[i])

        self.reset(code_dir)

    def reset(self, code_dir):
        # 用于初始化时 code_dir 为 None
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

    def compile(self):
        # 非 forced 状态下， 不覆写编译
        if self.exe.exists(): 
            print(self.fname + ' compiled already')
            return

        exec_gbk = f"g++ -std=c++14 -w -I{self.fdir} -finput-charset=GBK -fexec-charset=GBK {self.cpp} -o {self.debug / self.fname}"
        exec_gbk_utf = f"g++ -std=c++14 -w -I{self.fdir} -fexec-charset=GBK {self.cpp} -o {self.debug / self.fname}"
        # print(exec_gbk)
        if  os.system(exec_gbk) and os.system(exec_gbk_utf):
            self.build_failed = True
            print(self.fname + ' build error!!!<-----------')
        else:
            print(self.fname + ' build passed')


    def running_test_case(self):
        
        # if not self.exe.exists() : continue 
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

    def issubseq(self, subList, S):
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
            if i not in self.TLE and not self.issubseq(ans.split(), self.output[i]):
                self.WA.append(i)
                # print(f'{self.fname}对测例{i+1}\tWrong Answer\t ')



class AutoJudge(object):
    """docstring for AutoJudge
        code_dirs: 列表，每个文件夹是一个等待评测的 cpp 文件夹
        

        pattern: re.Pattern 类型，用于提取学号，如果没有提供则默认使用文件夹名称
        pkl_path: pathlib.Path 类型，以文件形式加载或保存AutoJudge对象
        

        一次性测试多个同学, 同一个问题

    """
    def __init__(self, code_dirs, ouput_dir, finput, fanswer, pattern=None, is_forced=False, sids_forced=None):
        super(AutoJudge, self).__init__()
        
        self.code_dirs  = code_dirs
        self.auto_judge = AutoJudgeSingle(None, ouput_dir, finput, fanswer, is_forced, sids_forced)

        code_names   = [code_dir.name for code_dir in code_dirs]
        if pattern is not None:
            code_names = [pattern.findall(code_name)[0] for code_name in code_names]

        self.code_names   = code_names
        # self.build_failed = {code_name:False for code_name in code_names}
        self.STATE        = {code_name:'INIT' for code_name in code_names}
        self.TLE          = {code_name:None for code_name in code_names}
        self.WA           = {code_name:None for code_name in code_names}
        self.outputs      = {code_name:None for code_name in code_names}
        self.scores       = {code_name:0    for code_name in code_names}
        self.time         = {code_name:0    for code_name in code_names}
        self.memory       = {code_name:0    for code_name in code_names}

    def process(self, fullscore=100):
        auto_judge = self.auto_judge
        for i, code_dir in enumerate(self.code_dirs):
            code_name = self.code_names[i]
            auto_judge.reset(code_dir)

            if self.STATE[code_name] == 'INIT':

                auto_judge.compile()
                
                # 如果编译失败，不再测试、打分
                if auto_judge.build_failed: 
                    self.STATE[code_name] = 'BUILD FAILED'
                else:
                    self.STATE[code_name] = 'BUILD PASS'

            if self.STATE[code_name] == 'BUILD PASS':

                auto_judge.running_test_case()
                auto_judge.check_answers()

                self.TLE[code_name]      = auto_judge.TLE
                self.WA[code_name]       = auto_judge.WA
                self.outputs[code_name]  = auto_judge.output
                # 打分，每个测例占总分的 5%
                self.scores[code_name]   = fullscore * (1 - len(auto_judge.TLE + auto_judge.WA) * .05)
                self.STATE[code_name]    = 'FINISH'

    
    def load(self, pkl_path):
        if pkl_path is not None and pkl_path.exists():
            self.__dict__.update(pickle.load(open(pkl_path, 'rb')).__dict__)

    def save(self, pkl_path):
        pickle.dump(self, open(pkl_path, 'wb'))

    
    
    
