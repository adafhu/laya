---
layout:     post
title:      "Golang Interface"
subtitle:   ""
date:       2022-01-10 16:56:19
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## Embadding （内嵌）

在 effective go 中对于 embadding 有如下描述：

> Go does not provide the typical, type-driven notion of subclassing, but it does have the ability to “borrow” pieces of an implementation by embedding types within a struct or interface.

Go 没有提供典型的、类型驱动的子类概念，但是 Go 拥有 “借用” 内嵌结构体或接口部分实现的能力。（译者注：这种借用能力能够达到继承的效果）。

内嵌的几种情况，做了一个表格列举了一下：

|序号|类型|内嵌类型|是否支持|
|---|---|---|---|
|1|struct|struct|yes|
|2|struct|interface|yes|
|3|interface|struct|no|
|4|interface|interface|yes|

其中1 和 4 是比较常见的，对于第 2 种情况 `struct` 内嵌 `interface` 又该作何理解呢？

从 effective go 可知，“内嵌” 可以使得被嵌入方可以“借用” 内嵌方的能力。所以`struct` 内嵌 `interface` 后就可以调用 `interface` 的所有方法，相当于实现了 `interface` 这个接口。

使用场景：`struct` 可以按需实现 `interface` 接口中的方法。

举例: 内置包 `context/context.go` 中 `cancelCtx` 内嵌了 interface `Context`

```golang
type cancelCtx struct {
	// 内嵌 Context
    Context

	mu       sync.Mutex            // protects following fields
	done     atomic.Value          // of chan struct{}, created lazily, closed by first cancel call
	children map[canceler]struct{} // set to nil by the first cancel call
	err      error                 // set to non-nil by the first cancel call
}

// cancelCtx 只实现了 Context 3 个接口
func (c *cancelCtx) Value(key any) any {}
func (c *cancelCtx) Done() <-chan struct{} {}
func (c *cancelCtx) Err() error {}
```

自己写个例子, [embadding](https://gist.github.com/kougazhang/6808c01fda9f2794e2c703bbb5ccb842)


### 参考
- [effective go](https://go.dev/doc/effective_go#embedding)
- [stackoverflow: Meaning of a struct with embedded anonymous interface?](https://stackoverflow.com/questions/24537443/meaning-of-a-struct-with-embedded-anonymous-interface)
