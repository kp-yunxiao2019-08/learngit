```
urllib和urllib2模块之间的区别
在python中，urllib和urllib2不可相互替代的。

整体来说，urllib2是urllib的增强，但是urllib中有urllib2中所没有的函数。

urllib2可以用urllib2.openurl中设置Request参数，来修改Header头。如果你访问一个网站，想更改User Agent（可以伪装你的浏览器），你就要用urllib2.

urllib支持设置编码的函数，urllib.urlencode,在模拟登陆的时候，经常要post编码之后的参数，所以要想不使用第三方库完成模拟登录，你就需要使用urllib。

urllib一般和urllib2一起搭配使用
https://docs.python.org/3.5/library/urllib.html(官方文档 Python 3.5.2版本)
```

```
urllib.request.ProxyHandler(proxies=None)
导致请求通过一个代理。如果代理是给定的，它必须是一个字典的代理协议名称映射到url
```

- urllib.parse.urlencode(dict), `=`拼接键值对，`&`拼接每一对字符串

```
>>> import urllib.request
>>> import urllib.parse
>>> params = urllib.parse.urlencode({'spam': 1, 'eggs': 2})
>>> url = "http://www.baidu.com/query?%s" % params
>>> print(url)
"http://www.musi-cal.com/query?span=1&eggs=2
>>> with urllib.request.urlopen(url) as f:
...     print(f.read().decode('utf-8'))
```

