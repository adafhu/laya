---
layout:     post
title:      "dockerfile"
subtitle:   "写给懒人的 dockerfile 入门指南"
date:       2021-05-28 16:41:00
author:     "kgzhang"
catalog: false
category: devops
header-style: text
tags:
  - docker
  - devops
---

## 指令
- ARG，接收命令行参数. 参见 [分阶段打包](https://gist.github.com/kougazhang/6a62116d79b279e1f6f679dbb3a574cf)
- as，from, 分阶段打包镜像，参见 [分阶段打包](https://gist.github.com/kougazhang/6a62116d79b279e1f6f679dbb3a574cf)
### CMD

在 CMD 中使用变量
```
当您使用执行列表时，如...

CMD ["django-admin", "startproject", "$PROJECTNAME"]
...然后Docker将直接执行给定的命令，而无需使用shell。由于不涉及任何外壳，因此意味着：

无变量扩展
没有通配符扩展
没有I / O重定向功能>，<，|等
没有多个命令通过 command1; command2
依此类推。
如果要CMD扩展变量，则需要安排一个shell。您可以这样做：

CMD ["sh", "-c", "django-admin startproject $PROJECTNAME"]
```

## 容器启动
- 容器启动时无法把带中划线的参数如 `-a=1` 等传递给容器实例，因为 docker 会把此类命令接收。


## 实战
- [分阶段打包](https://gist.github.com/kougazhang/6a62116d79b279e1f6f679dbb3a574cf)
