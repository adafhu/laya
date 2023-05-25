---
layout:     post
title:      "Linux User Commands"
subtitle:   "Linux 用户命令"
date:       2021-05-29 18:47:00
author:     "kgzhang"
catalog: false
category: linux
header-style: text
tags:
  - linux
---

## content

> 本文默认执行环境为 Centos7.

+ [用户](#用户)
+ [网络](#网络)
+ [进程](#进程)
+ [文件处理](#文件处理)
+ [文本处理](#文本处理)
+ [磁盘](#磁盘)
+ [系统文件](#系统文件)
+ [资源管理](#资源管理)
+ [时间](#时间)

## 未归类

### yes
不断输出 yes 命令, 通过管道符与其他有询问的命令组合, 自动回答 yes.

```
yes|<command> 
```

## 运算

### 使用 bc
```
echo "5+6"| bc
```

## 终端
### 查看当前 terminal 使用的终端
```shell
echo $0
```
### 不同解释器对脚本的影响
+ `bash xxx` 是使用 `bash` 解释器执行 xxx 脚本。
+ 脚本第一行加 `#!/bin/zsh` 然后使用 `./xxx` 执行，是使用 zsh 执行脚本。

不同解释器之间的同一个命令存在差异，如果不指定脚本执行时的解释器可能会出现在 terminal 中调试的输出和脚本输出不一致的情况。

## 批量执行
批量 copy，批量 mkdir，使用 `{}`, 示例：
```shell 
# 注意 a,b,c 三者之间不能有空格
mkdir ./{a,b,c}
```

## ssh

### 生成密钥对
```
ssh-keygen
```

### 把公钥拷贝到目标机器
```
ssh-copy-id <userName>@<ip>
``` 

## 用户

### 切换为 root 用户
```
sudo su
```
### 把用户加入一个新的用户组
```
usermod -a -G 用户组 用户
```

### 用户权限
+ r, 4, gives read permissions
+ w, 2, gives write permissions
+ x, 1, gives execute permissions

## 网络
+ hostname: 主机名, 内网地址
+ hostname, 显示机器的主机名
+ hostname -I, 显示机器的内网 IP.

### dig: 从 DNS 服务器查看域名解析
安装 dig 工具:
```
yum install -y bind-utils
```
```
$ dig baidu.com
```


### curl
- 使用代理 -x, --proxy <[protocol://][user:password@]proxyhost[:port]>
- 指定请求方法：-X, --request <command>
- 指定请求头，-H, `-H "Content-type: Application/json"`

+ 安静模式 `-s`
```
# 未开启安静模式
echo `curl -X 'POST' -H 'Content-Type: application/json' -H "Accept: application/json" -d '{"msg_type":"text","content":{"text":"request example"}}' https://open.feishu.cn/open-apis/bot/v2/hook/<token>`

# response
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   131  100    75  100    56    362    270 --:--:-- --:--:-- --:--:--   632
{"code":19001,"msg":"param invalid: incoming webhook access token invalid"}

# 开启后
{"code":19001,"msg":"param invalid: incoming webhook access token invalid"}
```

+ 使用代理访问
```bash
curl http://xxx -x [PROTOCOL://]HOST[:PORT] -vo /dev/null
```
+ 发送 POST 请求
```bash
curl --location -X POST address \
--header 'Content-Type: application/json' \
--data/-d 'json格式的参数'
```
+ 显示 response header
```bash
curl -I <url>
```
+ 查看详细信息
```bash 
curl -v <url>
```

### wget
+ 指定文件的下载目录
```shell
wget -P 目录 网址
```

---

## 进程

### flock: 管理来自 shell 脚本的锁

#### SYNOPSIS 概要

```shell
# 1st form
flock [options] <file|directory> <command> [command args]
# 2st form
flock [options] <file|directory> -c <command>
# 3st form
flock [options] <file descriptor number>
```

#### DESCRIPTION 描述

第 1 种和第 2 种形式将锁包裹在要执行的命令的前面, 类似于 `su` 或 `newgrp` 的形式. 它锁定指定文件或目录, 如果文件或目录不存在加锁时会被创建(假设有适当的权限). 默认情况下, 如果不能立即获取锁, flock 会阻塞等到锁释放.

第 3 种形式是通过打开文件的文件描述符数字.

#### OPTIONS 选型
- `-e, -x`, `--exclusive`, 默认选型, 写锁.
- `-s`, `--share`, 获取共享锁, 也叫做读锁.
- `-u`, `--unlock`, 释放锁.
- `-n`, `--nonblock`, 如果不能立即获取锁将失败. (默认状态下会等待)
- `-w`, `--wait`, 获取锁超时则失败. 单位秒, 允许使用双精度数.
- `-c`, `--command`, 传输 1 个单独 command, 不能使用参数.
- `-o`, `--close`, 在执行命令前关闭加锁的文件描述符. 这个选项对于当命令挂起的子进程不应该持有锁时非常有帮助.

#### EXAMPLES 例子

例子1

```shell
# 打开 2 个 shell, shell1 和 shell2, 执行以下命令:
shell1> flock /tmp -c cat # 目录 /tmp 加排他锁
shell2> flock -w .007 /tmp -c echo; /bin/echo $?
# shell2 的命令会因获取锁超时失败, $? 的值为 1.
```

例子2

```shell 
shell1> flock -s /tmp -c cat
shell2> flock -w .007 /tmp -c echo; /bin/echo $?
# 将锁设置为共享锁后, shell2 的命令就不会失败了.
```

例子3

```shell
flock -x local-lock-file echo 'a b c'
# 在运行 `echo 'a b c'` 前获取锁 local-lock-file
```

例子4

```shell 
# 打开 /tmp 作为文件描述符 200 读取
exec 200</tmp
# 文件描述符 200 加锁
flock 200 
```

### ltrace
ltrace 的使用场景：
- 如果我们用 strace 跟踪一个进程，输出结果很少，是不是说明进程很空闲？其实试试 ltrace，可能会发现别有洞天。记住有内核态和用户态之分。
- ltrace 只能分析调用动态链接库的应用程序，像 Golang 这种使用静态链接的程序无法分析。

### strace
参考资料：
- [strace 跟踪进程中的系统调用](https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/strace.html)
- [运维利器：万能的 strace](https://mp.weixin.qq.com/s?__biz=MzA4Nzg5Nzc5OA==&mid=2651659767&idx=1&sn=3c515cb32bcbcafe16c749024d1545ef&scene=21#wechat_redirect)

starce 可以用来监控进程执行时的系统调用（System call）、信号传递和进程状态变更。

strace 有两种运行模式：
- 通过 strace 启动要跟踪的程序。用法很简单，在原本的命令前加上 strace 即可。
- 跟踪已经在运行的程序，用法同样很简单，把pid 传给 strace 即可。`strace -p <pid>`

常用参数：
-c 统计每种系统调用所执行的时间，调用次数，出错次数。
  - % time：执行耗时占总时间百分比 
  - seconds：执行总时间 
  - usecs/call：单个命令执行时间 
  - calls：调用次数 
  - errors: 出错次数 
  - syscall: 系统调用
-f 跟踪由fork调用所产生的子进程.
-t 在输出中的每一行前加上时间信息.
-tt 在输出中的每一行前加上时间信息,微秒级.
-T 显示每次系统调用所花费的时间
-ttt 微秒级输出,以秒了表示时间.
-e expr, 指定一个表达式, **过滤显示系统调用**。
  -e trace=set，只跟踪指定的系统 调用.例如:-e trace=open,close,rean,write表示只跟踪这四个系统调用.默认的为set=all.
  -e trace=file，只跟踪有关文件操作的系统调用.
  -e trace=process，只跟踪有关进程控制的系统调用.
  -e trace=network，跟踪与网络有关的所有系统调用.
  -e strace=signal，跟踪所有与系统信号有关的 系统调用
  -e trace=ipc，跟踪所有与进程通讯有关的系统调用
-o filename，将strace的输出写入文件filename
-p pid，跟踪指定的进程pid.


**用来观察性能、error log：**
```
strace -T -vvvv -d  -Ff -s 128  -o strace.log -p PID
```

**查找瓶颈调用：**
```
strace  -v -T -d  -Ff  -c -p
```

**例子1：查看应用程序启动失败的原因**
```
strace -tt -f <ProgramName>
```

**例子2：机器上有个叫做run.sh的常驻脚本，运行一分钟后会死掉。 需要查出死因**
```
# 在 run.sh 还在运行时获取其 pid
strace -o strace.log -tt -p 24298
```
查看strace.log, 我们在最后2行看到如下内容:
```
22:47:42.803937 wait4(-1,  <unfinished ...>
22:47:43.228422 +++ killed by SIGKILL +++
```
这里可以看出，进程是被其他进程用KILL信号杀死的。

**例子3：性能分析**
通过分析系统调用次数来比较性能.

```
# 通过「c」选项用来汇总各个操作的总耗时
strace -cp <PID>
```

### 查看进程的启动时间
```shell
ps -eo pid,lstart|grep <PID>
```

### `&` 的作用

终端执行的程序是 shell 进程的子进程. 

每一个命令行终端都是一个 shell 进程，你在这个终端里执行的程序实际上都是这个 shell 进程分出来的子进程。

**正常情况下shell 会阻塞.**

正常情况下，shell 进程会阻塞，等待子进程退出才重新接收你输入的新的命令。

* `&` 只是让 shell 不再阻塞.

加上&号，只是让 shell 进程不再阻塞，可以继续响应你的新命令。但是无论如何，你如果关掉了这个 shell 命令行端口，依附于它的所有子进程都会退出。

**`(cmd &)` 把 cmd 命令挂载到 `systemd` 下.**

而(cmd &)这样运行命令，则是将cmd命令挂到一个systemd系统守护进程名下，认systemd做爸爸，这样当你退出当前终端时，对于刚才的cmd命令就完全没有影响了。

### nuhup 进程守护

```bash
nohup 命令 > log 位置 2&>1 &
```

### screen 进程守护
- 创建新的窗口, `screen -S <窗口名>`
- 进入创建的窗口, `screen -r 窗口名_xxxx`
- 临时退出窗口，让进程后台运行：`ctrl + a + d`
- 查看所有窗口: `screen -ls`
- 在另一台机器或shell上没有分离一个Screen会话，在新的 shell 中可以查看到这个窗口，但是无法进入。这时可以使用下面命令强制将这个会话从它所在的终端分离，转移到当前终端上来：`screen -d`
- 查看当前是否处于 screen 中：`echo $TERM`
- 退出 screen 程序，exit

### supervisor 进程守护
[专门文章单列]

---

### systemd 进程管理

1. 启动/重启/停止某服务. 如果启动失败, 看输出的日志进行处理.

```bash
systemctl start/restart/stop xxx.service
```

查看当前服务的状态

```bash
systemctl status xxx.service
```

2. 对服务进行开机启动项的控制.

```bash
# 将服务加入开机自启动
systemctl enable Service_Name

# 禁止服务开机自启动
systemctl disable Service_Name

# 查看服务是否开机自启动
systemctl is-enabled Service_Name

# 重启 systemctl 服务使配置生效
systemctl daemon-reload
```

3. Centos7 使用 systemctl 添加自定义服务.

   1. 配置文件一般路径:
      + 系统服务目录: `/usr/lib/systemd/system/`，经测试放在系统服务目录下才会生效。
      + 用户服务目录: `/usr/lib/systemd/user/`
      + 查看某个服务的配置文件：`systemctl cat <seriveName>`
   2. 配置文件后缀:
      + `.target` 后缀是开机级别的 unit.
      + `.service` 后缀是服务级别的 unit.
   3. 服务级别的 unit 文件.

   ```
   # Unit: 启动顺序与依赖关系
   [UNIT]
   #服务描述
   Description=Media wanager Service
   #指定了在systemd在执行完那些target之后再启动该服务
   After=network.target
   
   # Service: 启动行为
   [Service]
   #定义Service的运行类型
   Type=simple
   
   #定义systemctl start|stop|reload *.service 的执行方法（具体命令需要写绝对路径）
   #注：ExecStartPre为启动前执行的命令
   ExecStartPre=/usr/bin/test "x${NETWORKMANAGER}" = xyes
   ExecStart=/home/mobileoa/apps/shMediaManager.sh -start
   ExecReload=
   ExecStop=
   
   #创建私有的内存临时空间
   PrivateTmp=True
   
   [Install]
   #多用户为 multi-user.target 的, 表示开机启动.
   WantedBy=multi-user.target
   ```

   修改完配置后, 需要重启 systemctl 服务：
   ```shell
   systemctl daemon-reload
   systemctl enable <serviceName>
   systemctl start <serviceName>
   ```

4. 例子：部署 supervisord

部署 supervisord 程序，使用 systemd 托管。

前提：supervisord 已经安全成功。

首先配置如下文件, [源文件可以从这里获取](https://github.com/kougazhang/linux/tree/master/supervisor)：
+ supervisord.service, 把该文件放置到 `/usr/lib/systemd/system/supervisord.service` 目录下
+ supervisord, 把该文件放置到 `/etc/rc.d/init.d/` 目录下
    + 该文件中 `exec` 的值应该等于 `which supervisord` 的值
+ supervisord.conf，把该文件放到 `/etc` 目录下

使用 ansible 部署可以参考 [此链接](https://github.com/kougazhang/ansible/tree/master/supervisor)

执行命令：
```shell 
# 加载配置文件 supervisord.service
systemctl daemon-reload
# 配置开机自启
systemctl enable supervisord
# 启动服务
systemctl start supervisord
```

---

## 查找文件

### find

find 的参数模式是：`<optionAction> param`
- 如查找文件类型：`-type f`
- 如匹配 `.gz` 结尾的文件名：`-name '*.gz'`

+ 查找 $YouPath 路径下 10 天前的文件并删除
``` 
# -exec rm -f {} \;, 表示查找到后执行的动作
find $YouPath -type f -mtime +10 -exec rm -f {} \;
```
+ 查找含某特征的目录
```
# type d -name "2021-0$loop-*", 表示查找目录
for loop in `seq 4 7`;do find /data -type d -name "2021-0$loop-*" -exec rm -rv {} \;;done
```

## 文件处理

### ls 当前文件夹所有文件
+ `ls -d`, 显示文件夹的绝对路径
+ `ls /disk/sata*`, 支持通配符 `*`

### 文件路径 dirname
- 获取当前的文件所在的目录：dirname 同 golang `filepath.dir()` 一样的

### 文件软链接

+ readlink: 显示软链接文件完整的路径
+ readlink -f <softLinkName>

### rename: 文件重命名

rename 这个命令要区分不同的版本, 下述以 Centos 中的 rename 为例.
该rename用法较为简单：
rename [options] expression replacement file... 
如下述命令将当前目录后缀为.htm的文件改为.html。

```bash
  rename .htm .html *.htm 
```

### 压缩/解压

解压 `tgz`:
- `-C` 的作用是改变当前目录。当解压时使用 `-C` 能够指定解压文件的目录，当压缩时使用 `-C` 能够指定打包文件的根目录。
```shell
// 解压
tar -xzvf xx.tgz -C <当前目录>
// 压缩
tar -cvf xx.tar -C <当前目录> <压缩目录>
```

---

## 磁盘

### 挂载文件系统 mount

命令的基本格式:
- `-t type`, 指定挂载的文件系统, 一般可省略
- `-o options`, 指定挂载的参数, 比如 ro 表示以只读的方式挂载文件系统
- `device`, 指定要挂载的设备, 比如磁盘
- `dir`, 指定把文件系统挂载到哪个目录.

```
mount -t type [-o options] device dir
```

例子1: `mount /dev/sdn1 /disk/sata2`, 把磁盘 `/dev/sdn1` 挂载到目录 `/disk/sata2` 

### 卸载文件系统 unmount

``` 
# 通过卸载点 /disk/sata2 卸载 
unmount /disk/sata2 

# 通过设备名卸载
unmount /dev/sdn1
```

### iostat 查看磁盘读写情况
+ iostat: 磁盘读写情况
+ iostat -x 1, 查看磁盘当前的读写情况.
+ iostat -m, 以 mb 为单位进行显示.

### du 查找大文件
```shell 
du -h <dir> --max-depth=1 | sort -hr | head -n 10
```

例子1: 查找当前目录下的大文件, 目录深度为 1

```shell 
du -h --max-depth=1 .
```

### mkfs 磁盘格式化为指定的文件系统
```shell
# 把磁盘 /dev/sdb1 格式化为 ext4 文件系统 
mkfs -t ext4 /dev/sdb1
```

### fsck 检查/修复文件系统
> 使用 fsck 修复文件系统前, 一定要先把对应的磁盘卸载, 否则会对磁盘造成损坏并且造成数据丢失.

fsck, `filesystem check`.

修复磁盘 deviceA, 对所有的询问回答 yes.
```
fsck -y deviceA
```

---

## 文本处理

### 打印字符串
- `echo` 的移植性没有 printf 好。
- `printf` 是模仿 C 语言风格的，输出更符合直觉。
  
### 比较文本
+ 比较文本，在找到第一个不同时就停止比较
```
cmp <fileA> <fileB>  
```

### tee 重定向数据的副本
```
# 有时屏幕输出可能不是标准输出，所以要一般把标准错误输出重定向到标准输出，然后再使用 tee 重定向
cat <filePath> 2>&1|tee <saveFilePath>
```

### awk: 文本分割
参考 [awk 学习指南](https://kougazhang.github.io/2021/07/07/awk/)

### grep: 文本匹配

#### grep 使用正则表达
- `-F`, --fixed-strings       PATTERN 是固定的字符串, 其中特殊的字符也不会发生转义. 也可以使用 `fgrep` 命令.
- `-E`, --extended-regexp     PATTERN 是扩展的正则表达式 (ERE), 可以直接使用 `egrep` 命令.
- `-G`, --basic-regexp        PATTERN 是基础的正则表达式 (BRE)
- `-P`, --perl-regexp         PATTERN 是 Perl 语言中的正则表达式
- `-w`, --word-regexp         强制 PATTERN 只匹配单词 
- `-x`, --line-regexp         强制 PATTERN 进行段落匹配

例子1:
```bash
echo "abc123dd"|grep -P '\d+'
``` 

例子2:
```bash
docker images|grep -E ^k.*
```

#### 使用引号包含空格的关键字

```bash
grep '2019-10-24 00:01:11' *.log
```

#### 使用 -i 来忽略大小写.

```bash
grep –i 'x' 文件名
```

#### 使用 -v(verse. 翻转), 过滤 `-v` 后的内容
```shell 
# 
echo -e "a\nb\ngrep" grep -v grep 
```

#### 使用 -C 来显示显示前后几行

```bash
grep -C 10 'ok' <fileName>
```

#### 使用 `-R` 匹配目录.
```bash
grep -R 'xxx' directory.
```

### sed: 文本替换

语法模板

```bash
# g 代表全局替换.
s/pattern/replaced/g
```

sed 只支持[基本的正则表达式(BREs)](https://kougazhang.github.io/linux/2021/06/07/linux-basic/#%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%20RegExp) 对正则表达式的支持程度:
- 不支持 \d , 可以使用 [0-9] 代替
- 不支持 +, 使用 * 可以, 但是语义不同, * 表示 0到多个.
- 转义符为 \
- 分组匹配时, 使用 \1, \2, \3 作为匹配项, 举例:

```bash
echo 2021010100|sed -E 's/([0-9]{4})([0-9]{2})([0-9]{2})([0-9]*)/\1-\2-\3 \4/g'
# 输出: 2021-01-01 00
```

sed 常用参数:
- i 表示把结果输出到文件. 不加 -i 不会输出到文件的. 所以可以先不加 -i 验证 sed 的处理程序, 验证通过后再写回文件.

```bash
cat a     
# dsadadsqd213234234

# sed -i 's/[0-9]/got/g' a
```

sed 首字母大小写转换

```shell
echo abc|sed 's/\b\(.\)/\u\1/g'
```

---

## 系统文件

### lsof

+ 查看某进程打开的文件, socket 链接:
  +  `lsof -p <pid>`
  + `lsof -c <progressName>`
+ 查看端口占用, `lsof -i:<port>`
+ 查看某文件的进程: `lsof <fileName>`
+ 查看某目录下文件的进程:
  + 不递归: `lsof +d <dirName>`
  + 递归: `lsof +D <dirName>`

---

## 资源管理

### top

+ load average: 负载均衡, 机器过去 5min, 10min, 15min 负载均衡的情况. 一般在 3, 4 左右比较正常.
+ wa: wait io. 比如网络请求或磁盘读写都属于该项. 一般小于 1 时比较正常.
+ %CPU, 表示程序使用的核数. 每 100 表示使用了 1 个核.
+ 按下1, 会显示该机器有几个逻辑核, 每个核的使用情况.

## 时间

### date

**当前时间格式化**

```shell
date +"%Y-%m-%d %H:%M:%S"
# 2021-03-09 14:09:17
```

**时间运算: 指定日期减 1 天**

```shell
# param: 20210316 被减数, -1 day 要减去的天数
# param: "%Y-%m-%d": 输出格式
date -d "20210316 -1 day" +"%Y-%m-%d"
# output: 2021-03-15
```

**时间运算的其他例子**

```shell 
# 当前时间减去 4 天
date -d "-4 day" +"%Y-%m-%d"

# 当前时间减 1 day
date --date="-1 day"

# 当前时间减 1 year
date --date="-1 year"

# 当前时间加 1 year
date --date="+1 year"

# 当前月第 1 天
date +"%Y%m01"

# 当前月最后 1 天
date -d"$(date -d"1 month" +"%Y%m01") -1 day" +"%Y%m%d"
```

**字符串日期转为时间戳**

```shell
# exmaple1
date -d "Nov  4 15:49:41 CST 2018" +%s

# example2
date -d "2021-07-01" +%s

# 如果字符串的日志并不规律, 直接转换为时间戳时会失败, 这时要先对字符串日期进行转换
# $yesterday is 2021-08-09, $i is hour 03
start=`date -d "$yesterday $i" +%s`

```

**字符串日期转换指定格式的字符串**

```shell
[root@localhost ~]# date -d 'Mon Jul 27 20:31:33 2020' +'%Y-%m-%d %H:%M:%S'
2020-07-27 20:31:33
```

**时间戳转为日期**

```shell
# 不指定日志的格式
date -d @1541317781

# 指定日志的格式
date -d @1541317781 +'%Y%m%d %H:%M:%S'
```

### 网络校时: NTP

NTP 通讯协议是专门用来校正服务器时间的. NTP 会从国家授时中心等权威服务器获取当前时间.

**安装 NTP**

```shell
yum install -y ntp
```

**NTP 配置**

`/etc/ntp.conf`, 可以在配置文件中配置 NTP 的服务端. 比如以下配置是使用阿里云的授时服务.

```shell
server time1.aliyun.com
server time2.aliyun.com
server time3.aliyun.com
server time4.aliyun.com
server time5.aliyun.com
server time6.aliyun.com
server time7.aliyun.com
```

**使用 systemctl 管理 NTP**

```shell
# 启动
system start ntp
# 开机自启 ntp
system enable ntp
```


## 未归类

### xargs

+ -n, 每次执行命令时替换的最大参数个数, 如-n1
+ -I 指定一个替换字符串

```bash
realpath ./sugar| xargs -t -I '{}' ln -s {} /root/sugar
```

+ -d, 定界符. 默认使用空格. 使用 -d 来指定新的分隔符.

```bash
printf "abn"|xargs -d b
a n
```

### wc: word count

wc -l, 统计出现的行

### crontab: 定时任务

**配置时间**
> 推荐到在线网站上验证时间配置

crontab 时间位置：分、时、日、月、周

crontab的命令构成为 时间+动作，操作符有:
+ `*` 取值范围内的所有数字
+ `/` 每过多少个数字
+ `-` 从X到Z
+ `,` 散列数字

实例
```
// 每隔 1 小时执行。* 代表取值范围内的所有数字，所以分位不能是 *，如果写为 * */1 * * *, 则是每小时的每1分都执行，也就是每分钟执行 1 次
0 */1 * * *
// 每周六 03:00 执行任务
0 */3 * * 6
```

**常用命令**
+ 编辑定时任务项: crontab -e, 编辑的是 `/var/spool/cron/<用户名>` 文件.
+ 列出当前 crontab 计划: crontab -l
+ 查看执行记录: tail -f /var/log/cron
+ 查看 crontab 执行任务的日志, 这个不一定会有: tail -f /var/spool/mail/

**crontab 常用配置文件**

我们经常使用的是crontab命令是cron table的简写，它是cron的配置文件，也可以叫它作业列表，我们可以在以下文件夹内找到相关配置文件。

+ /var/spool/cron/ 目录下存放的是每个用户包括root的crontab任务，每个任务以创建者的名字命名
+ /etc/crontab 这个文件负责调度各种管理和维护任务。
+ /etc/cron.d/ 这个目录用来存放任何要执行的crontab文件或脚本。
+ 我们还可以把脚本放在/etc/cron.hourly、/etc/cron.daily、/etc/cron.weekly、/etc/cron.monthly目录中，让它每小时/天/星期、月执行一次。

**记录日志**
程序要自己写日志，便于后期排查问题。

**使用环境变量**
```
0 5 * * * . $HOME/.profile; /path/to/command/to/run
```

最简单的方法：
```
# 注意 >> 添加符号
# 2>&1 是要把标准输出和标准错误都统一输出到一个文件.
* * * * * find $YouPath -type f -mtime +10 -exec rm -f {} \; >> /disk/ssd1/crontab-log 2>&1
```

**踩坑: 一定要调试**
  
+ 非系统命令需要写出它的绝对路径.

+ 脚本能运行成功, 不代表在 crontab 下一定会执行成功. 

比如 hdfs 这个命令在 shell 下可以正常调用, 但是 crontab 执行时就会抛出找不到该命令之类的异常, 需要写出 hdfs 的绝对路径才能执行成功.

比如 `find $YouPath -type f -mtime +10 -exec rm -f` 在命令行下可以执行，但是在 crontab 中需要加 `\;`, 即：
```
* * * * * find $YouPath -type f -mtime +10 -exec rm -f {} \; >> /disk/ssd1/crontab-log 2>&1
``` 

在crontab文件中定义多个调度任务时，需要特别注环境变量的设置，因为我们手动执行某个任务时，是在当前shell环境下进行的，程序当然能找到环境变量，而系统自动执行任务调度时，是不会加载任何环境变量的，因此，就需要在crontab文件中指定任务运行所需的所有环境变量，这样，系统执行任务调度时就没有问题了。

不要假定cron知道所需要的特殊环境，它其实并不知道。所以你要保证在shelll脚本中提供所有必要的路径和环境变量，除了一些自动设置的全局变量。所以注意如下3点：

脚本中涉及文件路径时写全局路径；

脚本执行要用到java或其他环境变量时，通过source命令引入环境变量，如:

```shell
cat start_cbp.sh
!/bin/sh
source /etc/profile
export RUN_CONF=/home/d139/conf/platform/cbp/cbp_jboss.conf
/usr/local/jboss-4.0.5/bin/run.sh -c mev &
```
当手动执行脚本OK，但是crontab死活不执行时,很可能是环境变量惹的祸，可尝试在crontab中直接引入环境变量解决问题。如:

```shell
0 * * * * . /etc/profile;/bin/sh /var/www/java/audit_no_count/bin/restart_audit.sh
```

**排查 crontab 任务没有执行的原因:**
+ 查看执行记录: tail -f /var/log/cron
+ 如果日志显示任务执行了但是没生效, 应该是程序问题, `查看 crontab 执行任务的日志: tail -f /var/spool/mail/root` , 执行日志中应该有具体错误的原因.
+ 如果日志显示任务根本没执行:
    + 排查时间配置是否正确, 可以找个在线网站校验一下.
    + `ps -ef|grep cron` , 排查 crontab 程序是否正常运行.
    + `/sbin/service cron start`, centos6 启动 crontab

## 包管理 yum

### 安装 epel-release
 EPEL (Extra Packages for Enterprise Linux)是基于Fedora的一个项目，为“红帽系”的操作系统提供额外的软件包，适用于RHEL、CentOS和Scientific Linux.
```shell
yum install epel-release
```
yum 官方提供的包不全，所以必须先安装 `epel-release`，才能找到常用的软件。

## 包管理 dpkg
dpkg 是 Debian 的包管理工具，dpkg 是管理安装本地包。

```shell
# 安装
dpkg installl -i xx.dep
# 卸载
dpkg -r <serviceName>
# 删除配置
dpkg --purge <serviceName>
```

## 帮助命令

### shell 内置命令与外部命令
使用 `type <command>`, 如果显示为 `is a shell builtin` 说明是 shell 内置命令，否则为外部命令

- help 只能查看 shell 内置命令
- man 
 - man <command>
- info, 也可以查看命令内容。

## yum 镜像源管理

插件 yum-fastestmirror 自动选择最快的yum 源.

安装命令：`yum -y install yum-fastestmirror`

配置镜像:

```shell
# vim /var/cache/yum/timedhosts.txt

mirrors.163.com
mirrors.aliyun.com
```
