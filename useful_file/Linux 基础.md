- Linux 显示指定行

  1、tail date.log               输出文件末尾的内容，默认10行

  ​     tail -20  date.log        输出最后20行的内容

  ​     tail -n -20  date.log    输出倒数第20行到文件末尾的内容

  ​     tail -n +20  date.log   输出第20行到文件末尾的内容

  ​     tail -f date.log            实时监控文件内容增加，默认10行。

  2、head date.log           输出文件开头的内容，默认10行

  ​     head -15  date.log     输出开头15行的内容

  ​     head -n +15 date.log 输出开头到第15行的内容

  ​     head -n -15 date.log  输出开头到倒数第15行的内容
  
  3、`sed命令`
  
  ```
    sed -n "开始行，结束行p" 文件名    
  
    sed -n '70,75p' date.log        输出第70行到第75行的内容
  
    sed -n '6p;260,400p; ' 文件名    输出第6行 和 260到400行
  
    sed -n 5p 文件名                 输出第5行
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    sed -i '/该行包含的内容/d' 文件名   删除该行
    sed -i '2d' file  							 删除第二行
    sed -i '$d' fiel                 删除最后一行
    sed -i '/^$/d' file 						删除空白行
    sed -i '2, 4d' file             删除2到4行
    sed -i '/^test/d' 							删除以test开头的行
    sed -i '/test$/d'								删除以test结尾的行
    
    sed -i 's/旧内容/新内容/g' 文件名  替换内容
    
    -n选项和p命令一起使用表示只打印那些发生替换的行：
  	sed -n 's/test/TEST/p' file
  ```
  
  

  ​	

  tail 和 head 加上 -n参数后 都代表输出到指定行数，tail 是指定行数到结尾，head是开头到指定行数

  +数字 代表整数第几行， -数字代表倒数第几行

  

-	Linux设置环境变量

  - 1，首先打开终端

    ```
    open ~/.bash_profile
    ```

       打开配置文件

    1. 写入python的外部环境变量

     export PATH=${PATH}:/Library/Frameworks/Python.framework/Versions/3.6/bin

    3.重命名python

    alias python="/Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6"

    （这步很重要，直接关系到默认启动的python版本是否修改）

    4.关闭文件

    1. $ source ~/.bash_profile

    5.$ python，查看是否修改成功

    ```
    原文链接：https://blog.csdn.net/Homewm/article/details/78057124
    ```

- comm

  ```
  comm -13 f1 f2       显示f2中有f1没有的行数据
  comm -23 f1 f2       显示f1中有f2没有的行数据
  comm -123 f1 f2      什么都不显示
  ```
  
- `wc`

  -		`wc -l 文件夹/* `统计文件夹下所有文件数据条数

- `scp` [链接](https://www.runoob.com/linux/linux-comm-scp.html) https://www.cnblogs.com/clovershell/p/9870603.html

  - 参数：`-r`递归
  - 从本地复制到远程`scp local_file remote_username@remote_ip:remote_folder`
  - 从远程复制到本地(上面的命令后两个参数交换位置)
  - `scp -r iyx@172.17.66.220:/Users/iyx/Desktop/全国中考卷 ./全国中考卷`
  - `scp -o "StrictHostKeyChecking no" username@172.17.42.216:/Users/iyx/Desktop/filename ./`
    - ` -o "StrictHostKeyChecking no"` 可跳过这个yes/no询问
  - scp -P 16000 pengkunpeng@10.10.254.13:~/simple_pro ./

- `/home/pengkunpeng/.local/share/virtualenvs/dmp28-xj2EC8Xl/bin`虚拟环境

- `xargs`https://blog.csdn.net/xjping0794/article/details/77747418

  - `find t/ -name '*.jpg'|xargs -i mv {} {}.png`重命名文件
  - `find . -name "*.jpg"  |xargs rm -rfv`删除当前文件夹下的所有以`.jpg`结尾的文件。`-rfv`递归、强制、显示删除信息
  
  

- locale
  - `locale`： 展示语言包
  - `echo $LANG`: 展示正在使用的语言包