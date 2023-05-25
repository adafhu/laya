---
layout:     post
title:      "Golang Micro Service 04"
subtitle:   "多集群 & 多租户"
date:       2021-12-14 15:06:28
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## 多集群

### 多集群部署保障重要服务的稳定性
L0 服务指非常重要的服务，如课中提到的账号服务。

对于这种非常重要的服务应该多集群部署。想实现多集群部署首先要在物理上划分出多个集群，配置中心也支持 “多集群” 这个配置。每个集群都有独立的 Cache。

为了实现某集群故障时迅速把它摘除，多集群在部署时要默认全部连接都有流量请求进来，这样可以对集群 Cache 充分预热。

### 使用子集算法改进集群全链接

集群全部链接的弊端：
- 最初时使用了全链接，全链接在集群规模很大时（300账号节点*1万上游Consumer），这种频繁地建立链接进行 Health Check 对集群的压力也很大，按照毛剑的说法时会有 30% 的 CPU 开销。
- RPC 框架会在空闲期把长连接退化成短连接

改进思路：使用子集算法在每个集群中挑选一部分节点，这样比全链接开销小，还能保障每个集群的 Cache 充分预热。

子集算法需要考虑的点：
- Provider 和 Consumer 是动态变化的，子集算法要能够动态感知这些变化，否则就会出现负载均衡不均的情况, 某些节点的压力大。
- 在客户端重启或扩缩容时，不能使得大面积的服务大面积地重连。
- 需要机器名有一定的连续性

```golang
// backends 保存了 Apiserver 节点的 IP
// clientId 是将原 client 的Ip地址做了 CRC 处理的int
// subsetSize 是子集的大小
func Subset(backends []string, clientId int,subsetSize int) []string{
	subSetCount := len(backends) / subsetSize
 
 
    // 洗牌
	round := clientId / subSetCount
	rand.Seed(int64(round))
	rand.Shuffle(len(backends), func(i, j int) {
		backends[i],backends[j]= backends[j],backends[i]
	})
 
	subsetId:= clientId%subSetCount
	start := subsetId * subsetSize
 
	return backends[start:start+subsetSize]
}
```
## 多租户
多租户：允许多系统共存的方式叫做多租户。多系统共存比如指多个版本共存。多租户能够保证代码隔离，基于流量做路由决策。

### 多租户要解决的问题？
- 微服务通常有上千个节点，搭建 N 套测试环境硬件成本、人力成本都非常高
- 1 套测试环境没有办法做压力测试，因为被多人共用，测试结果不可靠
- 1 套测试环境时无法解决 N 个功能并行测试时，服务A 的变动与服务B的变动互相隔离不影响

### 多租户使用场景
- 金丝雀发布/灰度发布: 会对用户产生影响
- 全链路压测: 影子系统
- 多测试环境构建
- staging deploy 发布
- A/B test

### 多租户本质
从源头传递一个标签，比如说是 HTTP Header, 然后挂载到 Go Context 上下文中，然后基于 RPC 的负载均衡流量来路由，路由到想要的节点。这样就可以使用 1 套测试环境虚拟出无数套测试环境。

### 使用多租户实现染色发布
- 在 K8S 上部署1个待测试的服务实例，该实例的环境变量新增一个 tag 如 `colora`。
- 待测试的实例向服务中心注册时，tag 会写入到该实例的 metadata 中。
- RPC 框架向服务中心查询相关服务时，会将感兴趣实例的 metedata 一并读取。RPC 框架使用 map 数据结构构建 Provider 的连接池，key 值是 tag，默认情况下只会构建一个 tag 为空的连接池。当有了染色 tag 后,  tag `color` 会对应一个单独的连接池，维护着待测试服务实例的链接。这样就实现了测试代码和正常服务的隔离。
- 用户端 HTTP 请求时加个一个特殊的 header，值为上述的 tag。
- RPC 框架中在处理请求时会读取请求的特殊 header，读取后在负载均衡的链接池中找到对应的打了 tag 的节点。这样一层套一层通过 tag 就可以找到全部染色的节点。
- 如果待测试的服务节点只有 1 个，其他服务都是正常服务，这也是可以做到的。染色的服务节点会调用下游时会寻找相同tag，如果没有找到则会降级，也就是会调用正常服务。
- 为了方便运维，要在日志、指标、存储和消息队列里都要标记该 tag，这样能够方便的区别是否是测试流量。
- 全链路压测：全链路压测时也统一部署对应的tag，这样只有压测流量会进入到待压测的容器中。（当然对底层的数据库和缓存有压力的，在 redis 使用不同的 db，数据里使用生产数据库的镜像）


