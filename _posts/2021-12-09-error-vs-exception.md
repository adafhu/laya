---
layout:     post
title:      "Golang-error-01: Error vs Exception"
subtitle:   "Golang 异常处理"
date:       2021-12-09 10:46:43
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## todo
- [  ] errors 包设计

## Error 类型的本质

Go error 就是一个普通接口 interface. 看一下它的实现：

```golang
type error interface {
	Error() string
}
```

所以自定义错误类型只有实现该结构体即可。 

## 自定义 Error 规范

建议规范: "packageName: errorInfo"

举例：`errors.New("customer: invalid customer id")`

## Question1

为什么Golang 内置包 `errors.New()` 返回的是内部 errorString 对象的指针？

```golang
func New(message string) error {
    // 返回的是一个指针
	return &fundamental{
		msg:   message,
		stack: callers(),
	}
}
```

因为这样可以保证定义 2 个内容一致的 error 时，由于返回的是指针，指向的是不同地址，所以这两个 error 进行比较时不会相等。举例：

```golang

a := errors.New("hello")
b := errors.New("hello")

fmt.Println(a==b)
// false
```

## 为什么 Golang 选择 Error 作为异常处理的方式？

各个语言演进的历史：
- C 语言单值返回，传入指针作为入参，返回值为 int 表示成功或失败
- Java 引入 checked exception, 方法的所有者必须声明 `checked Exception` 才能抛出异常。这样的话，大量的异常没有区分等级。开发者通常 catch 父类 Exception 统一处理。
- Golang 区分 error 和 panic。Go panic 代表是异常（fatal error）和 error （良性错误）。recover 的场景是用来兜底的，而不能理解为 Java 中的 catch。

### 异常与ERROR
- 异常：是指不可恢复的错误，例如索引越界、不可恢复的环境问题、空指针等
- ERROR: 除异常外的其他错误，这些错误是可以处理的。

### Exception 的局限性
代码的任何一行都可能出错误，可能会破坏语义。

### 总结为什么 Golang 使用 Error
- 简单。
- 考虑失败，而不是成功（plan for failure, not succeess)
- 没有隐藏的控制流。（不会像 `try ... catch ..` 那样代码在发送异常时会跳转）
- 完全交给你来控制 Error
- Error are values。（Golang 官方Blog）


## 其他知识

`*` 星号能获取指针所指向的内容。


