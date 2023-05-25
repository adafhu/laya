---
layout:     post
title:      "Golang Interview: 01"
subtitle:   ""
date:       2022-01-04 14:35:32
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## 1、make 与 new 区别
- `make` 的作用是初始化内置的数据结构，如切片、哈希表和 Channel
- `new` 的作用是根据传入的类型分配一片内存空间并返回指向这片内存空间的指针。

我们在代码中往往都会使用如下所示的语句初始化这三类基本类型，这三个语句分别返回了不同类型的数据结构：

```golang
slice := make([]int, 0, 100)
hash := make(map[int]bool, 10)
ch := make(chan int, 5)
```
1. `slice` 是一个包含 `data`、`cap` 和 `len` 的结构体 `reflect.SliceHeader`
2. `hash` 是一个指向 `runtime.hmap` 结构体的指针；
3. `ch` 是一个指向 `runtime.hchan` 结构体的指针；

`new` 的功能就简单多了，它只能接收类型作为参数然后返回一个指向该类型的指针：

```golang
i := new(int)

var v int
i := &v
```

上述代码片段中两种不同初始化方法是等价的，它们都会创建一个指向 `int` 零值的指针。

## make
refer: https://draveness.me/golang/docs/part1-prerequisite/ch02-compile/golang-typecheck/#%E5%85%B3%E9%94%AE%E5%AD%97-omake

`make` 是 Go 语言中常见的内置函数。在类型检查阶段之前，无论是创建切片、哈希还是 Channel 用的都是 `make` 关键字, 不过在类型检查阶段会根据创建的类型将 `make` 替换成特定的函数，后面 `生成中间代码` 的过程就不会再处理 `OMAKE` 类型的节点了，而是会根据生成的细分类型取处理：

```
make
- makechan
- makeslice
- makemap
```

编译器会先检查关键字 `make` 的第一个类型参数，根军类型的不同进入不同分支，切片分支 `TSLICE`, 哈希分支 `TMAP`, Channel 分支 `TCHAN`:

(我看的是 golang1.18 的代码，所以与 refer 中不同。现在是封装到 `tcMake` 的函数中)

```golang
// tcMake typechecks an OMAKE node.
func tcMake(n *ir.CallExpr) ir.Node {

    var nn ir.Node
	
    switch t.Kind() {
    default:
	    base.Errorf("cannot make type %v", t)
	    n.SetType(nil)
	    return n

	    case types.TSLICE:
        //...
        case types.TMAP:
        // ...
        case case types.TCHAN:
        // ..
    }
}
```
如果 `make` 的第一个参数是切片类型，那么就会从参数中获取切片的长度 `len` 和容量 `cap` 并对这两个参数进行校验：
- 切片的长度参数是否被传入；
- 切片的长度必须要小于或者等于切片的容量；

```golang
i := 1
// ...
    case types.TSLICE:
        // 缺少参数
		if i >= len(args) {
			base.Errorf("missing len argument to make(%v)", t)
			n.SetType(nil)
			return n
		}

        // l 是第 2 个参数 （make 函数中第一个参数是类型：slice、map 或 channel）
		l = args[i]
		i++
		l = Expr(l)
		var r ir.Node
        // r 是第 3 个参数
		if i < len(args) {
			r = args[i]
			i++
			r = Expr(r)
		}

        // make 函数中只传了一个类型参数，len 和 cap 都没有
		if l.Type() == nil || (r != nil && r.Type() == nil) {
			n.SetType(nil)
			return n
		}
    
		if !checkmake(t, "len", &l) || r != nil && !checkmake(t, "cap", &r) {
			n.SetType(nil)
			return n
		}
        // 切片的长度必须要小于或者等于切片的容量
		if ir.IsConst(l, constant.Int) && r != nil && ir.IsConst(r, constant.Int) && constant.Compare(l.Val(), token.GTR, r.Val()) {
			base.Errorf("len larger than cap in make(%v)", t)
			n.SetType(nil)
			return n
		}
		nn = ir.NewMakeExpr(n.Pos(), ir.OMAKESLICE, l, r)
```

第二种情况就是 `make` 的第一个参数是 `map` 类型，在这种情况下，第二个可选的参数就是哈希的初始大小，在默认情况下它的大小是 0：

```golang
case types.TMAP:
		if i < len(args) {
			l = args[i]
			i++
			l = Expr(l)
			l = DefaultLit(l, types.Types[types.TINT])
			if l.Type() == nil {
				n.SetType(nil)
				return n
			}
			if !checkmake(t, "size", &l) {
				n.SetType(nil)
				return n
			}
		} else {
            // 没有指定大小，则默认值是 0
			l = ir.NewInt(0)
		}
		nn = ir.NewMakeExpr(n.Pos(), ir.OMAKEMAP, l, nil)
		nn.SetEsc(n.Esc())
```

第三种情况是数据结构 `channel`, 第二个参数表示的是 Channel 缓冲区大小，如果不存在第二个参数表示的是 Channel 缓冲区的大小，如果不存在第二个参数，那么会创建缓冲区大小为 0 的 Channel:

```golang
case types.TCHAN:
		l = nil
		if i < len(args) {
			l = args[i]
			i++
			l = Expr(l)
			l = DefaultLit(l, types.Types[types.TINT])
			if l.Type() == nil {
				n.SetType(nil)
				return n
			}
			if !checkmake(t, "buffer", &l) {
				n.SetType(nil)
				return n
			}
		} else {
			l = ir.NewInt(0)
		}
		nn = ir.NewMakeExpr(n.Pos(), ir.OMAKECHAN, l, nil)
```

## new

编译器会在中间代码生成阶段通过一下两个函数处理该关键字：
1. `cmd/compile/internal/gc.callnew` 会将关键字转换成本 `ONEWOBJ` 类型的节点；
2. `cmd/compile/internal/gc.state.expr` 会根据申请空间的大小分两种情况处理：
    1. 如果申请的空间为 0，就返回一个表示空指针的 `zerobase` 变量；
    2. 在遇到其他情况时会将关键字转换成 `runtime.newobject` 函数：

在 golang1.18 中机制已经不一样了。作者说的代码没有找到。
