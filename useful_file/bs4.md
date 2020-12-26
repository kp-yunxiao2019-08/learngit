- 以标签属性查询

  `soup.find(attrs={'class':'pages'})`

-	`div.page a`与`div.page>a`

  -	`div.page a`获取class属性为page的div下所有a标签
  -	`div.page>a`获取class属性为page的div下直接子标签a

  