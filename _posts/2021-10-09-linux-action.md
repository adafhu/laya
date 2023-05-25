---
layout:     post
title:      "Linux In Action"
subtitle:   ""
date:       2021/10/9 11:25 上午
author:     "kgzhang"
catalog: false
category: linux
header-style: text
tags:
  - devops
  - linux 
---

## 文件系统损坏导致无法写入文件

### 现象
程序写入某目录下的文件全部失败.

### 排查
使用 `touch a` 在该目录下创建文件会出现 `Read-only file system` 的报错信息. 这说明文件系统损坏导致文件系统变成了只读模式.

> 文件系统损坏的原因?
> 计算机难免会由于某些系统因素或人为误操作（突然断电）出现系统异常，这种情况下非常容易造成文件系统的崩溃，严重时甚至会造成硬件损坏。这也是我们一直在强调的“服务器一定要先关闭服务再进行重启”的原因所在。

### 修复

1. 查看是否有进程正在使用磁盘. `lsof /disk/sata1`
2. 杀掉占用的进程.
3. 卸载磁盘. `unmount /disk/sata1`
4. 修复文件系统, 假设该磁盘是 `/dev/sdq1`, 修复命令: `fsck -y /dev/sdq1`
5. 重新挂载磁盘, `mount /dev/sdq1 /disk/sata1`

### 监测

对于文件系统损坏导致文件系统变成只读模式, 应该加以监测, 避免此类问题再次发生.

最简单的监测命令:
```shell 
# /proc/mounts 中记录了当前的挂载情况, 使用 `fgrep -c 'ro,'` 会把只读模式的磁盘过滤出来.
fgrep -c ' ro,' /proc/mounts
```

完整脚本可以参考[这里]()

根据 [该链接上的讨论帖](https://www.zabbix.com/forum/zabbix-help/21401-linux-monitoring-for-a-read-only-filesystem) 上述命令在 vmware 下有问题, 在 vmware 中只读的磁盘不会显示出来, 那么可以采取以下方案:

```shell 
touch /tmp/zabbix.test && rm /tmp/zabbix.test
```