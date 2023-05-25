---
layout:     post
title:      "COW: Copy On Write 写时复制"
subtitle:   ""
date:       2021-12-31 09:42:09
author:     "kgzhang"
catalog: false
category: redis
header-style: text
tags:
  - redis
---

## 一、Linux 下的 Copy On Write

在说明 Linux 下的 Copy On Write 机制前，需要知道两个函数：`fork()` 和 `exec()`。需要注意的是 `exec` 不是一个特定的函数，而是一组函数的统称，它包括了 `execl`、`execlp`, `execv`, `execle`, `execve`, `execvp`。

### 1.1 fork 基本介绍

fork 在 man 手册上的介绍:
> fork is an operation whereby a process creates a copy of itself.

fork 是进程创建自身副本的操作。也就是说，父进程创建一个子进程，这就是 `fork`。

下面以例子说明一下 `fork`:

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
  pid_t fpid; // fpid 表示 fork 函数返回值
  int count=0;

  // 调用 fork, 创建出子进程
  fpid = fork();

  // 所以下面的代码有两个进程执行
  if (fpid < 0) {
      printf("create subprocess failed\n");
  } else if (fpid == 0) {
      printf("i am subprocess\n");
      count++;
  } else {
      printf("i am father process\n");
      count++;
  }
  printf("the result of count is %d\n", count);
  return 0;
}
```

输出结果：

```
i am father process
the result of count is 1
i am subprocess
the result of count is 1
```

解释一下:
- fork 作为一个函数被调用。fork 函数会有两次返回，将子进程的 PID 返回给父进程，0 返回给子进程。(如果小于0，说明创建子进程失败)。
- 注意：当前进程调用 `fork`, 会创建一个跟当前进程完全相同的子进程（除了pid)，所以子进程同样是会执行 `fork` 之后的代码。

### 1.2 再看看 exec 函数
一个进程一旦调用 exec 类函数，这个进程本身就 “死亡” 了，系统把代码段替换成新的程序的代码，废弃原有的数据段和堆栈段，并为新程序分配新的数据段与堆栈段，唯一留下的就是进程号。也就是对系统而言，还是同一个进程，不过已经是另一个程序了。（不过 exec 类函数中有的还允许继承环境变量之类的信息）。

所以，exec 系列函数在执行时会*直接替换掉当前进程的地址空间*

如果我的程序想启动另一个程序的执行但自己仍想运行的话，怎么办呢？那就是结合 fork 与 exec 的使用。

举例如下：

```c
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>

char command[256];

int main(void) {
  int rtn; // 子进程的返回数值
  while (1) {
      // 从终端读取要执行的命令
      printf(">");
      fgets(command, 256, stdin);
      command[strlen(command)-1] = 0;
      // 子进程执行此命令
      if (fork() == 0) {
          execlp(command, NULL);
          // 如果 exec 函数返回，表明没有正常执行命令，打印错误信息
          perror(command);
          exit(errno);
      } else { // 父进程，等待子进程结束，并打印子进程的返回值
          wait(&rtn);
          printf("child process return %d\n", rtn);
      }
  }
  return 0;
}
```

### 1.3 Linux 下的 COW
> 没有理解 COW 与 exec 的关系

fork 创建的子进程，*与父进程共享内存空间*。也就是说，如果把子进程*不对内存空间进行写入操作的话，内存空间中的数据不会复制给子进程*，这样创建子进程的速度就很快了。(不用复制，直接引用父进程的物理空间)

技术实现原理：fork 之后，kernel 把父进程中所有的内存页的权限都设置为 read-only，然后子进程的地址空间指向父进程。当父子进程都只读内存时，相安无事。当其中某个进程写内存时，CPU 硬件检测到内存页是 read-only 的，于是触发页异常中断（page-fault）,陷入 kernel 的一个中断例程。中断例程中，kernel 就会把触发异常的页复制一份，于是父子进程各自持有独立的一份。

Copy On Write 技术优点：
- COW 结束可减少分配和复制大量资源时带来的瞬间延迟。（分配内存也有时间上的开销）
- COW 可减少**不必要的资源分配**。比如 fork 进程时，并不是所有的页面都需要复制，父进程的代码段和只读数据段都不被允许修改，所以不需要复制。

Copy On Write 技术缺点：
- 如果 fork 之后，父子进程都还要继续进行写操作，那么会产生大量的分页错误（页异常中断 page-fault）。


补充知识点：
- 页缺失（硬中断、分页错误、缺页中断），指的是当软件试图访问已经映射在虚拟地址空间中，但是并未被加载在物理内存中的一个分页中，由中央处理器的内存管理单元所发出的中断。通常情况下，用于处理此中断的程序是操作系统的一部分。如果操作系统判断此次访问有效的，那么操作系统会尝试将相关的分页从硬盘上的虚拟内存文件中调入内存。（来源：百度百科）
- 中断：为什么需要中断？因为外接设备的速度远远慢于 CPU，如果操作系统通过 CPU “主动关心” 外设事件，采用通常的轮询（polling) 机制，这样太浪费 CPU 了。所以需要一种机制，让外设在需要操作系统处理外设相关事件的时候，能够“主动通知”操作系统，即打断操作系统和应用的正常执行，让操作系统完成外设的相关处理，然后再恢复操作系统和应用的正常执行。这种机制称为中断机制。（中断 CPU 的机制）,(refer: https://chyyuu.gitbooks.io/ucore_os_docs/content/lab1/lab1_3_3_2_interrupt_exception.html)

## 二、Redis 的 COW

《Redis 设计与实现》中讲到的 COW：
- Redis 在持久化时，如果采用 BGSAVE 命令或 BGREWRITEAOF 的方式，那 Redis 会 fork 出一个子进程来读取数据，从而写到磁盘中。
- 总体来看，Redis 还是读多写少。如果子进程存在期间，发生了大量的写操作，那可能会出现很多分页错误，这样就会耗费很多性能在复制上。
- 而在 rehash 阶段上，写操作是无法避免的。所以 Redis 在 fork 出子进程后，将负载因子阈值提高，尽量减少写操作，避免不必要的内存写入，最大限度地节约内存。

## 三、文件系统的 COW

Copy-on-write 在对数据进行修改时，不会直接在原来的数据位置上进行操作，而是重新找个位置修改，这样的好处是一旦系统突然断电，重启之后不需要 Fsck。好处是能保证数据的完整性，断电的话容易恢复。

比如说，要修改数据块 A 的内容，先把 A 读出来，写到 B 块里面去。如果这时断电了，原来 A 的内容还在。

fsck, 是对文件内容做一致性检查的 Linux 命令。

## 四、总结 Copy-On-Write
fork 的


## 参考
- [COW奶牛！Copy On Write机制了解一下](https://zhuanlan.zhihu.com/p/48147304)
- [Linux下Fork与Exec使用](https://www.cnblogs.com/hicjiajia/archive/2011/01/20/1940154.html)
