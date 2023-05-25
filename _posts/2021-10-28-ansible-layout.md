---
layout:     post
title:      "Ansible Advanced"
subtitle:   "如何使用 Ansible 发布复杂项目"
date:       2021-10-28 14:24:57
author:     "kgzhang"
catalog: false
category: devops
header-style: text
tags:
  - devops
  - ansible
---

> Tips: 与前文 《Ansible 快速入门》 一样，本文使用的 Ansible 版本 2.5.4，项目演示环境 MacOS。由于 Ansible 项目开发活跃版本更新快，很多 API 接口不向后兼容，所以对照本文实践时请确保所用版本一致。

学完前文[Ansible 快速入门](https://mp.weixin.qq.com/s/Duj2PIDwXyeudyr9078JzA)后，用来发布单体项目绰绰有余。 但是实际生产环境中一个服务往往有多个组件, 比如部署大数据服务时, 常常需要部署一个“大数据全家桶”： Hadoop、 Zookeeper、 Hive、 Mysql、 Flink 等。这时仅靠前文中的知识就有点捉襟见肘了，繁多的 yaml 文件和其他配置文件依赖关系复杂，如果不能正确地划分目录组织项目结构，对于后期维护是非常不利。所以今天的文章着重解决一下这个问题：如何科学正确地划分 Ansible 应用的目录结构？

## 把 Ansible 视为一种编程语言

首先要树立这样一个观念：“把 Ansible 视为一种编程语言”。Ansible 是专门用来管理自动化发布的 DSL，基本语法规则约等于 yaml 语言规则，诸如 `synchronize`、`pip`、`template` 等 Ansible 模块可等价为语言的内置函数或内置包，编写 playbook 就是在写 Ansible 这门语言的代码块 ... 沿着编程语言的思路去理解 Ansible，很多疑惑会迎刃而解：比如 Ansible 支持变量，模块 `when` 就是编程语言的流程控制语句 `if`， 模块 `loop` 或 `with_*` 就是编程语言中的循环迭代语句 `for` 或 `while`。

使用编程语言进行项目开发的过程中，我们是如何降低项目复杂度的？当然是进行“模块化”。不同的功能封装到不同的包或文件中，这样构成一个业务功能的最小单位我们称之为“模块”。在项目的入口文件中，我们通过 `import` (Python、Golang 等语言中使用此关键字) 或 `require` (Node.js 等语言使用此关键字) 等关键字把需要的模块载入进来，然后就可以进行业务逻辑上的编排。这样做的优点显而易见，一个模块是一个业务功能的具体实现，当后期有修改的需求时只需要修改相关的模块即可，这正是 SOLID 原则中的 “SRP” (单一职责原则) 所提倡的。此外，模块化还支持像“搭积木”一样根据业务需求灵活地组织业务流程，这样就能最大限度地复用当前模块，这也符合编程原则中的 “DRY” (Don't Repeat Yourself)。

既然 “模块化” 有诸多好处且 Ansible 又可以视为一门编程语言（DSL），那么 Ansible 肯定支持模块化了。确实，在 Ansible 文档中用 Roles 表示“模块”这个概念，用 `import_tasks`、`include_tasks` 等表示 `import` 这个概念。(窃以为，Ansible 中发明的“playbook”、“roles” 等概念是非常糟糕的，这些词直译成“剧本”、“角色”真是让人摸不着头脑，直接写成 “task”、“modules” 不是更直观吗？) 

## 至关重要的概念：Roles

读完上部分，在脑海中应已树立这样一个观念“Roles = 模块”。我引用一下文档中对 Roles 的定义，丰富一下这个观念的细节部分:

> Roles let you automatically load related vars, files, tasks, handlers, and other Ansible artifacts based on a known file structure. After you group your content in roles, you can easily reuse them and share them with other users.

“角色允许您基于已知的文件结构自动加载相关的变量、文件、任务、处理程序和其他Ansible工件。在将内容按角色分组后，可以轻松地重用它们并与其他用户共享它们。”

直白来讲，Roles 是对变量、文件、任务等的封装，目的是为了模块重用。这个理解是和上部分的内容能够对齐的。

## 如何使用 Roles？

在软件设计范式的最佳实践中有一条叫做 “约定大于配置”，简单来讲就是“软件中做了一些前提性假设，这些假设就是软件开发者与软件用户的约定。作为软件用户你遵守这些约定即可，不再需要（或不支持）对这些约定进行配置。”—— 一定程度上可以理解为软件中的默认配置。

Ansible 在使用 Roles 时同样存在 “约定大于配置” 的情况，并且这些约定是硬性的（即不支持在配置文件中自定义）。

**首先，Role 的目录结构是固定的。**

> An Ansible role has a defined directory structure with eight main standard directories. You must include at least one of these directories in each role. You can omit any directories the role does not use.

Ansible角色有一个定义好的目录结构，其中有八个主要的标准目录。在每个角色中必须包含至少一个这样的目录。您可以省略角色不使用的任何目录。

该已规定好的目录结构，示例如下：

```
├── defaults
│   └── main.yml
├── files
├── handlers
│   └── main.yml
├── meta
│   └── main.yml
├── tasks
│   └── main.yml
├── templates
├── tests
│   ├── inventory
│   └── test.yml
└── vars
    └── main.yml
```

> By default Ansible will look in each directory within a role for a main.yml file for relevant content.

每个目录下都有一个 `main.yml` 文件。它是该目录的入口文件，Ansible 读取时会默认查找该文件。所以这个 `main.yml` 文件不能省略。

这八个目录的作用是：
- `tasks/main.yml`: 放置 role 执行任务时用到的文件。
- `handlers/main.yml`: 处理程序，可以在 role 内部或外部使用
- `library/my_module.py`: 模块，可以在 role 中使用(有关更多信息，请参见在rroles 中嵌入模块和插件)。
- `defaults/main.yml`: role 的默认变量(有关更多信息，请参阅使用变量)。这些变量具有所有可用变量中最低的优先级，并且可以被任何其他变量(包括库存变量)轻松覆盖。
- `vars/main.yml`: role 中的其他变量。（与 Ansible 模块中的 `vars` 作用一致，只不过这里的 `vars` 表示目录。）
- `files/main.yml`: role 部署时用到的文件。
- `templates/main.yml`: role 部署时用到的模板。与 Ansible 模块中的 `templates` 作用一致，只不过这里的 `templates` 表示目录。）
- `meta/main.yml`: role 使用到的元数据。

**其次，存储和查找 roles**

上文我们已经了解到了一个 role 的内部目录结构，但是这远远不能满足实际生产的需求。在文章的开始部分我们也以一个大数据项目为例，往往需要部署 Flink、Hadoop 等多个组件。这每一个组件都可以看做是一个 role。那么 Ansible 是如何查找 roles 的呢？

默认情况下，有 2 种方式：
- 在 Ansible 的发布项目中，创建一个叫做 `roles` 的目录。
- 默认情况下，Ansible 会自动查找 `/etc/ansible/roles` 目录下的 role。

举个例子，我们要使用 ansible 创建一个发布大数据“全家桶”的项目 bigdata, 该项目下要包含 Flink、Mysql、Hive 这 3 个 role。（在后面的实战部分会进行具体讲解）, 那么 bigdata 这个项目的目录结构大致如下：

```
➜  bigdata tree -L 3
.
└── roles
    ├── flink
    │   ├── defaults
    │   ├── files
    │   ├── handlers
    │   ├── meta
    │   ├── tasks
    │   ├── templates
    │   ├── tests
    │   └── vars
    ├── hive
    │   ├── defaults
    │   ├── files
    │   ├── handlers
    │   ├── meta
    │   ├── tasks
    │   ├── templates
    │   ├── tests
    │   └── vars
    └── mysql
        ├── defaults
        ├── files
        ├── handlers
        ├── meta
        ├── tasks
        ├── templates
        ├── tests
        └── vars
```

由此可见，roles 下的 flink、hive、mysql 的子目录结构就是上文中提到的八大目录。

## ansible-galaxy

### 快速创建 Role

从上文可知，每创建一个 role 都必须至少含有八大目录之一。所以 Ansible 中已内置了一个命令行工具 `ansible-galaxy` 快速创建 role 的八大目录，减轻我们的工作量。

假设该 role 名称是 `flink`, 用如下命令生成相关目录:

```shell
ansible-galaxy init flink
```

使用 `tree` 命令看到 `ansible-galaxy` 生成的目录正是 role 所要求的标准的八个目录。

```
➜  tree flink
flink
├── README.md
├── defaults
│   └── main.yml
├── files
├── handlers
│   └── main.yml
├── meta
│   └── main.yml
├── tasks
│   └── main.yml
├── templates
├── tests
│   ├── inventory
│   └── test.yml
└── vars
    └── main.yml
```

`ansible-galaxy init` 其他几个实用的参数:
- `ansible-galaxy init -force role_name`, 默认情况下创建的 role 与当前工作目录下存在的文件重名的话，会抛出异常。使用 `-force` 选项会强制创建 role 目录，并对 role 目录下重名的目录或文件进行替换。
- `ansible-galaxy init --role-skeleton=/path/to/skeleton role_name`，使用过 Maven 的同学应该知道， Maven 支持以其他项目做骨架创建新项目。ansible-galaxy 同样支持该功能，以 `/path/to/skeleton` 路径下的 role 为骨架，把所有的文件都进行拷贝来创建新的 role。

### Galaxy: role 在线分享社区

此外与 Docker Hub、Grafana Dashboards 类似，Ansible Galaxy 也有一个[在线社区 Galaxy](https://galaxy.ansible.com/home)，上面有开发者分享的各种已经开发好的 roles。你可以搜索现成的 role 下载，也可以上传自己开发的 role 到 Galaxy。

下载或上传 role 到 Galaxy 网站，同样需要使用命令行工具 `ansible-galaxy`。默认情况下 `ansible-galaxy` 调用的 Galaxy 服务端的地址是  https://galaxy.ansible.com, 可以通过 `-server` 选项或在 ansible.cfg 文件中重新配置 Galaxy
的地址。

### 下载 roles

下载 roles 的语法模板是：

```shell
$ ansible-galaxy install username.role_name
```
默认情况下 `ansible-galaxy` 会把 role 下载到环境变量 `ANSIBLE_ROLES_PATH` 中，`ansible-galaxy` 提供了参数 `--role_path` 指定 role 下载的地址。

### ansible-galaxy 其他命令速览
- `ansible-galaxy search elasticsearch`, 查找 Galaxy 网站中的 role `elasticsearch`。
- `ansible-galaxy info username.role_name`, 查看 `username.role_name` 的详细信息
- `ansible-galaxy list`, 查看已安装的 roles.
- `ansible-galaxy remove username.role_name`, 卸载安装的 `username.role_name`
- `ansible-galaxy login`，登录 Galaxy 网站。

## 整体布局: Suit Is Best

如果你坚持读完上述部分，那么你肯定对于如何使用 role 了然于心，简单来讲就是当前 Ansible 应用下需要存在一个叫做 `roles` 的目录。接下来我们聊聊 Ansible 应用下除了 `roles` 目录外，其他目录该如何布局呢? [Ansible 最佳实践官方文档](https://docs.ansible.com/ansible/2.5/user_guide/playbooks_best_practices.html#content-organization) 中是这样建议的：

> Your usage of Ansible should fit your needs, however, not ours, so feel free to modify this approach and organize as you see fit.
> One crucial way to organize your playbook content is Ansible’s “roles” organization feature, which is documented as part of the main playbooks page. You should take the time to read and understand the roles documentation which is available here: Roles.

Ansible 整体的目录结构没有一定之规，适合你的当前需求就好。但是 Roles 这个概念至关重要。

良心的 Ansible 官方在 Github 上开了一个项目 [ansible-examples](https://github.com/ansible/ansible-examples) 专门用来收集优秀的最佳实践。大家可以根据实际需求吸收借鉴，下面我分享一下我常用的项目布局：

```shell
.
├── Makefile
├── README.md
├── deploy.retry
├── deploy.yml
├── files
│   ├── apache-maven-3.8.3-bin.tar.gz
│   ├── apache-zookeeper-3.7.0-bin.tar.gz
│   ├── flink-1.14.0-bin-scala_2.11.tgz
│   ├── hadoop-2.7.5.tar
│   ├── hadoop-3.3.1.tar.gz
│   ├── mysql-connector-java-8.0.26-1.el7.noarch.rpm
│   ├── mysql-connector-java-8.0.26.jar
│   └── openjdk-11.0.2_linux-x64_bin.tar.gz
├── inventories
│   └── hosts
└── roles
    ├── flink
    ├── hadoop
    ├── hadoop3
    ├── hive
    ├── java
    ├── linux
    ├── mvn
    ├── mysql
    └── zookeeper
```
- Makefile，用来封装 Ansible 的发布命令
- deploy.yml, 是执行 Ansible 命令时的入口文件
- files, 用来存放 role 相关的部署包，一般体积较大，不会使用 git 进行版本管理。
- inventories, 用来管理部署机器。
- roles, 用来部署的组件。从上面的目录可知，当前主要是用来部署大数据相关的组件。

给自己打个小广告：在下一个实战章节将使用这个项目布局发布大数据项目，在这个过程中又需要补充哪些 Ansible 的知识呢？为什么我不直接使用 Galaxy 网站上的 role 而是要自己从头开发呢？在部署 Hadoop3、Flink 项目中，使用 Ansible 又踩了哪些坑呢？敬请期待 Ansible 大数据实践!!!

## 参考资料
- [使用 Ansible 传输文件的几种方式](https://zdyxry.github.io/2019/11/22/%E4%BD%BF%E7%94%A8-Ansible-%E4%BC%A0%E8%BE%93%E6%96%87%E4%BB%B6%E7%9A%84%E5%87%A0%E7%A7%8D%E6%96%B9%E5%BC%8F/)
- [Ansible](https://gist.github.com/MrNice/89a3bbe44e218c9d2309)
- [Roles](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html#id2)
- [Galaxy User Guide](https://docs.ansible.com/ansible/2.5/reference_appendices/galaxy.html)
- [约定优于配置](https://zh.wikipedia.org/wiki/%E7%BA%A6%E5%AE%9A%E4%BC%98%E4%BA%8E%E9%85%8D%E7%BD%AE)

