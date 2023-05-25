---
layout:     post
title:      "Golang-err03: Handling Error"
subtitle:   ""
date:       2021-12-11 21:23:28
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

## 错误类型

已介绍的几种 Error Type:
- Sentinel Error
- 自定义的错误类型
- OpError: 不透明的错误类型

## 更友好地处理方式

### 1 无错误的正常代码将成为 1 条直线
> Indented flow is for errors

不要正常的业务逻辑写到 `err == nil` 中，如下是不鼓励的写法:

```golang
file,err := os.Open(path)
if err == nil {
    // do something ...
}
return err
```

鼓励的写法:
```golang
file,err := os.Open(path)
if err != nil {
    return err
}
// do something ...
```
### 2 程序中最后 1 个 Error 不用处理，直接返回就好

Bad Case:

```golang
func AuthenticateRequest(r *Request) error {
    // biz logic ...

    err := authenticate(r.User)
    if err != nil {
        return err
    }
    return nil
}
```

Good Case:
```golang
// 因为 authenticate 是最后一步，所以这个 error 是不需要判断的.
func AuthenticateRequest(r *Request) error {
    // biz logic ...

    return authenticate(r.User)
}
```

### 3 Scanner 扫描器的例子
`bufio.NewScanner` 更优雅地处理错误。

普通情况下读写文件:

```golang
func CountLines(r io.Reader) (int, error) {
    var (
        br = bufio.NewReader(r)
        lines int
        err error
        )

        for {
            _, err = br.ReadString('\n')
            lines++
            if err != nil {
                break
            }
        }

    if err != io.EOF {
        return 0,err
    }
    return lines, nil
}
```

使用 Scanner 简化读取文件：
```golang
// 整体上看使用 NewScanner 比上面简洁不少
func CountLines(r io.Reader) (int, error) {
    sc := bufio.NewScanner(r)
    lines := 0

    // Scan 在读完或者遇到错误时就会返回 False
    for sc.Scan() {
        lines++
    }

    // 一定要返回 sc.Err(), 它会把读取文件中遇到的第一个错误记录下来
    return lines, sc.Err()
}
```

### 4 HTTP 请求封装 error 的例子

普通情况下写入 response:

```golang
type Header struct {
    Key, Value string
}

type Status struct {
    Code int
    Reason string
}

func WriteResponse(w io.Writer, st Status, header []Header, body io.Reader) error {
    _, err := fmt.Fprintf(w, "HTTP/1.1 %d %s\r\n", st.Code, st.Reason)
        if err != nil {
            return err
        }

    for _,h := range headers {
        _, err := fmt.Fprintf(w, "%s: %s\r\n", h.Key, h.Value)
        if err != nil {
            return err
        }
    }

    if _,err := fmt.Fprintf(w, "\r\n"); err != nil {
        return err
    }

    _, err = io.Copy(w, body)
    return err
}
```

简化的思想就是封装一个带 error 的结构体，把对 error 的处理封装起来，尽可能的服用。调用方最后一次再处理异常。

```golang
type errWriter struct {
    // 组合了 io.Writer
    io.Writer
    err error
}

func (e *errWriter) Write(buf []byte) (int, error) {
    // 这个地方的封装在于，如果 e.err != nil
    // 后续的内容就写不进去了。这里就直接返回了。
    if e.err != nil {
        return 0, e.err
    }

    var n int
    // 这里通过定义了 n，来使得 e.err 能够重新被赋值
    n, e.err = e.Writer.Write(buf)
    return n, nil
}
```

使用 `errWriter` 替换内置的 `io.Writer`:

```golang
func WriteResponse(w io.Writer, st Status, headers []header, body io.Reader) error {
    ew := &errWriter{Writer: w}
    fmt.Fprintf(ew, "HTTP/1.1 %d %s\r\n", st.Code, st.Reason)

    for _,h := range headers {
        fmt.Fprintf(ew, "%s: %s\r\n", h.Key, h.Value)
    }

    fmt.Fprint(ew, "\r\n")
    io.Copy(ew, body)

    return ew.err
}
```
## Wrap errors: 包裹错误生成的上下文
> 原则：you should only handle errors once. Handling an error means inspecting the error value, and making a single decision.

Bad case1, 重复记录日志:

```golang
func Foo() error{
    if err != nil {
        // 这里处理了 2 次错误
        log.Errorf("err %v", err)
        return err
    }
    return nil
}
```
应该在什么情况下记录日志？
- 错误要被日志记录
- 应用程序处理错误，保证 100% 完整性
- 之后不再报告该错误。

### pkg/errors

常用 API：
- `errors.Cause`, 获取原始 error，然后就可以使用 sentinel error 比较了。
- `errors.New/Errorf`, 创建 error
- `errrors.Wrap/Wrapf`, wrap error

使用 `pkg/errors` 来 wrap error 信息的一些原则：
- 在你的应用代码中，使用 `errors.New` 或 `errors.Errorf` 返回错误。
- 如果调用其他包内的函数，通常简单的直接返回。
- 调用第三方库时使用 `errors.Wrap` 对 error 进行封装。
- 直接返回错误，不是每个错误产生的地方打日志。
- 在程序的顶部或是工作的 goroutine 顶部，使用 `%+v` 把堆栈信息记录下来。

需要注意的是，`pkg/errors` 这个包具有入侵性的，只能对使用 `errors.New` 或 `errors.Errorf` 打印出堆栈。这一点可以从 `errors.Errorf` 的实现看出来：

```golang
func Errorf(format string, args ...interface{}) error {
	return &fundamental{
		msg:   fmt.Sprintf(format, args...),
        // 记录堆栈
		stack: callers(),
	}
}
```
完整的例子：

```golang
func a() error {
	return errors.Errorf("i am a")
}

func b() error {
	err := a()
	return errors.Wrap(err, "b:")
}

func TestAll(t *testing.T) {
	err := errors.Cause(b())
    // 此时使用 %+v 可以打印堆栈
	fmt.Printf("\n%+v\n", err)
}
```

总结：

- Packages that are reusable across many projects only return root error values.

写基础库时不应该 wrap error, 而应该直接返回 root error，如果也使用 `pkg/errors` 对 error 进行封装，那么调用者打印堆栈时就会看到二个堆栈信息。

所以业务代码可以使用 `pkg/errors`，基础库不该使用。

- If the error is not going be handled, wrap and return up the call stack.

如果当前的函数不想处理这个错误，就该把这个错误封装一下携带上堆栈信息往上抛。

- Once an error is handled, it is not allowed to be passed up the call stack any longer.

如果 error 处理过，比如记录了日志，那么这个 error 就不要再往上抛了。
