---
layout:     post
title:      "Golang-error-02: Error Type"
subtitle:   ""
date:       2021-12-11 18:22:33
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## Sentinel Error

Sentinel Error, 使用特定的值表示错误。例子：

```golang
if err == ErrSomething {...}
```
### 局限性1：不灵活
这种方法不灵活，因为当使用 `errors.Wrap` 对 error 进行封装后，上面的判断就不成立了。举例：

```golang
// 对 Error 进行封装
err = errors.Wrapf(ErrSomething, "user %s", "foo")
// 此时下面对错误的判断变不再成立
if err == ErrSomething {...}
```
此时比较蹩脚的办法：
```golang
if strings.Contains(err.Error(), "xxx") {

}
```
### 局限性2：Sentinel errors 成为你 API 公共部分。
> 基础库设计原则：对外暴露的更少的方法，包使用更简单。

该特定错误必须是公开的，要有文档记录，这就会增加 API 的表面积。

（注：即暴露了更多的细节）

如果 API 定义了一个返回特定错误的 interface, 则该接口的所有实现都将被限制为仅返回该错误，即便它们能提供更具描述性的错误。

(注：由于 API 接口已经约定了返回该错误，所以该 API 接口的实现就只能返回该错误，不然的话就违背了这个约定，这样的话非常死板。)

举例：

```golang

var ErrUserNotFound = errors.New("user not found")

type User interface {
    // 当 err 为 ErrUserNotFound 时表示用户不存在
    Query(userID string)(UserInfo, error)
}

// 因为在接口文档中已经约定了用户不存在只能表示为 ErrUserNotFound, 那么对这个 User 接口的实现就很僵化。

type VipUser struct {}

func (v VipUser) Query(userID string)(UserInfo, error) {
    // 这个方法由于要与 User 接口保持一致
    // 在用户不存在时只能返回 ErrUserNotFound, 不能使用 errors.Wrap 等进行封装，以免用户直接使用等于判断是出错。
}

```
### 局限3：Sentinel errors 在两个包之间创建了依赖。
比如，检查错误类型是否等于 `io.EOF` ，必须导入 io 包。当需要对很多 error 进行类型判断时，包与包之间就容易出现循环依赖。

### 结论
不要模仿标准库，不建议平时开发中使用 sentinel errors。

## Error types

Error types: 通过实现 Error 接口，自定义一个 Error 类型。

标准库 `os.PathError` 实现了此方式。

```golang
type PathError struct {
	Op   string
	Path string
	Err  error
}

func (e *PathError) Error() string { return e.Op + " " + e.Path + ": " + e.Err.Error() }
```

可以通过 switch type 断言来处理 Error types:

```golang
func main(t *testing.T) {
	err := a()
	switch err := err.(type) {
	case nil:
		fmt.Println("it is nil")
	case *os.PathError:
		fmt.Printf("%s", err.Path)
	default:
		fmt.Printf("unknown err %v",err)
	}
}

func a() error {
    return os.PathError{Path:"/usr/local"}
}
```

### Error types 的缺点

优点：与使用错误值 Sentinel Error 相比，Error types 可以封装底层错误的更多的上下文信息。

缺点：与 Sentinel Error 一样，还是要将自定义的 error 暴露给调用者，增加了接口的表面积。

结论：尽量少用。

### Opaque errors 不透明错误

Opaque errors 依据的思想：Assert errors for behaviour, not type。不要通过类型而是通过行为断言错误。

标准库中的相关实现：`net.Error`
```golang
// An Error represents a network error.
type Error interface {
    // 组合内置的 error 接口
	error
	Timeout() bool   // Is the error a timeout?
	Temporary() bool // Is the error temporary?
}
```

实现 `net.Error` 的结构体。

```golang
// DNSError represents a DNS lookup error.
type DNSError struct {
	Err         string // description of the error
	Name        string // name looked for
	Server      string // server used
	IsTimeout   bool   // if true, timed out; not all timeouts set this
	IsTemporary bool   // if true, error is temporary; not all errors set this
	IsNotFound  bool   // if true, host could not be found
}

func (e *DNSError) Error() string {
	if e == nil {
		return "<nil>"
	}
	s := "lookup " + e.Name
	if e.Server != "" {
		s += " on " + e.Server
	}
	s += ": " + e.Err
	return s
}

func (e *DNSError) Timeout() bool { return e.IsTimeout }

func (e *DNSError) Temporary() bool { return e.IsTimeout || e.IsTemporary }
```

进行相关调用时，如果只关心是否有错误:

```golang
// net 包 lookup_test.go 中的测试用例：
// 关心是否是 Temporary 时，可以调用 Temporary 这个接口
if nerr,ok := err.(net.Error); ok && nerr.Temporary() {

}
```
不足：还是暴露了 `net.Error` 这个类型信息。

