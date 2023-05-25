---
layout:     post
title:      "Golang Pointer"
subtitle:   ""
date:       2021-12-21 10:17:23
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## Golang 指针的三种操作
- `*` 定义指针类型：`var p *string` 定义一个 `*string` 类型的指针
- `&` 对非指针变量取地址：`var str string; p = &str`, 取 `str` 的地址，赋值给指针变量 `p`
- `*` 对指针取值：`str = *p`, 取指针变量 `p` 指向的值，赋给变量 `str`

## 指针作为函数参数

函数参数是基本类型时，一般都是值拷贝的形式。也就是说，在函数内修改参数不会影响到原来的值，因为它是做了一次拷贝。

```golang
var a = 1
func foo(a int) {
    a=2
}
fmt.Println(a) // 1
```

把指针作为函数参数时，就是“值引用” 的形式。在函数内修改参数会影响到原来的值。

```golang
var a = 1
func foo(a *int) {
    // *a 是对指针取值
    // *a = 2 是把指针a 指向的值改改为指向2
    *a=2
}
fmt.Println(a) // 2
```
