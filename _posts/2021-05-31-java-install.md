---
layout:     post
title:      "Java Install"
subtitle:   ""
date:       2021-05-31 20:45:00
author:     "kgzhang"
catalog: false
category: java
header-style: text
tags:
  - java
---

# JAVA 各版本下载
- [国人维护镜像](https://www.injdk.cn/)
- [openJDK 官网](https://jdk.java.net/archive/)

# Linux下JDK的安装

>**系统环境**：centos 7.6
>
>**JDK 版本**：jdk 1.8.0_20

## yum 安装
```shell 
yum install -y java-1.8.0-openjdk
```

## 源码安装

### 1. 下载并解压

JDK 下载版本区别:
- ARM 开头的文件名指的是支持 ARM 架构的下载包,如 ARM 64 Compressed Archive	
- x64 开头的文件名指的是传统架构的下载包, 如 x64 Compressed Archive. 当前主流的服务器仍旧是 x64

在[官网](https://www.oracle.com/technetwork/java/javase/downloads/index.html) 下载所需版本的 JDK，这里我下载的版本为[JDK 1.8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) ,下载后进行解压：

```shell
[root@ java]# tar -zxvf jdk-8u201-linux-x64.tar.gz
```



### 2. 设置环境变量

```shell
[root@ java]# vi /etc/profile
```

添加如下配置：

```shell
export JAVA_HOME=/usr/java/jdk1.8.0_201
# JRE_HOME 在高版本中已经不需要配置了.
export JRE_HOME=${JAVA_HOME}/jre  
export CLASSPATH=.:${JAVA_HOME}/lib:${JRE_HOME}/lib  
export PATH=${JAVA_HOME}/bin:$PATH
```

执行 `source` 命令，使得配置立即生效：

```shell
[root@ java]# source /etc/profile
```



### 3. 检查是否安装成功

```shell
[root@ java]# java -version
```

显示出对应的版本信息则代表安装成功。

```shell
java version "1.8.0_201"
Java(TM) SE Runtime Environment (build 1.8.0_201-b09)
Java HotSpot(TM) 64-Bit Server VM (build 25.201-b09, mixed mode)

```
