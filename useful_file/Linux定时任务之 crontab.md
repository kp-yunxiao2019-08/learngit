### Linux定时任务之 crontab

- `crontab -e`编辑定时任务列表
- `crontab -l`展示定时任务列表

- 实例

- shell 文件（cron.sh）

  - ```
    #!/bin/bash
    
    . /etc/profile
    . ~/.bash_profile
    
    cd ~/feed_crawler/hot_spot_crawler
    pipenv run python ~/dmp28/msg_crawl.py kb_dmp >log
    ```

  - 注释版

    ```linux
    #!/bin/bash
    
    . /etc/profile #全局（公有）配置，不管是哪个用户，登录时都会读取该文件
    . ~/.bash_profile  #每个用户都可使用该文件输入专用于自己使用的shell信息,当用户登录时,该文件仅仅执行一次!默认情况下,他设置一些环境变量,执行用户的.bashrc文件.
    
    cd ~/feed_crawler/hot_spot_crawler   # 执行下面Python文件所需要的虚拟环境文件(Pipfile)位置路径
    pipenv run python ~/dmp28/msg_crawl.py kb_dmp >log   #执行Python文件
    ```

- 定时任务文件 (crontab -e)

  - ```linux
    0 9 2 * *  /home/pengkunpeng/dmp28/cron.sh 2>/home/pengkunpeng/cron.log   #每月2号9点执行cron.sh文件
    ```

- 

- 各文件

  ```
  /etc/profile:此文件为系统的每个用户设置环境信息,当用户第一次登录时,该文件被执行.
  并从/etc/profile.d目录的配置文件中搜集shell的设置.
  /etc/bashrc:为每一个运行bash shell的用户执行此文件.当bash shell被打开时,该文件被读取.
  ~/.bash_profile:每个用户都可使用该文件输入专用于自己使用的shell信息,当用户登录时,该
  文件仅仅执行一次!默认情况下,他设置一些环境变量,执行用户的.bashrc文件.
  ~/.bashrc:该文件包含专用于你的bash shell的bash信息,当登录时以及每次打开新的shell时,该
  该文件被读取.
  ~/.bash_logout:当每次退出系统(退出bash shell)时,执行该文件. 
  
  另外,/etc/profile中设定的变量(全局)的可以作用于任何用户,而~/.bashrc等中设定的变量(局部)只能继承/etc/profile中的变量,他们是"父子"关系.
   
  ~/.bash_profile 是交互式、login 方式进入 bash 运行的
  ~/.bashrc 是交互式 non-login 方式进入 bash 运行的
  通常二者设置大致相同，所以通常前者会调用后者。
  
  设置生效：可以重启生效，也可以使用命令：source 
  alias php=/var/eyouim/pub/php/bin/php
  source /etc/profile
  ```

- 相关链接

  - https://www.cnblogs.com/persist/p/5197561.html
  - https://www.cnblogs.com/bandiao/p/10805749.html
  - https://www.cnblogs.com/aminxu/p/5993769.html



定时任务其他实例

```
0 8 * * 0 /home/kb_crawler/.local/share/virtualenvs/env_python3.6-Sq45nPbW/bin/python /home/kb_crawler/kb_tools_master/lib/static/resource_statistics.py 7 >>/home/kb_crawler/kb_tools_master/lib/static/log_7 2>>/home/kb_crawler/kb_tools_master/lib/static/err_log_7

0 8 1 * * /home/kb_crawler/.local/share/virtualenvs/env_python3.6-Sq45nPbW/bin/python /home/kb_crawler/kb_tools_master/lib/static/resource_statistics.py 30 >>/home/kb_crawler/kb_tools_master/lib/static/log_30 2>>/home/kb_crawler/kb_tools_master/lib/static/err_log_30

0 8 1 * * /home/kb_crawler/.local/share/virtualenvs/env_python3.6-Sq45nPbW/bin/python /home/kb_crawler/kb_tools_master/lib/static/excellent_feed_statistics.py >>/home/kb_crawler/kb_tools_master/lib/static/log_feed 2>>/home/kb_crawler/kb_tools_master/lib/static/err_log_feed

0 8 * * 0 /home/kb_crawler/.local/share/virtualenvs/env_python3.6-Sq45nPbW/bin/python /home/kb_crawler/kb_tools_master/lib/static/disk_statistic.py >>/home/kb_crawler/kb_tools_master/lib/static/log_disk 2>>/home/kb_crawler/kb_tools_master/lib/static/err_log_disk

0 5 * * 1 cd /home/kb_crawler/jy-flow/kb_schema_check && /home/kb_crawler/.local/share/virtualenvs/env_python3.6-Sq45nPbW/bin/python schema_check.py release >> log/log 2>> err &

0 0 * * 1 cd /home/kb_crawler/jy-flow/basic_data_check && /home/kb_crawler/.local/share/virtualenvs/env_python3.6-Sq45nPbW/bin/python data_check_scheduler.py debug >> log/log 2>> err &

0 20 * * 1-6 source ~/.bash_profile && cd /home/kb_crawler/jy-flow && python3 parse_jy_start.py >>jy_start_log 2>>jy_start_err_log &
```

