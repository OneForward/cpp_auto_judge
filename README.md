## CPP作业批改脚本

------

#### 环境要求

python包: pandas
环境中有gcc编译器

#### 使用方法:

以批改实验6为例子

1. 需要在根目录提供学生姓名和学号，目前要求保存为sid_names.txt(每行学号<TAB>姓名)和student_ids.txt(每行学号)
2. 新建文件夹junk/lab06，在此处解压所有学生的作业到单独的文件夹里面
3. 在src/config.json中分别修改实验号、问题号、每个问题的分数
4. 新建lab06/test_case，在此处添加若干测例和答案
5. 逐行执行`python src/main.py`

##### main中提供了若干的操作，包括

`move_redundant_files`：删除冗余作业，只保留同一个同学最新提交的作业
`copy_files：` 从解压处拷贝作业到lab06/codes/ 和 lab06/codes/reports下，统一处理
`compile_cpps`：编译所有同学的cpp为exe
`exe2output`: 逐问题逐测例测试每一个exe,输出为excel
`check_answer`: 对比测例输出的结果是否正确
`ans2scores`: 打分
`recommend_cpp`：从优秀代码.txt中抽取出学号，将这些同学的作业拷贝到 lab06/优秀代码 下




