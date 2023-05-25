---
layout:     post
title:      "Flink HA"
subtitle:   ""
date:       2021-11-01 19:00:17
author:     "kgzhang"
catalog: false
category: bigdata
header-style: text
tags:
  - flink
  - bigdata
---

## Flink Standalone 模式部署 HA

1. 修改 flink-conf.yaml 

```yaml
# HA 使用 zookeeper
high-availability: zookeeper
# 配置 zookeeper 集群节点的链接
high-availability.zookeeper.quorum: hadoop01:2181,hadoop02:2181,hadoop03:2181
# zookeeper 中存储的根路径
high-availability.zookeeper.path.root: /flink
high-availability.cluster-id: /cluster_flink
# Flink 用到的相关数据会存在 hdfs
high-availability.storageDir: hdfs://hadoop01:9000/flink/recovery
```

2. 修复配置: masters

填写 master 节点的地址, 2 个地址中一个会是 active, 一个会是 standby.
```
flink-addr-1:8081
flink-addr-2:8081
```

3. 启动集群

文档
