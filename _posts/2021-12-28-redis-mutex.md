---
layout:     post
title:      "Redis Distributed Mutex"
subtitle:   "Redis 分布式锁"
date:       2021-12-28 09:54:56
author:     "kgzhang"
catalog: false
category: redis
header-style: text
tags:
  - redis
  - distribute
---

使用 redis 的 `setnx` 命令可以实现分布式锁。
- 加锁命令：SETNX key value，当键不存在时，对键进行设置操作并返回成功，否则返回失败。KEY 是锁的唯一标识，一般按业务来决定命名。
- 解锁命令：DEL key，通过删除键值对释放锁，以便其他线程可以通过 SETNX 命令来获取锁。
- 锁超时：EXPIRE key timeout, 设置 key 的超时时间，以保证即使锁没有被显式释放，锁也可以在一定时间后自动释放，避免资源被永远锁住。

加减锁的伪代码如下：
```
// 等于1 表示加锁成功
if (setnx(key,1) == 1) {
    expire(key, time.Duration)
    try {
        // TODO 业务逻辑
    } finally {
        // 释放锁，这是非常关键的步骤。
        // 加锁后不释放锁且锁的过期时间很长的话，就会导致其他线程长期获得不到锁。
        del(key)
    }
}
```

## redis 分布式锁的存在问题

### 问题1：SETNX 和 EXPIRE 非原子性
`setnx` 命令不能设置过期时间, 如果再使用 `expire` 对 key 进行过期时间设置，这样就不是原子性操作。

如果 `expire` 设置失败，会造成死锁的问题。

解决这个问题的 2 个办法：
1、写一个 lua 脚本封装 `setnx` 和 `expire`:

```lua
-- 竞锁失败，直接返回
if (redis.call('setnx', KEYS[1], ARGV[1]) < 1)
then return 0;
end;
-- 竞锁成功，设置过期时间
redis.call('expire', KEYS[1], tonumber(ARGV[2]));
return 1;
```

2. 使用 `set` 命令：

从 Redis 2.6.12 版本开始， SET 命令的行为可以通过一系列参数来修改：
- EX seconds ： 将键的过期时间设置为 seconds 秒。 执行 SET key value EX seconds 的效果等同于执行 SETEX key seconds value 。
- PX milliseconds ： 将键的过期时间设置为 milliseconds 毫秒。 执行 SET key value PX milliseconds 的效果等同于执行 PSETEX key milliseconds value 。
- NX ： 只在键不存在时， 才对键进行设置操作。 执行 SET key value NX 的效果等同于执行 SETNX key value 。
- XX ： 只在键已经存在时， 才对键进行设置操作。

所以使用 `set key value EX seconds NX`, 可以达到使用 `setnx` 并同时设置 `expire` 的效果。`set key value EX seconds NX`, 设置成功返回 OK，没有设置成功返回 `nil`。

## 问题2：锁误解除

线程 A 拿到锁执行超时，导致锁 expired 被自动释放。此时 B 获取了锁，随后 A 执行完成，线程 A 使用 DEL 命令释放锁，但此时 B 线程加的锁还没有执行完成，此时 A 释放的是线程 B 加的锁。

解决方案：`setnx` 设置的 value 是加锁者的 UUID，只用加锁者才能去释放锁。

## 问题3： 超时解锁导致的并发

线程 A 执行超时，锁到期释放。此刻 B 获得了锁，线程 A 和 B 都并发执行。

解决方案：
- 锁过期设置的足够大；
- 为获取锁的线程增加守护线程，快过期时增加有效时间。

上述解决方案要注意, 设置过期时间的本质是为了避免因持有锁的线程因为各种意外情况导致的死锁。所以，锁过期时间不能过大，为快过期时的锁增加有效时间也应要有次数限制。

## 问题4：不可重入

当线程在持有锁的情况下再次请求加锁，如果一个锁支持一个线程多次加锁，那么这个锁就是可重入的。如果一个不可重入锁被再次加锁，由于该锁已经被持有，再次加锁会失败。

Redis 可通过对锁进行重入计数，加锁时加1，解锁时减 1，当计数归 0 时释放锁。

使用 Redis Map 数据结构来实现分布式锁，既存锁的标识也对重入次数进行计数。`Redission` 加锁示例：

```lua
// 如果 lock_key 不存在
if (redis.call('exists', KEYS[1]) == 0) then
    // 设置 lock_key 线程标识 1 进行加锁
    redis.call('hset', KEYS[1], ARGV[2], 1);
    // 设置过期时间, pexpire 以毫秒为单位设置过期时间
    redis.call('pexpire', KEYS[1], ARGV[1]);
    return nil;
    end;
// 如果 lock_key 存在且线程标识是当前欲加锁的线程标识
if (redis.call('hexists', KEYS[1], ARGV[2]) == 1)
    // 自增
    then redis.call('hincyby', KEYS[1], ARGV[2], 1);
    // 重置过期时间
    redis.call('pexpire', KEYS[1], ARGV[1]);
    return nil;
    end;
// 如果加锁失败，返回锁剩余时间
return redis.call('pttl', KEYS[1]);
```

## 问题5：无法等待锁释放

客户端等待锁有 2 种方式：
- 客户端定时轮询获取锁;
- 使用 Redis 的发布订阅功能，当获取锁失败时订阅锁释放的信息，获取锁成功释放后，发送锁释放的信息。

## 集群

### 1. 主备切换
redis 将指令缓存在内存 buffer 中，异步将 buffer 中的指令同步到从节点。

在主从节点切换时，当客户端 A 成功加锁时信息存储在主节点的 buffer 还没来得及同步到从节点时主备切换，这样客户端 A 加锁成功的信息就会丢失。导致客户端B 也能成功加锁。

### 2. 集群脑裂
redis 集群发生脑裂，导致有两个 redis master。

## 补充信息

### 可重入锁
可重入锁又名递归锁，是指同一个线程在外层方法获取锁的时候，再进入该线程的内层方法就会自动获取锁，不会因为之前已经获取过还没释放而阻塞。

Java 中的 `ReentrantLock` 和 `synchronized` 都是可重入锁，可重入锁的优点是一定程序上可以避免死锁。

```java
public class Widget {
    public synchronized void doSomething() {
        System.out.println("方法1执行...");
        // 如果 synchronizied 不是可重入的，那么在调用 doOthers 之前需要将 synchronized 释放掉，
        // 实际上锁已经被当前线程所持有了，这样就造成了死锁。
        doOthers();
    }

    public synchronized void doOthers() {
        System.out.println("方法2执行...");
    }
}
```

另外一个需要使用可重入锁的场景：

```java
public class LockTest {
    static ReentrantLock lock = new ReentrantLock();

    public void m1() {
        lock.lock();
        try {
            m2();
        } finally {
            lock.unlock();
        }
    }

    public void m2() {
        lock.lock();
        try {
            // 同步代码块
        } finally {
            lock.unlock();
        }
    }
}
```
上述例子中，`m2` 必须加锁的原因是存在别人不通过 `m1` 直接调用 `m2` 的情况。所以为了避免 `m1` 调用 `m2` 出现死锁的问题，加的锁必须是可重入的。



## 参考
- [分布式锁的实现之 redis 篇](https://xiaomi-info.github.io/2019/12/17/redis-distributed-lock/)
- [Redis 命令参考](http://redisdoc.com/string/set.html)
- [美团技术：不可不说的Java“锁”事](https://tech.meituan.com/2018/11/15/java-lock.html)
- [java的可重入锁用在哪些场合？ - 春风翻书的回答 - 知乎](https://www.zhihu.com/question/23284564/answer/1709892488)

