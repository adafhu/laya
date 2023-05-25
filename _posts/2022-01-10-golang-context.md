---
layout:     post
title:      "Golang Context"
subtitle:   ""
date:       2022-01-10 16:11:40
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## WithCancel
`WithCancel` 函数签名：
```golang
func WithCancel(parent Context) (ctx Context, cancel CancelFunc)
```

`WithCancel` 函数签名解析
- 参数 `parent` 是 `context` 整体传播链路中的根`Context`。通常 `parent` 通过 `context.Background()` 生成。
- 返回值 `ctx` 的类型是结构体 `cancelCtx`。[`cancelCtx` 通过 embadding 的方式实现了 Context 接口](https://kougazhang.github.io/golang/2022/01/10/golang-interface/)
- 返回值 `cancel` 的类型是 `CancelFunc`。`CancelFunc` 会通知 work 中断。

`WithCancel` 的大致原理：
- 调用 `WithCancel` 方法会返回 2 个值 `ctx` 和 `cancel`。
- `ctx` 的类型是结构体 `cancelCtx`。`cancelCtx` 实现了接口 Context，所以后续需要 `Context` 的地方如下面的示例 `gen` 函数传入的就是 `ctx`。
- `cancelCtx` 实现的 `Done` 方法在第一次被调用时, 如果发现没有 `chan struct{}` 会进行创建。这就是 `cancelCtx` 中提到的 `craeted lazily`。未关闭且收不到任何消息的 `chan struct{}`，`select` 是不能读取到任何消息的。
- `cancel` 函数调用后会关闭 `chan struct{}`。`select` 读取关闭的 channel 时会返回 `nil`, 从而 goroutine 就会退出了。

```golang
func main() {
    // ctx 的类型是 cancelCtx
	gen := func(ctx context.Context) <-chan int {
		dst := make(chan int)
		n := 1
		go func() {
			for {
				select {
                // cancelCtx.Done 第一次被调用时会创建 chan struct{}
                // 当 cancel 执行时 chan struct{} 被关闭，select 会读取到 nil，从而整个 goroutine 结束.
				case <-ctx.Done():
					return // returning not to leak the goroutine
				case dst <- n:
					n++
				}
			}
		}()
		return dst
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel() // cancel when we are finished consuming integers

	for n := range gen(ctx) {
		fmt.Println(n)
		if n == 5 {
			break
		}
	}
}
```
