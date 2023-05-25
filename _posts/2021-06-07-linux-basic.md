---
layout:     post
title:      "Linux Basic"
subtitle:   "Linux 基础知识"
date:       2021-06-07 20:51:00
author:     "kgzhang"
catalog: false
category: linux
header-style: text
tags:
  - linux
  - devops
---

## 磁盘与文件系统
磁盘是设备 device. 磁盘需要先格式为指定的文件系统, 然后挂载到某个目录, 普通用户才可以在这个目录下进行文件操作.

proc、tmpfs、sysfs、devpts 等都是 Linux 内核映射到用户空间的虚拟文件系统，它们不和具体的物理设备关联，但它们具有普通文件系统的特征，应用层程序可以像访问普通文件系统一样来访问他们。

### 挂载与挂载点
参见 [鸟哥的 Linux 私房菜](https://wizardforcel.gitbooks.io/vbird-linux-basic-4e/content/20.html)

> 所谓的 "挂载" 就是利用一个目录当成进入点, 将磁盘分区的数据放置在该目录下; 也就是说,进入该目录就可以读取该分区的意思. 这个动作我们称为 "挂载", 那个进入点的目录称为 "挂载点".

### 绑定挂载是容器实现自身文件系统的基础
一个绑定挂载就是相关目录树的另外一个视图。典型情况下，挂载会为存储设备创建树状的视图。而绑定挂载则是把一个现有的目录树复制到另外一个挂载点下。通过绑定挂载得到的目录和文件与原始的目录和文件是一样的，无论从挂载目录还是原始目录执行的变更操作都会立即反映在另外一端。
简单的说就是可以将任何一个挂载点、普通目录或者文件挂载到其它的地方。
绑定挂载是一项非常有用的技术，它可以实现跨文件系统的数据共享，这是容器技术实现自身文件系统的基础。

## 文件描述符

Refer: [What are file descriptors, explained in simple terms?](https://stackoverflow.com/questions/5256599/what-are-file-descriptors-explained-in-simple-terms)

**什么是文件描述符?**

简而言之, 当你打开一个文件时, 操作系统会创建一个 entry 代表该文件并存储关于该打开文件的信息. 如果打开 100 个文件则需要 100 个 entries. 目前在操作系统中使用数字代表打开的文件; 与此类似的是 Socket Descriptor, 当你打开网络 socket 时, 同样会有一个数字代表该网络 socket. 这个数字就是 Socket Descriptor.

**系统内置的文件描述符**
- 0, 标准输入;
- 1, 标准输出;
- 2, 标准错误输出.

## 把 hostname 解析为本地地址 127.0.0.1 
> resolve hostname to localhost

在 linux 系统中 `ping <hostname>` 是通的，这是如何做到的呢？

在 `/etc/hosts` 和 `/etc/resolv.conf` 中并没有看到配置 hostname.

使用 `strace -e trace=open -f ping -c1 DT-LNA-09` 查看一下内核调用：
```

```

但是在 `/etc/nsswitch.conf` 中发现有如下配置：
```
hosts:      files dns
```

`/etc/nsswitch.conf` 的作用是什么？nsswitch, name service switch configuration, 名称服务切换配置.

`nsswitch.conf` 的文件格式: `<info> <method1> <method2> <method3>`

info 分类:
- hosts: 主机名和主机号（/etc/hosts)，gethostbyname()以及类似的函数使用该文件

### nss-myhostname 
- [github地址](https://github.com/nomeata/libnss-myhostname)

nss-myhostname 是一个 glibc(GNU C Library) NSS(Name Service Switch) 插件， 提供了解析本地配置的系统主机名的功能。 所谓"本地配置的系统主机名"其实就是 gethostname(2) 函数的返回值。

nss-myhostname 的需求背景：

许多软件依赖于存在一个可以永远被解析的本地主机名。 当使用动态主机名的时候， 传统的做法是在主机名发生变化的同时修改 /etc/hosts 文件。 这种做法的缺点在于要求 /etc 目录必须是可写的， 而且有可能在修改 /etc/hosts 文件的同时， 系统管理员也正在编辑它。启用 nss-myhostname 之后， 就可以不必修改 /etc/hosts 文件。更进一步， 在许多系统上甚至无需存在这个文件。

如何使用？

要激活此NSS模块，可将 "myhostname" 添加到 /etc/nsswitch.conf 文件中以 "hosts:" 开头的行里面。

```
hosts:          files mymachines resolve [!UNAVAIL=return] dns myhostname
```

## 系统调用 (System call)
> 系统调用：运行在用户空间的程序向操作系统内核请求需要更高运行权限的服务。

系统调用分类：
- 文件和设备访问类 比如open/close/read/write/chmod等
- 进程管理类 fork/clone/execve/exit/getpid等
- 信号类 signal/sigaction/kill 等
- 内存管理 brk/mmap/mlock等
- 进程间通信IPC shmget/semget * 信号量，共享内存，消息队列等
- 网络通信 socket/connect/sendto/sendmsg 等
- 其他

## 用户空间和内核空间
> 应用代码通过 glibc 库封装的函数，间接调用 system call

- 内核空间：操作系统直接运行在硬件上，提供设备管理、内存管理、任务调度等功能。
- 用户空间：用户空间通过API请求内核空间的服务来完成其功能——内核提供给用户空间的这些API, 就是系统调用。


## functions

/etc/rc.d/init.d/functions几乎被/etc/rc.d/init.d/下所有的Sysv服务启动脚本加载，也是学习shell脚本时一个非常不错的材料，在其中使用了不少技巧。

在该文件中提供了几个有用的函数：

+ daemon：启动一个服务程序。启动前还检查进程是否已在运行。
+ killproc：杀掉给定的服务进程。
+ status：检查给定进程的运行状态。
+ success：显示绿色的"OK"，表示成功。
+ failure：显示红色的"FAILED"，表示失败。
+ passed：显示绿色的"PASSED"，表示pass该任务。
+ warning：显示绿色的"warning"，表示警告。
+ action：根据进程退出状态码自行判断是执行success还是failure。
+ confirm：提示"(Y)es/(N)o/(C)ontinue? [Y]"并判断、传递输入的值。
+ is_true："$1"的布尔值代表为真时，返回状态码0，否则返回1。包括t、y、yes和true，不区分大小写。
+ is_false："$1"的布尔值代表为假时，返回状态码0。否则返回1。包括f、n、no和false，不区分大小写。
+ checkpid：检查/proc下是否有给定pid对应的目录。给定多个pid时，只要存在一个目录都返回状态码0。
+ __pids_var_run：检查pid是否存在，并保存到变量pid中，同时返回几种进程状态码。是functions中重要函数之一。
+ __pids_pidof：获取进程pid。
+ pidfileofproc：获取进程的pid。但只能获取/var/run下的pid文件中的值。
+ pidofproc：获取进程的pid。可获取任意给定pidfile或默认/var/run下pidfile中的值。

## Autotools
参考：[GNU Autotools 介绍](https://zhuanlan.zhihu.com/p/77904822)

Autotools 可以生成 makefile，很多 Linux 上的项目通过源码安装时都要执行 `./configure; make && make install` 这就说明使用的是 autotools.

从 github 上获取源码后，会发现没有 Makefile 文件，但是发现有 Makefile.am 文件。Makefile.am是一种比Makefile更高层次的编译规则，可以和configure.in文件一起通过调用automake命令，生成Makefile.in文件，再调用./configure的时候，就将Makefile.in文件自动生成Makefile文件了。

为了能执行上述命令，需要先生成 Autotools 构建脚本。
```
autoreconf --install
```

## Linux man pages
[文档链接](https://www.kernel.org/doc/man-pages/)

Linux man pages 分为几个 section:
- 1 User commands: GNU C 库的文档
- 2 System calls:  Linux kernel 的系统调用
- 3 Library function: 标准 C 库的函数文档
- 4 Devices: 设备文档, 大部分在 `/dev` 目录下
- 5 Files: 包括多种文件系统和 `proc(5)` (即在 `/proc` 目录下的文档)
- 7 其他杂项
- 8 管理员文档

## 正则表达式 RegExp

正则表达式的分类
- 基本的正则表达式（Basic Regular Expression 又叫Basic RegEx 简称BREs）
- 扩展的正则表达式（Extended Regular Expression 又叫Extended RegEx 简称EREs）
- Perl的正则表达式（Perl Regular Expression 又叫Perl RegEx 简称PREs）

Linux 系统中常见的文件处理工具中 grep 与 sed 支持基础正则表达式，而 egrep 与 awk 支持扩展正则表达式。

### 基本组成部分
正则表达式的基本组成部分。

|正则表达式|描述|示例|Basic RegEx|Extended RegEx|Python RegEx|Perl regEx|
|:----|:----|:----|:----|:----|:----|:----|
|\|转义符，将特殊字符进行转义，忽略其特殊意义|a\.b匹配a.b，但不能匹配ajb，.被转义为特殊意义|\|\|\|\|
|^|匹配行首，awk中，^则是匹配字符串的开始|^tux匹配以tux开头的行|^|^|^|^|
|$|匹配行尾，awk中，$则是匹配字符串的结尾|tux$匹配以tux结尾的行|$|$|$|$|
|.|匹配除换行符\n之外的任意单个字符，awk则中可以|ab.匹配abc或bad，不可匹配abcd或abde，只能匹配单字符|.|.|.|.|
|[]|匹配包含在[字符]之中的任意一个字符|coo[kl]可以匹配cook或cool|[]|[]|[]|[]|
|[^]|匹配[^字符]之外的任意一个字符|123[^45]不可以匹配1234或1235，1236、1237都可以|[^]|[^]|[^]|[^]|
|[-]|匹配[]中指定范围内的任意一个字符，要写成递增|[0-9]可以匹配1、2或3等其中任意一个数字|[-]|[-]|[-]|[-]|
|?|匹配之前的项1次或者0次|colou?r可以匹配color或者colour，不能匹配colouur|不支持|?|?|?|
|+|匹配之前的项1次或者多次|sa-6+匹配sa-6、sa-666，不能匹配sa-|不支持|+|+|+|
|\*|匹配之前的项0次或者多次|co*l匹配cl、col、cool、coool等|\*|\*|\*|\*|
|()|匹配表达式，创建一个用于匹配的子串|ma(tri)?匹配max或maxtrix|不支持|()|()|()|
|{n}|匹配之前的项n次，n是可以为0的正整数|[0-9]{3}匹配任意一个三位数，可以扩展为[0-9][0-9][0-9]|不支持|{n}|{n}|{n}|
|{n,}|之前的项至少需要匹配n次|[0-9]{2,}匹配任意一个两位数或更多位数|不支持|{n,}|{n,}|{n,}|
|{n,m}|指定之前的项至少匹配n次，最多匹配m次，n<=m|[0-9]{2,5}匹配从两位数到五位数之间的任意一个数字|不支持|{n,m}|{n,m}|{n,m}|
|\| |交替匹配\|两边的任意一项|ab(c\|d)匹配abc或abd|不支持|\| |\| |\| |

### POSIX字符类
POSIX字符类是一个形如[:...:]的特殊元序列（meta sequence），他可以用于匹配特定的字符范围。

|正则表达式|描述|示例|Basic RegEx|Extended RegEx|Python RegEx|Perl regEx|
|:----|:----|:----|:----|:----|:----|:----|
|[:alnum:]|匹配任意一个字母或数字字符|[[:alnum:]]+|[:alnum:]|[:alnum:]|[:alnum:]|[:alnum:]|
|[:alpha:]|匹配任意一个字母字符（包括大小写字母）|[[:alpha:]]{4}|[:alpha:]|[:alpha:]|[:alpha:]|[:alpha:]|
|[:blank:]|空格与制表符（横向和纵向）|[[:blank:]]*|[:blank:]|[:blank:]|[:blank:]|[:blank:]|
|[:digit:]|匹配任意一个数字字符|[[:digit:]]?|[:digit:]|[:digit:]|[:digit:]|[:digit:]|
|[:lower:]|匹配小写字母|[[:lower:]]{5,}|[:lower:]|[:lower:]|[:lower:]|[:lower:]|
|[:upper:]|匹配大写字母|([[:upper:]]+)?|[:upper:]|[:upper:]|[:upper:]|[:upper:]|
|[:punct:]|匹配标点符号|[[:punct:]]|[:punct:]|[:punct:]|[:punct:]|[:punct:]|
|[:space:]|匹配一个包括换行符、回车等在内的所有空白符|[[:space:]]+|[:space:]|[:space:]|[:space:]|[:space:]|
|[:graph:]|匹配任何一个可以看得见的且可以打印的字符|[[:graph:]]|[:graph:]|[:graph:]|[:graph:]|[:graph:]|
|[:xdigit:]|任何一个十六进制数（即：0-9，a-f，A-F）|[[:xdigit:]]+|[:xdigit:]|[:xdigit:]|[:xdigit:]|[:xdigit:]|
|[:cntrl:]|任何一个控制字符（[ASCII](http://zh.wikipedia.org/zh/ASCII)字符集中的前32个字符)|[[:cntrl:]]|[:cntrl:]|[:cntrl:]|[:cntrl:]|[:cntrl:]|
|[:print:]|任何一个可以打印的字符|[[:print:]]|[:print:]|[:print:]|[:print:]|[:print:]|

### 元字符
元字符（meta character）是一种Perl风格的正则表达式，只有一部分文本处理工具支持它，并不是所有的文本处理工具都支持。

|正则表达式|描述|示例|Basic RegEx|Extended RegEx|Python RegEx|Perl regEx|
|:----|:----|:----|:----|:----|:----|:----|
|\b|单词边界|\bcool\b 匹配cool，不匹配coolant|\b|\b|\b|\b|
|\B|非单词边界|cool\B 匹配coolant，不匹配cool|\B|\B|\B|\B|
|\d|单个数字字符|b\db 匹配b2b，不匹配bcb|不支持|不支持|\d|\d|
|\D|单个非数字字符|b\Db 匹配bcb，不匹配b2b|不支持|不支持|\D|\D|
|\w|单个单词字符（字母、数字与_）|\w 匹配1或a，不匹配&|\w|\w|\w|\w|
|\W|单个非单词字符|\W 匹配&，不匹配1或a|\W|\W|\W|\W|
|\n|换行符|\n 匹配一个新行|不支持|不支持|\n|\n|
|\s|单个空白字符|x\sx 匹配x x，不匹配xx|不支持|不支持|\s|\s|
|\S|单个非空白字符|x\S\x 匹配xkx，不匹配xx|不支持|不支持|\S|\S|
|\r|回车|\r 匹配回车|不支持|不支持|\r|\r|
|\t|横向制表符|\t 匹配一个横向制表符|不支持|不支持|\t|\t|
|\v|垂直制表符|\v 匹配一个垂直制表符|不支持|不支持|\v|\v|
|\f|换页符|\f 匹配一个换页符|不支持|不支持|\f|\f|

## Linux 信号
- 2，Interrupt 中断，使用 `kill -2` 相当于用键盘输入 `Ctrl-c` 中断程序。
