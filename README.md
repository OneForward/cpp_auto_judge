## CPP作业批改脚本

#### AutoJudge类

在`src/autojudge.py`中提供了方便移植的AutoJudge类。

```python
class AutoJudgeSingle(object):
    """
    批改一份代码, 包括编译、测试、打分与评论错误等操作

    Parameters
    ----------
        code_dir : 代码所在文件夹
        ouput_dir: 编译、测试、打分过程产生的文件的保存路径
        finput   : 输入测例的文件路径 
        fanswer  : 测例答案的文件路径

    Methods
    ---------
        self.compile()           : 编译代码
        self.running_test_case() : 测试测例
        self.check_answers()     : 检查测例输出是否为正确答案

    Properties
    ---------
        self.build_failed : 是否编译成功
        self.TLE          : 运行超时的测例列表
        self.WA           : 答案错误的测例列表
        self.time         : 运行测例的时间列表
        self.memory       : 运行测例的内存列表

    TODO
    ---------
        提供更多的编译接口
    """
class AutoJudge(object):
    """
    同时批改一个问题下的多份代码, 包括编译、测试、打分与评论错误等操作

    Parameters
    ----------
        code_dirs: 列表，每个文件夹是一个等待评测的 cpp 文件夹
        work_dir : 工作文件夹, 在此处保存编译文件(debug/*.exe)、测试结果(.cache/下)
        finput   : 该问题输入测例的文件路径 
        fanswer  : 该问题测例答案的文件路径
        pattern  : re.Pattern 类型，用于提取学号，如果没有提供则默认使用文件夹名称

    Methods
    ----------
        self.process(fullscore=100, p=0.05): 
            fullscore 是该问题的满分, p=0.05 是指一个测例分数默认占 5%
            完成所有代码的编译、测试、打分操作
        self.load(pkl_path):
        self.save(pkl_path):
                pkl_path 是 pathlib.Path 类型，以文件形式加载或保存AutoJudge对象
    """
    
```

#### 环境要求

python包: pandas(仅用于将评价结果输出为excel时使用)

环境中有mingw-w64版本g++编译器(用于编译cpp代码，且提供了编译时的gbk编码支持)

#### 使用方法:

1. 需要在根目录提供学生姓名和学号，目前要求保存为`sid_names.txt`(每行学号\<TAB\>姓名)
3. 在`src/config.json`中配置相关参数，包括实验号、问题号、每个问题的分数、包含所有学生的作业压缩包的路径。目前提供了批改实验9的配置。
4. 在`test_case`文件夹中添加不同问题的测例和答案
5. 逐行执行`python src/main.py`

##### 本项目提供的其他操作，包括

- `src/move.py`中`move_redundant_files()`：删除冗余作业，只保留同一个同学最新提交的作业
- `src/copy.py`中`copy_files()`: 从解压处拷贝作业到`work_dir/codes/` 和`work_dir/reports`下，统一处理
- `src/release.py`中`auto_judge()`：自动评价`work_dir/codes/`中所有的代码，包括编译、测试、打分，接受的测例跟据实验号和题号在`test_case`文件夹中寻找
- `src/release.py`中`release_excel()`：将评价结果和测例输出发布为excel
- `src/release.py`中`recommend_cpp()`：从`work_dir/优秀代码.txt`中抽取出学号，将这些同学的作业拷贝到 `work_dir/优秀代码/`下。这里`优秀代码.txt`中的学号需要自行提供。




