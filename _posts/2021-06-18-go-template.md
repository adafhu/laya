---
layout:     post
title:      "Golang template 小抄"
subtitle:   ""
date:       2021-06-18 11:11:00
author:     "kgzhang"
catalog: false
category: golang
header-style: text
tags:
  - golang
---

Go标准库提供了几个package可以产生输出结果，而text/template 提供了基于模板输出文本内容的功能。html/template则是产生 安全的HTML格式的输出。

## golang template API

### template.New

模板名称，多个模板渲染的话，不能重复, 最好以模板的名称作为 New 的参数。

```go
src := "xx.tpl"
template.New(filepath.Base(src))
```

### template.Funcs

自定义模板变量 parse 函数。

```go
tpl, err := template.New(filepath.Base(src)).Funcs(template.FuncMap{
    "capital": strings.Title,
}).ParseFiles(src)
```

模板中使用：

{% raw %}
```shell
{{ .Name| capital }}
```
{% endraw %}

### ParseFiles

`ParseFiles` parse 模板， 例子见上。

### Execute

输出渲染结果到文件

```go
err = tpl.Execute(file, data)
if err != nil {
  log.Fatal(err)
}
```

## 模板语法

### 使用变量
- 变量需要与传入的 struct 成员的首字母的大小写保持一致；
- 变量前面需要加 `.`

{% raw %}
```shell
{{ .Name }}
```
{% endraw %}

### 变量赋值

{% raw %}
```shell
# 外部传入的变量 Job 赋值给 counter
{{ $counter := .Job }}
```
{% endraw %}

### if 条件

{% raw %}
```shell
{{ if .<condition> }}
  // action ...
{{- end }}
```
{% endraw %}

### 逻辑比较
- eq: arg1 == arg2
- ne: arg1 != arg2
- lt: arg1 < arg2
- le: arg1 <= arg2
- gt: arg1 > arg2
- ge: arg1 >= arg2

逻辑比较在 `if` 中使用:

{% raw %}
```shell
{{- if lt $counter $pvdLength }},{{- end }}
```
{% endraw %}

### 迭代 Range

语法模板如下所示：
{% raw %}
```shell
{{- range $key,$val := .Pvds}}
    key is {{$key}}
    val is {{$val}}
{{- end }}
```
{% endraw %}

释义：
- `range` 迭代的对象可以是 slice、dict 等; 整个语法结构也与 range 等价 
{% raw %}
- 在 range 中的变量必须使用 `{{$}}` 的形式，其他变量传入时需要重新赋值。
{% endraw %}

### 消除空格
默认情况下，模板表达式会在输出结果中占一行空格，为了消除这样空格可以使用 `-`, 示例如下:

{% raw %}
```shell
{{- }}
```
{% endraw %}

## 实战

### 累加

golang template 不支持直接进行累加，需要自己实现：

1. 先实现一个累加函数：

```golang
tpl, err := template.New(filepath.Base(src)).Funcs(template.FuncMap{
    "inc": func(i int) int {
			return i + 1
		},
}
```

2. 在 `range` 中实现累加

{% raw %}
```shell
// 变量赋值
{{- $pvdLength := (len .Job) }}
{{- $counter := 0 }}
// 使用 range 迭代变量
{{- range $key,$val := .Pvds}}
  {{- $counter = inc $counter }}
  "{{$key}}": {
  "window": {
  "start": "{{$val.Window.Start}}",
  "end": "{{$val.Window.End}}"
    },
  "pvd_conf_path": "/home/filex/{{$job}}/etc/pvd/{{$key|slash2underline}}.json"
  }{{- if lt $counter $pvdLength }},{{- end }}
{{- end}}
```
{% endraw %}

## 参考
+ [[译]Golang template 小抄](https://colobu.com/2019/11/05/Golang-Templates-Cheatsheet/#%E8%A7%A3%E6%9E%90%E5%92%8C%E5%88%9B%E5%BB%BA%E6%A8%A1%E6%9D%BF)
+ [gist: 渲染模板-filex ctl](https://gist.github.com/kougazhang/4b996d733a454b8b34201a7a6683c54a)
