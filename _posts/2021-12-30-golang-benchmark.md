---
layout:     post
title:      "Golang Benchmark"
subtitle:   ""
date:       2021-12-30 11:16:59
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

使用 golang 内置的 `testing` 实现 benchmark。

首先在 `_test.go` 结尾的测试文件中实现一个 benchmark 用例：

```golang

// 函数名需要以 Benchmark 开头
// 参数是 *testing.B
func BenchmarkFib(b *testing.B) {
    for n:=0; n < b.N; n++ {
        fib(30)
    }
}
```

运行测试用例：
- 运行当前 package 内的用例：`go test .`
- 运行子 packge 内的用例：`go test ./<packagename>`
- 递归运行当前目录下的所有的 package: `go test ./...`

默认情况下，`go test` 命令不会执行 benchmark 用例的。想运行 benchmark 用例需要传递 `-bench` 参数。
- `go test -bench .`, 这样就会运行当前 package 内的用例。
- `go test -bench=regexp .`, 只有函数名匹配 regexp 的 benchmark 用例才会被执行。

## benchmark 是如何工作的？
`benchmark` 用例的参数 `b *testing.B`, 有个属性 `b.N` 表示这个用例需要运行的次数。`b.N` 对于每个用例都是不一样的。

`b.N` 这个值是如何决定的？`b.N` 从 1 开始，如果该用例能够在 1s 内完成，`b.N` 的值便会增加，再次执行。`b.N` 的值大概以 1,2,3,5,10,20... 这样的序列增加，越到后面增加得越快。

```
// BenchmarkFib-8, -8 即 GOMAXPROCS, 默认等于 CPU 核数。
// 可以通过 -cpu 参数改变 GOMAXPROCS, -cpu 支持传入一个列表作为参数, 可以看不同 CPU 核数下程序的性能
BenchmarkFib-8               202           5980669 ns/op
```

## benchmardk CPU 性能

对于性能测试来说，提升测试准确度的一个重要手段是增加测试的次数。我们可以使用 `-benchtime` 和 `-count` 两个参数达到这个目的。

`benchmark` 的默认时间是 1s，那么我们可以使用 `-benchtime` 指定为 5s。例如：

```
goos: darwin
goarch: amd64
pkg: camp/week03-concurrency/exercise/package-sync
cpu: Intel(R) Core(TM) i7-8850H CPU @ 2.60GHz
BenchmarkFib-12    	    1299	   4563221 ns/op
PASS
ok  	camp/week03-concurrency/exercise/package-sync	6.480s
```

`benchmark` 的值除了是时间外，还可以是具体的次数。例如，执行 30 次可以用 `-benchtime=30x`:

```
goos: darwin
goarch: amd64
pkg: camp/week03-concurrency/exercise/package-sync
cpu: Intel(R) Core(TM) i7-8850H CPU @ 2.60GHz
BenchmarkFib-12    	      50	   4632452 ns/op
PASS
ok  	camp/week03-concurrency/exercise/package-sync	0.722s
```

`-count` 参数可以用来设置 benchmark 的轮数。比如进行 3 轮 benchmark。

```
goos: darwin
goarch: amd64
pkg: camp/week03-concurrency/exercise/package-sync
cpu: Intel(R) Core(TM) i7-8850H CPU @ 2.60GHz
BenchmarkFib-12    	      50	   4632452 ns/op
PASS
ok  	camp/week03-concurrency/exercise/package-sync	0.722s
```

## 内存分配情况
`-benchmem` 参数可以度量内存分配的次数。内存分配次数也是和性能息息相关的。例如不合理的切片容量，将导致内存重新分配，带来不必要的内存开销。

```
goos: darwin
goarch: amd64
pkg: example
BenchmarkGenerateWithCap-8  43  24335658 ns/op  8003641 B/op    1 allocs/op
BenchmarkGenerate-8         33  30403687 ns/op  45188395 B/op  40 allocs/op
PASS
ok      example 2.121s
```

## 注意事项

### ResetTimer

如果在 benchmark 开始前，需要一些准备工作，如果准备工作耗时比较长，则需要将这部分代码的耗时忽略掉。

```golang
func BenchmarkFib(b *testing.B){
    // sleep 3 秒是一个耗时的操作，我们要排除他的干扰
    time.Sleep(time.Second*3)
    // 使用 ResetTimer 来排除干扰
    b.ResetTimer()
    for n:=0; n < b.N; n++ {
        fib(30)
    }
}
```

### StopTimer && StartTimer
每次函数调用前后需要一些准备工作和清理工作，我们可以使用 `StopTimer` 暂停计时以及使用 `StartTimer` 开始计时。

```golang
func BenchmarkBubbleSort(b *testing.B) {
    for n := 0; n < b.N; n++ {
        // 暂停计时
		b.StopTimer()
		nums := generateWithCap(10000)
        // 开始计时
		b.StartTimer()
		bubbleSort(nums)
	}
}
```


## 参考
- [benchmark 基准测试](https://geektutu.com/post/hpg-benchmark.html)

