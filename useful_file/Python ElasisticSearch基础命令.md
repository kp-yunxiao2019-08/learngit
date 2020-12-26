ElasisticSearch [https://elasticsearch-py.readthedocs.io/en/master/api.html?highlight=exists_alias#elasticsearch.client.IndicesClient.exists_alias]

- 创建连接
  - `es = Elasticsearch([self.host, self.por])`

- 获取所有索引
  - `es.indices.get_alias()`

```python
from elasticsearch import ElasticSearch

# 创建elasticsearch连接对象
es = Elasticsearch([host, por])

# 获取所有索引
es.indices.get_alias()

# 查看索引是否已存在
es.indices.exsits(index_name)
es.indices.exists_alias(alias_name, index_name)

# 创建索引
es.indices.create(index_name)

# 查
es.search()

# 更新索引别名
es.indices.update_alias(body, params=None, headers=None) [https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-aliases.html]

```



