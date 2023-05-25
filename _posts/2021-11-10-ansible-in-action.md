---
layout:     post
title:      "Ansible In Action"
subtitle:   "Ansible 实战"
date:       2021-11-10 17:24:17
author:     "kgzhang"
catalog: false
category: devops
header-style: text
tags:
  - ansible
  - devops
---

> Tip1: 与前文 《Ansible 快速入门》、《进击的 Ansible：如何快速搞定生产环境 Ansible 项目布局？》 一样，本文使用的 Ansible 版本 2.5.4，项目演示环境 MacOS。由于 Ansible 项目开发活跃版本更新快，很多 API 接口不向后兼容，所以对照本文实践时请确保所用版本一致。

> Tip2: 本文是 Ansible 系列的第三篇。为了阅读效果的最大化，建议按照《Ansible 快速入门》、《进击的 Ansible：如何快速搞定生产环境 Ansible 项目布局？》、本文的顺序进行阅读。

今天主要分享是 Ansible 的实践部分，会以我最近搭建的“大数据套件”实际的项目需求为案例。该“大数据套件”主要包括：Zookeeper、Hadoop、Flink、Kafka 等 4 个组件。从中你可以了解到 Ansible 实际使用场景、上述大数据组件的安装教程及下载可用的 Ansible 发布代码和在此过程中涉及到的一些 Ansible 实用的模块。

我首先会交代一下在搭建项目时使用的第三方模块，以便大家后续看到这些模块时心中有数。其次是大数据组件搭建的具体步骤，—— 这部分内容对于不了解大数据的同学来说可能会有些陌生，但是实际上没有任何关系。因为我在《进击的 Ansible：如何快速搞定生产环境 Ansible 项目布局？》中提到过 “理解 Ansible 最好的方式就是把它看出是一门语言”，所以我会给出这些组件的搭建文档，大家着重理解“我是如何把这些搭建文档翻译成 Ansible DSL” 的，而不是被组件复杂的配置或繁琐的步骤吓倒。

另外需要声明的是，我是 Ansible 的初学者，也只是把 Ansible 作为一个自动化发布的工具。对于 Ansible 的掌握，远逊于诸位运维大佬。所以，后续给出的 Ansible 代码可能没那么精炼，使用 Ansible 的方式与 Galaxy 上的开源项目相比存在诸多不足。“Ansible 系列” 完全是抛砖引玉，欢迎各位大佬评论指教。

## Ansible 进阶模块

好了，闲言少叙，书归正传。在使用 Ansible 进行发布的过程中，我发现有以下几个 Ansible 模块需要重点关注，后续的实战环境我们就直接用了，不再进行解释。

### 引入模块

读完《进击的 Ansible：如何快速搞定生产环境 Ansible 项目布局？》这篇文章你是否有这种疑惑：“尽管知道了如何使用 roles 去合理地组织项目布局，但是具体落实到代码中该如何去把对应的 task、role 等 import 进来呢？”

答案是使用 import 三兄弟或 include 四兄弟。

先看“import 三兄弟”：`import_task`、`import_playbook` 和 `import_role`, 人如其名，光看名字就能知道它们三兄弟分别能把 task、playbook 和 role 引入到当前的文件中。

再看“include 四兄弟”：`include_vars`、`include_tasks`、`include_role` 和 `include`。`import*` 能实现的功能，`include*` 也能实现的七七八八。

那么 “import 三兄弟” 和 “include 四兄弟”之间有什么区别呢？来，咱们上官网文档。

### synchronize

### lineinfile

### with_items

## 参考链接
- [import_tasks](https://docs.ansible.com/ansible/2.5/modules/import_tasks_module.html#import-tasks-module)
- [Including and Importing](https://docs.ansible.com/ansible/2.5/user_guide/playbooks_reuse_includes.html#including-and-importing)
- [Creating Reusable Playbooks](https://docs.ansible.com/ansible/2.5/user_guide/playbooks_reuse.html)





