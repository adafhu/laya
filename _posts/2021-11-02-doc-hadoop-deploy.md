---
layout:     post
title:      "Hadoop3 HA Docment"
subtitle:   ""
date:       2021-11-02 10:15:53
author:     "kgzhang"
catalog: false
category: bigdata
header-style: text
tags:
  - hadoop
  - bigdata
  - doc
---

## 架构
> Tips: 磨刀不误砍柴工. 理解 Hadoop 的架构, 有助于解决在部署过程中遇到的各种奇奇怪怪的问题.

Hadoop3 支持多于 2 个以上的机器作为 namenode.

任何时间点, 只能有一个 namenode 处于 Active 状态, 其余的机器处于 Active 状态, 否则就会出现 "脑裂问题".

在集群中 Active 节点负责响应所有客户端的操作, 然后 Standby 同步 Active 所有的状态, 以便能实现快速故障转移.

为了能让 Active 节点与 Standby 节点同步状态, 它们需要一组单独的服务 "JournalNodes" 进行通信. 当 Active 节点执行了 namespace 的修改操作时, 它会把这条操作记录写入 JournalNodes 的主节点. Standby 节点通过 JournalNode 读取了 Active 节点的操作记录后, 它会在自己的 namespace 也进行同样的操作. 如果发生故障转移时, Standby 节点在切换为 Active 节点之前会确保读取了所有的 JournalNodes 记录.

为了能实现快速故障转移, Standby 节点必须知道集群中所有 blocks 的最新信息. 为了实现这一点, DataNodes 配置了所有的 NameNodes, 并向所有的 NameNodes 发送块信息和心跳.

在任意时间, 只有 1 个节点处于 Active 状态对于集群至关重要, 否则就会出现"脑裂问题". 为了防止"脑裂问题", 在任意时刻 JournalNodes 只允许一个 Namenode 写入. 在故障转移期间, 将要变成 Active 的 NameNode 可以非常简单地接管写入 JournalNodes 的角色, 这可以有效预防其他节点也继续切换为 Active.  

### Observer Namenode: 解决单机 Namenode 的性能瓶颈

## 硬件资源
- NameNodes 机器: 要有相同的硬件资源
- JournalNode 机器: JournalNode daemon 非常轻量, 所以它可以与 Hadoop daemons 混合部署. 但是需要注意的是: JournalNode 的节点个数必须是大于等于 3 的奇数. JournalNode 服务可用性与实例个数 n 的关系: (n-1)/2

在HA集群中，Standby NameNode也执行命名空间状态检查点，因此在HA集群中不需要运行Secondary NameNode、CheckpointNode 或 BackupNode.

## 部署

### 配置预览
HA 配置是向后兼容的, 允许当前的单点 Namenode 配置继续工作而不需要更换. 配置文件在所有机器上都相同, 不需要根据不同机器的角色调整配置.

HA 集群重用 nameservice ID 来识别单个 HDFS 实例, 该实例实际上可能由多个 HA NameNodes 组成. 另外, 一个叫做 NameNode ID 的新抽象被添加到 HA. 每个在集群中的 NameNode 有一个不同的 NameNode ID 来区分. 为了支持所有的 NameNodes 能使用同一份配置文件, 相关配置参数使用 `nameservice ID` 和 `NameNode ID` 作为后缀.

### 配置细节

#### 配置 hdfs-site.xml

`dfs.nameservices` 和 `dfs.ha.namenodes.[nameservice ID]` 是 2 项非常重要的配置, 要先配置好.

`dfs.nameservices`, nameservice 的逻辑名称. 举例, 该值设为 `mycluster`, 那么该进行如下配置:

```xml
<property>
  <name>dfs.nameservices</name>
  <value>mycluster</value>
</property>
```

`dfs.ha.namenodes.[nameservice ID]` 是在 nameservice 中每个 NameNode 独一无二的标识符. DataNodes 会读取该配置以确定集群中的 NameNodes (上面的架构中讲到 DataNodes 会把块信息和心跳发送到所有的 NameNodes, 所以 DataNodes 要知道 Namenodes 的位置); 假设 `nameservices ID` 配置为 `mycluster`, 使用 `nn1, nn2, nn3` 来标识集群不同的 NameNodes 节点, 那么应该做如下配置:

```xml
<property>
  <name>dfs.ha.namenodes.mycluster</name>
  <value>nn1,nn2, nn3</value>
</property>
```

最少要配置 2 个 NameNodes 来实现 HA, 但是不建议 NameNodes 的数量超过 5 个,建议最好配置 3 个, 以防止过度通信. 

`dfs.namenode.rpc-address.[nameservice ID].[name node ID]`, 每个 NameNode 要监听的 rpc 端口. 延续上面的配置, 那接下来应该配置为:

```xml
<property>
  <name>dfs.namenode.rpc-address.mycluster.nn1</name>
  <value>machine1.example.com:8020</value>
</property>
<property>
  <name>dfs.namenode.rpc-address.mycluster.nn2</name>
  <value>machine2.example.com:8020</value>
</property>
<property>
  <name>dfs.namenode.rpc-address.mycluster.nn3</name>
  <value>machine3.example.com:8020</value>
</property>
```

`dfs.namenode.http-address.[nameservice ID].[name node ID]`, NameNode 要监听的 http 地址及端口:

```xml
<property>
  <name>dfs.namenode.http-address.mycluster.nn1</name>
  <value>machine1.example.com:9870</value>
</property>
<property>
  <name>dfs.namenode.http-address.mycluster.nn2</name>
  <value>machine2.example.com:9870</value>
</property>
<property>
  <name>dfs.namenode.http-address.mycluster.nn3</name>
  <value>machine3.example.com:9870</value>
</property>
```

`dfs.namenode.shared.edits.dir`, 一组 JournalNodes 的地址, 用来供 NameNodes 读写. 示例如下:

```xml
<property>
  <name>dfs.namenode.shared.edits.dir</name>
  <value>qjournal://node1.example.com:8485;node2.example.com:8485;node3.example.com:8485/mycluster</value>
</property>
```

`dfs.client.failover.proxy.provider.[nameservice ID]` 是Java class, HDFS 客户端通过此项连接当前 Active 的 NameNode.

```xml
<property>
  <name>dfs.client.failover.proxy.provider.mycluster</name>
  <value>org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider</value>
</property>
```

`dfs.ha.fencing.methods`, 没看懂 ...

`fs.defaultFS`, Hadoop 客户端(比如自带的 cli 工具)默认使用的连接地址. 延续上述配置, 该项配置示例:

```xml
<property>
  <name>fs.defaultFS</name>
  <value>hdfs://mycluster</value>
</property>
```

`dfs.journalnode.edits.dir`, JournalNode 保存数据的路径, 只可以配置 1 个绝对路径. JournalNode 数据通过多个 JournalNode 保存同样的数据容灾.

```xml
<property>
  <name>dfs.journalnode.edits.dir</name>
  <value>/path/to/journal/node/local/data</value>
</property>
```

`dfs.ha.nn.not-become-active-in-safemode`, 要配置为 true.

## 部署细节

1. 配置文件修改完成后, 首先要运行 JournalNode. 命令如下:

```shell
hdfs --daemon start journalnode
```

2. 同步 NameNode 集群的配置. 这又分为 3 种情况:

2.1 如果当前是正在搭建的新集群, 要运行格式化命令: `hdfs namenode -format`

2.2 如果已经对 namenode 格式化过了, 或者是要把非 HA 集群转化为 HA 集群. 应该把格式化过的 namenode 元数据信息拷贝到另一台 namenode 机器上去, 未格式化的 namenode 机器运行 `hdfs namenode -bootstrapStandby`. 运行这个命令是确保 JournalNodes 包含足够的编辑事务以便能启动两个 namenode.

2.3 如果是把非 HA namenode 转为 HA, 那么应运行命令 `hdfs namenode -initializeSharedEdits`, 这个命令会初始化 JournalNodes 与本地 NameNode 编辑目录的编辑数据.

3. 正常启动所有的 NameNode 节点. 这时你会发现所有的节点都是 Standby 状态.


## 管理命令

- `hdfs haadmin transitionToActive/transitionToStandby`, 这个命令不会进行任何 `fencing`, 所以应该谨慎使用, 可以使用 `hdfs haadmin -failover` 代替.
- `failover`, 在 2 个 NameNode 之间初始化故障转移. 

## 负载均衡 Load Balancer Setup

如果想为 NameNodes 设置负载均衡, 可以通过 `/isActive` http 端口作为健康检查探针. 如果该节点是 active 则返回 200, 否则 405.

## 同步正在编辑的日志: In-progress Edit Log Tailing

默认配置下, Standby NameNode 仅用于编辑那些已经处理完的日志. 但是如果想启动 Standby/Observer 读取的功能, 那么需要开启此功能.

## 自动失败转移

上述配置只会进行手动的失败转移. 本节描述如何实现自动失败转移.

### 组件

为了实现自动失败转移, 需要添加 2 个组件: zookeeper 和 ZKFailoverController(缩写为 ZKFC)

大致实现:
- 失败检测. 每个 NameNode 机器都在 ZK 上缓存了一个 session, 如果机器挂掉, 那么 session 就会过期, 通知其他 Namenode 应该触发故障转移. (应该是 Active 的机器存 session 吧?)
- Active NameNode 选举. ZooKeeper 提供了互斥锁, 当 Active NameNode 崩溃时, 另一个机器获取该互斥锁, 然后它就可以变成下一个 Active 节点了.

ZKFC 是 Zookeeper 的客户端, 用来监控和管理 NameNode 的状态. 每一个运行 NameNode 的机器也运行了 ZKFC, ZKFC 的职责是:
- 健康检查. ZKFC 定时 ping 本地的 NameNode 程序对它进行健康检查. 只要 NameNode 有任何异常, 则 ZKFC 会把它标记为 unhealthy.
- ZooKeeper session 管理. 维护着 session. (但是看 zookeeper 并没有看到???)
- ZooKeeper 选举. 如果本地 NameNode 健康, 并且 ZKFC 看到当前没有其他节点持有锁, 那么这个 ZKFC 会尝试获取锁. 如果获取到锁, 那么它就 "赢得了选举", 它会运行失败转移把本地的 NameNode 设置为 Active 状态. 

> fence 就是加锁

### 关闭集群

需要先关闭集群

### 配置自动失败转移

配置 hdfs-site.xml:

```xml
<property>
   <name>dfs.ha.automatic-failover.enabled</name>
   <value>true</value>
 </property>
```

配置 core-site.xml:

```xml
 <property>
   <name>ha.zookeeper.quorum</name>
   <value>zk1.example.com:2181,zk2.example.com:2181,zk3.example.com:2181</value>
 </property>
```

停用 HDFS 集群.

### 初始化 ZooKeeper 集群

```shell
$HADOOP_HOME/bin/hdfs zkfc -formatZK
```
这条命令会在 ZooKeeper 中创建一个 znode 存储自动失败转移的数据.

### 使用 `start-dfs.sh` 启动集群

做完上述步骤后, 可以使用 `start-dfs.sh` 启动 HDFS 集群.

如果想手动启动集群, 在每一台 NameNode 的机器上执行:

```shell
[hdfs]$ $HADOOP_HOME/bin/hdfs --daemon start zkfc
```

### FAQ

1. 启动 ZKFC 和 NameNode 之间没有顺序

2. 配置监控

- 监控 ZKFC 正常运行
- 监控 ZooKeeper. ZooKeeper 挂了对 HDFS 继续工作没有影响, 只是 HA HDFS 失效了.

3. 是否支持指定某台机器作为 NameNode 的主或高优先级节点? 不可以

## HDFS 升级/回滚 与高可用

1. 关闭所有的 NameNode 节点, 安装新软件;

2. 启动所有的 JouralNode.

3. 启动 1 个 NameNodes 使用 `-upgrade` flag.

4. 该 NameNode 节点一旦启动会立刻变为 Active 节点.

## 参考资料
- [HDFS High Availability Using the Quorum Journal Manager](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html)
