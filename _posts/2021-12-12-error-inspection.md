---
layout:     post
title:      "Golang-err04: Error Inspection"
subtitle:   ""
date:       2021-12-12 13:39:48
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## Errors before Go 1.13

### 最简单的错误检查：

```golang
if err != nil {}
```

### 对 sentinel error 进行检查：

```golang
var ErrNotFound = errors.New("not found")

if err == ErrNotFound {}
```

### 自定义 error struct, 使用断言获取更丰富的上下文信息：

```golang
type ErrNotFound struct{
    Name string
}

func (e *ErrNotFound) Error() string {
    return e.Name + ": not found"
}

// 断言
if e, ok := err.(*ErrNotFound); ok {
    // ...
}
```

### fmt.Errorf

上抛错误时使用 `fmt.Errorf` 封装 error，会丧失 root error。

```golang
if err != nil {
    return fmt.Errorf("decompress %v: %v", name, err)
}
```
### 使用 struct

所以使用 struct 的方式保留 root error:

```golang
type QueryError struct {
    error
    Query string
}
```
程序可以查看 `QueryError` 值以根据底层错误做决策：

```golang
if e, ok := err.(*QueryError); ok && e.Err == ErrPermission {
    // ...
}
```

## Go1.13
标准库引入了 `Is` 和 `As`。这个最大的变化是：包含另一个错误的 error 可以返回底层错误的 `Unwrap` 方法。如果 `e1.Unwrap()` 返回 e2, 那么可以说 e1 包装了 e2。

结合 Go1.13 之前的内容来讲改进就是，之前使用 struct 虽然保留了 root error，但是调用法需要使用断言的方式来获取 root error ，这样比较麻烦。现在的改进措施是，这个 struct 实现一个 `Unwrap` 的方法来返回 root error, 这样调用方就可以使用 `Is` 和 `As` 两个方法更加方便的判断错误了。

### errors.Is 替换 sentinel error

示例如下：

之前 `if err == ErrNotFound` 就可以使用 `errors.Is` 来替换：

```golang
type ErrNotFound struct {
	Name string
	Err  error
}

func (e *ErrNotFound) Unwrap() error {
	return e.Err
}

func (e *ErrNotFound) Error() string {
	return e.Name
}

func TestAny(t *testing.T) {
	rootErr := errors.New("root error")
	errNotFound := &ErrNotFound{
		Name: "foo",
		Err:  rootErr,
	}
	fmt.Println(errors.Is(errNotFound, rootErr))
}
```

### errors.As 替换类型断言

之前进行类型断言来判断错误：

```golang
if e, ok := err.(*QueryError); ok {
    // ...
}
```

现在使用 `errors.As` 来做更简单:

```golang 
func TestAny(t *testing.T) {
    // 接上面的例子
    
    // 先声明一个变量 e
	var e *ErrNotFound
    // 如果 errNotfound 是 ErrNotFound 类型，
    // 则 errNotFound 的值会赋给 e
    // errors.As 返回 true
	if errors.As(errNotFound, &e) {
        // 在判断内部就可以使用 ErrNotFound 的成员变量了
		fmt.Println(e.Name)
	}
}
```
### fmt.Errorf 支持新的 `%w` 谓词

```golang
if err != nil {
    return fmt.Errorf("name %v: %w", name, err)
}
```

用 `%w` 包装错误可用于 `errors.Is` 以及 `errors.As`:

```golang
err := fmt.Errorf("access denied: %w", ErrPermission)
if errors.Is(err, ErrPermission) {
    // ...
}
```

## 比较 Go1.13 与 pkg/errors

pkg/errors 实现了 Go1.13 的 Is 和 As 的接口，并且比 1.13 多出了 Wrap 等保留堆栈信息的功能。所以 pkg/errors 还是比较实用的。

## Go2

handle error 的方式。


