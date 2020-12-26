- python字符串与url编码的转换

  ```python
  from urllib import parse
  poet_name = "李白"
  url_code_name = parse.quote(poet_name)
  print(url_code_name)
  ```

  

