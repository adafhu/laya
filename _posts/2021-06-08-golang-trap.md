---
layout:     post
title:      "Golang 语言中的陷阱"
subtitle:   "Golang trap"
date:       2021-06-08 21:24:00
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## for 循环中使用指针变量

### 示例 1

```go
func main() {
	var out []*int
	for i := 0; i < 3; i++ {
		out = append(out, &i)
	}
	fmt.Println("Values:", *out[0], *out[1], *out[2])
	fmt.Println("Addresses:", out[0], out[1], out[2])
}

// 输出
// Values: 3 3 3
// Addresses: 0x40e020 0x40e020 0x40e020
```

原因： 

> in each iteration we append the address of i to the out slice, but since it is the same variable, we append the same address which eventually contains the last value that was assigned to i。
> 在每个迭代中我们把 i 的地址添加到 out 切片，但是它们都是同一个变量，我们添加的变量 i 的地址最终会指向最后一次迭代时 i 被赋予的值。（也就是 3）。

### 示例 2

```go
func main() {
	arr1 := []int{1, 2, 3}
	arr2 := make([]*int, len(arr1))

	for i, v := range arr1 {
		arr2[i] = &v
	}

	for _, v := range arr2 {
		fmt.Println(*v)
	}
```

`for ... range ...` 是 for 循环的语法糖，根据 [go编译源码](https://github.com/golang/gofrontend/blob/e387439bfd24d5e142874b8e68e7039f74c744d7/go/statements.cc#L5501) 可知，上述代码会被编译成：

```go
func main() {
	arr1 := []int{1, 2, 3}
	arr2 := make([]*int, len(arr1))

	var v int
	for i:=0;i<len(arr1);i++ {
		v = arr1[i]
		arr2[i] = &v
	}

	for _, v := range arr2 {
		fmt.Println(*v)
	}
}
```

所以还是会存在示例 1 中的问题。

## for 循环与 goroutine

### 示例 1
```go
for _, val := range values {
	go func() {
		fmt.Println(val)
	}()
}
```

### 示例 2
```go
func main() {
	var s sync.WaitGroup
	for i := 0; i < 30; i++ {
		s.Add(1)
		go func() {
			fmt.Println(i)
			s.Done()
		}()
	}
	s.Wait()
}
```

> The above for loops might not do what you expect because their val variable is actually a single variable that takes on the value of each slice element. Because the closures are all only bound to that one variable, there is a very good chance that when you run this code you will see the last element printed for every iteration instead of each value in sequence, because the goroutines will probably not begin executing until after the loop.
  
摘自 https://github.com/golang/go/wiki/CommonMistakes#using-reference-to-loop-iterator-variable

golang 的 wiki 的解释不准确 "because the goroutines will probably not begin executing until after the loop"，goroutine 不一定会在 loop 之后运行，运行示例2有时会输出 4、9 等值，这说明 goroutine 被另一个线程调度，运行时间不固定。

当然上面这句话不是本例子的重点。重点是，for 循环只创建了一个变量 i，goroutine 运行时会读取变量 i 的值，又因为 goroutine 很可能是被另外一个线程调度的，运行的时间不定，所以 i 的值也不定。也就是说，上面的代码中迭代看似是顺序执行的，但是实际上 goroutine 的执行是乱序的。

### 实例3
不仅是 for 循环中创建的变量，即使是自增变量依旧可能会发生异常。这用上面的例子解释是 ** goroutine 的执行是乱序的**

[Bug参考](https://github.com/kougazhang/filex-v3-final/issues/180)

```go
for _, val := range values {
	go func() {
		fmt.Println(val)
	}()
}
```

## for ... select 中使用 default

详见 [pprof 全面解析](https://kougazhang.github.io/2021/05/29/pprof/) 中 【使用 pprof 优化 CPU 跑满的问题】 的问题。

## channel 什么时候会阻塞

### 向已满的 channel 发送数据会阻塞
```golang
func main(){
	a := make(chan interface{})
    a <- struct{}
    fmt.Println("hello")
}
```

### channel 没有接收到数据时读取该 channel 的数据会阻塞
```golang
func main() {
  a := make(chan interface{}, 1)
  fmt.Println(<-a)
  fmt.Println("hello world")
}
```
- issue: [读取空的 channel 到底会不会阻塞？](https://github.com/kougazhang/private/issues/46)
- bugfix: [第一个文件上半部分](https://github.com/kougazhang/filex-v3-final/pull/171/files#)

### 向关闭的 channel 发送数据会 panic
读取关闭的 channel 时不会有问题，如果 channel 有缓存数据则会返回缓存数据，如果 channel 为空则返回 nil。
```golang
func main() {
  a := make(chan interface{}, 1)
  close(a)
  a <- struct{}
}
```
这个知识点知道，但是容易发生错误的点是：误以为已经没有生产者向 channel 发送数据了，关闭 channel 以便使得接下来的 for 循环能够正常中断，结果造成了 Bug。[bugfix](https://github.com/kougazhang/filex-v3-final/pull/171/files#)
