ES_TEST

- *Elasticsearch* 是一个实时的分布式搜索分析引擎，它能让你以前所未有的速度和规模，去探索你的数据。 它被用作全文检索、结构化搜索、分析以及这三个功能的组合

- 不需要配置——只需要添加数据并开始搜索！

- `query DSL`查询表达式

- ```sh
  ./bin/elasticsearch
  bin/kibana
  http://localhost:5601/app/kibana#/dev_tools/console?_g=()
  ```
  
  ```python
  # mapping 的精髓
  PUT my-index-000001
  {
    "settings": {
      "analysis": {
        "filter": {
          "autocomplete_filter": {
            "type": "edge_ngram",
            "min_gram": 1,
            "max_gram": 20
          }
        },
        "analyzer": {
          "autocomplete": { 
            "type": "custom",
            "tokenizer": "standard",
            "filter": [
              "lowercase",
              "autocomplete_filter"
            ]
          }
        }
      }
    },
    "mappings": {
      "properties": {
        "text": {
          "type": "text",
          "analyzer": "autocomplete", 
          "search_analyzer": "standard" 
        }
      }
    }
  }
  
  PUT my-index-000001/_doc/1
  {
    "text": "Quick Brown Fox" 
  }
  
  GET my-index-000001/_search
  {
    "query": {
      "match": {
        "text": {
          "query": "Quick Br", 
          "operator": "and"
        }
      }
    }
  }
  ```
  

data

```python
# id = 1
{
    "first_name" : "John",
    "last_name" :  "Smith",
    "age" :        25,
    "about" :      "I love to go rock climbing",
    "interests": [ "sports", "music" ]
},
# id = 2
{
    "first_name" :  "Jane",
    "last_name" :   "Smith",
    "age" :         32,
    "about" :       "I like to collect rock albums",
    "interests":  [ "music" ]
},
# id = 3
{
    "first_name" :  "Douglas",
    "last_name" :   "Fir",
    "age" :         35,
    "about":        "I like to build cabinets",
    "interests":  [ "forestry" ]
}

```

```python
# 取回多个 _megt
GET /website/blog/_mget
{
   "docs" : [
      { "_id" : 2 },
      { "_type" : "pageviews", "_id" :   1 }
   ]
}
GET /website/blog/_mget
{
   "ids" : [ "2", "1" ]
}

# 更新多个 _bulk

```



```python
# 请求方式 /索引名/类型名/搜索
GET /meracorp/employee/_search
{
  "query":{
    "match": {
      "last_name": "Smith"
    }
  }
}

# 搜索"last_name"为"Smith"，"age"大于30
# 结果为数据2
GET /megacorp/employee/_search   
{
  "query": {
    "bool": {
      "match": {
        "last_name": "Smith"
      },
      "filter": {
        "range": {
          "age": {"gt": 30}
        }
      }
    }
  }
}

# 全文搜索 match（默认为`或`）, 搜索含rock或climbing的数据
# 结果为数据1、2。且1在2之前，相关性！
GET /megacorp/employee/_search 
{
  "query": {
    "match": {
      "about": "rock climbng"
    }
  }
}

# 精确搜索 match_parse(短语搜索),搜索含rock climbing的数据
# 结果为数据1
GET /megacorp/employee/_search
{
  "query": {
    "match_parse": {
      "about": "rock climbing"
    }
  }
}

# 高亮搜索 highlight
# 结果为数据1，但会多出highlight字段并以<em标签标出匹配到的字符串
#  "highlight": {
#               "about": [
#                  "I love to go <em>rock</em> <em>climbing</em>" 
#               ]
#            }
GET /megacorp/employee/_search
{
  "query": {
    "match_parse": {
      "about": "rock climbing"
    }
  },
  "highlight": {
    "fields": {
      "about": {}
    }
  }
}

# 聚合搜索 aggs, 挖掘出最受欢迎的兴趣爱好
# 结果包含
#"aggregations": {
#      "all_interests": {
#         "buckets": [
#            {
#               "key":       "music",
#               "doc_count": 2
#            },
#            {
#               "key":       "forestry",
#               "doc_count": 1
#            },
#            {
#               "key":       "sports",
#               "doc_count": 1
#            }
#         ]
#      }
#   }
GET /megacorp/employee/_search
{
  "aggs": {
    "all_instersts": {
      "terms": {"field": "instersts"}
    }
  }
}

# 增加筛选条件的聚合
#  "all_interests": {
#     "buckets": [
#        {
#           "key": "music",
#           "doc_count": 2
#        },
#        {
#           "key": "sports",
#           "doc_count": 1
#        }
#     ]
#  }
GET /megacorp/employee/_search
{
  "qeury": {
    "match": {
      "last_name": "Smith"
    }
  },
  "aggs": {
    "all_instersts": {
      "terms": {"field": "instersts"}
    }
  }
}

# 聚合分级汇总, 查看当前instersts的人数及平均年龄
# terms、term精确匹配
#  "all_interests": {
#     "buckets": [
#        {
#           "key": "music",
#           "doc_count": 2,
#           "avg_age": {
#              "value": 28.5
#           }
#        },
#        {
#           "key": "forestry",
#           "doc_count": 1,
#           "avg_age": {
#              "value": 35
#           }
#        },
#        {
#           "key": "sports",
#           "doc_count": 1,
#           "avg_age": {
#              "value": 25
#           }
#        }
#     ]
#  }
{
  "aggs": {
    "all_insterst": {
      "terms": {"field": "instersts"},
      "aggs": {
        "avg_age": {
          "avg": {"field": "age"}
        }
      }
    }
  }
}
```

分布式特性：

```Python
# 自动执行
分配文档到不同的容器 或 分片 中，文档可以储存在一个或多个节点中
按集群节点来均衡分配这些分片，从而对索引和搜索过程进行负载均衡
复制每个分片以支持数据冗余，从而防止硬件故障导致的数据丢失
将集群中任一节点的请求路由到存有相关数据的节点
集群扩容时无缝整合新节点，重新分配分片以便从离群节点恢复
```

- __节点__：一个运行中的 Elasticsearch 实例称为一个节点
  
  - 每个节点都知道任意文档所处的位置(类比域名映射)，并且能够将我们的请求直接转发到存储我们所需文档的节点
  - 主节点并不需要涉及到文档级别的变更和搜索等操作
  
- __集群__：由一个或者多个拥有相同 `cluster.name` 配置的节点组成，它们共同承担数据和负载的压力
  
  - 当有节点加入集群中或者从集群中移除节点时，集群将会重新平均分布所有的数据。
  
- __索引__ ： 保存相关数据的地方。 索引实际上是指向一个或者多个物理 *分片* 的 *逻辑命名空间*

-  __分片__： 是一个底层的 *工作单元* ，
  - 它仅保存了全部数据中的一部分，它本身就是一个完整的搜索引擎
  - 但应用程序是直接与索引而不是与分片进行交互
  - 分片是数据的容器，文档保存在分片内，分片又被分配到集群内的各个节点里
  - 一个分片可以是 *主* 分片或者 *副本* 分片。 索引内任意一个文档都归属于一个主分片，所以主分片的数目决定着索引能够保存的最大数据量
  - 一个副本分片只是一个主分片的拷贝，为搜索和返回文档等读操作提供服务以及数据备份功能
  - 索引建立的时候就已经确定了主分片数，但是副本分片数可以随时修改。
  
- 相同分片的副本不会放在同一节点
  
  - 当索引一个文档的时候，文档会被存储到一个主分片中
  
- __文档__。唯一标识：一个文档的 `_index` 、 `_type` 和 `_id` 唯一标识一个文档

  - 指最顶层或者根对象, 这个根对象被序列化成 JSON 并存储到 Elasticsearch 中，指定了唯一 ID。
  - 元数据之源数据必须元素
    - `_index`: 文档存储的地方（类比数据库库名）
      - 一个 *索引* 应该是因共同的特性被分组到一起的文档集合
      - 索引名必须小写，不能以下划线开头，不能包含逗号
    - `_type`: 文档表示对象类别（类比数据库中的表名）
      - 明确定义一些数据中的子分区（区分字段）
    - `_id`: 文档唯一标识
      - 字符串类型
      - 和 `_index` 以及 `_type` 组合就可以唯一确定 Elasticsearch 中的一个文档
      - 自定义`_id`需要用`PUT /{index}/{type}/{id}`
      - 用ES自动生成的`_id`需要用`POST /{index}/{type}/`
  - `_version`
    - 在 Elasticsearch 中每个文档都有一个版本号。当每次对文档进行修改时（包括删除）， `_version` 的值会递增。 
    - 在 [处理冲突](https://www.elastic.co/guide/cn/elasticsearch/guide/current/version-control.html) 中，使用 `_version` 号码确保应用程序中的一部分修改不会覆盖另一部分所做的修改。

- 检索独立性。

  - 每个子请求都是独立执行，因此某个子请求的失败不会对其他子请求的成功与否造成影响。

- 非原子性

  - `bulk` 请求不是原子的： 不能用它来实现事务控制
  - 原子性：
    - 一个事务包含多个操作，这些操作要么全部执行，要么全都不执行。实现事务的原子性，要支持回滚操作，在某个操作失败后，回滚到事务执行之前的状态。

- __字段__

  - `hits` : `dict`
    - `hits.total` : 表示匹配到的文档总数。`int`
    - `hits.hits` : 包含所查询结果的前十个文档。`list`
      - 每个文档：
        -  `_index` 、 `_type` 、 `_id`  ：唯一标识
        - `_source` ：文档数据内容。`dict`
        - `_score` : 衡量文档与查询的匹配程度的得分。`int`
    - `hits.max_score` : 与查询所匹配文档的 `_score` 的最大值。`int`
  - `took` : 执行整个搜索请求耗费的时间，单位毫秒。`int`
  - `_shards` : 查询中参与分片的总数，以及这些分片成功数量失败数量
  - `time_out` : 查询是否超时
    - 通常不会超时
    - 请求时可以设置参数`_search?timeout=10ms`
    - 在请求超时之前，ES 将会返回已经成功从每个分片获取的结果

- `简单搜索`与`_all`字段

  - 如`/_search?q=mary`
  - 当索引一个文档的时候，ES 取出所有字段的值拼接成一个大的字符串，作为 `_all` 字段(string类型)进行索引，`_all`字段含`mary`则返回该文档

- ES数据分类

  - 精确值
    - 日期、用户ID、邮箱等
  - 全文
    - 文本数据

- 倒排索引

  - 分析：分词和标准化的过程
    - 将一块文本分成适合于倒排索引的独立的 *词条*
    - 将这些词条统一化为标准格式以提高它们的“可搜索性”，或者 *recall*
  - 分析器：执行分词和标准化的工具。
    - 字符过滤器
      - 在分词前整理字符串。可以用来去掉HTML，或者将 `&` 转化成 `and`等
    - 分词器
      - 将字符串分为词条。简单的分词器遇到空格和标点的时候，可能会将文本拆分成词条。
    - Token过滤器
      - 处理词条。
      - 这个过程可能会改变词条（例如，小写化 `Quick` ），删除词条（例如， 像 `a`， `and`， `the` 等无用词），或者增加词条（例如，像 `jump` 和 `leap` 这种同义词）。

- 什么时候使用分析器

  - 当查询全文域时，会对查询字符串用相同的分析器处理，以产生匹配的搜索词条列表
  - 当查询精确值域时，不会分析字符串查询，而是搜索精确字符串
  - 例：日期 `2020-07-11`
    - 在全文域搜索会被分词为`2020`、`07`、`11`，含有这三个字符串的文档都会被作为查询结果返回
    - 在精确值域只会返回含`2020-07-11`的文档

- 常用分析器（ES自带分析器）

  - 标准分析器：`standard`
    - `standard` 分词器，通过单词边界分割输入的文本。
    - `standard` 语汇单元过滤器，目的是整理分词器触发的语汇单元（但是目前什么都没做）。
    - `lowercase` 语汇单元过滤器，转换所有的语汇单元为小写。
    - `stop` 语汇单元过滤器，删除停用词—对搜索相关性影响不大的常用词，如 `a` ， `the` ， `and` ， `is` 。
  - 空白分析器：`whitespace`
  - 简单分析器：`simple`
  - 英语分析器：`english`

- 测试分析器

  -  `analyze` API 来可以看文本是如何被分析的。需指定分析器和查询文本

  - 例：

    - ```Python
      GET /_analyze
      {
      	"analyzer": "standard",
      	"text": "text to anasyze"
      }
      ```

    - 结果中每一个元素代表一个词条

      ```python
      {
         "tokens": [
            {
               "token":        "text",
               "start_offset": 0,
               "end_offset":   4,
               "type":         "<ALPHANUM>",
               "position":     1
            },
            {
               "token":        "to",
               "start_offset": 5,
               "end_offset":   7,
               "type":         "<ALPHANUM>",
               "position":     2
            },
            {
               "token":        "analyze",
               "start_offset": 8,
               "end_offset":   15,
               "type":         "<ALPHANUM>",
               "position":     3
            }
         ]
      }
      ```

    - `token` 是实际存储到索引中的词条。 `position` 指明词条在原始文本中出现的位置。 `start_offset` 和 `end_offset` 指明字符在原始字符串中的位置。

- 映射（域：字段）

  - 映射定义了类型中的域，每个域的数据类型

  - 查看映射(查看指定索引[库]的指定类型[表]的映射[schema])

    - ```shell
      GET /{index}/_mapping/{type}
      ```

    - ```python
      {
      	{index}: {
      		mappings: {
      			{type}: {
      				properties: {
      					field: {type: string}
      				}
      			}
      		}
      	}
      }
      ```

- 自定义域映射

  - 域最重要的属性是 `type` 。对于不是 `string` 的域，只需要设置 `type` 

  - `string` 域映射的两个最重要属性是 `index` 和 `analyzer`
  
    - `index` :
  
      - `analysed` : 分析字符串，再做全文索引这个域
  
      - `not_analysed` ：不分析字符串，精确索引这个域
  
      - `no` ：不索引这个域
  
      - `index`默认属性为`analysed`，若想映射某个字符串域为精确索引，需要设置它为`no_analysed`
  
        ```Python
        {
          "properties": {
            	{field}: {
              	  "type":     "string",
                	"index":    "not_analyzed"
            }
          }
        }
        ```
  
    - `analyser`分析器
  
      - ES默认使用`standard`分析器，可以自定义指定一个内置分析器
  
      - ```python
        {
            {field}: {
                "type":     "string",
                "analyzer": "english"
            }
        }
        ```

- 更新映射

  - 首次创建一个索引的时候，可以指定类型的映射。
  - 更新映射时可以 *增加* 一个域映射，但不能 *修改* 存在的域映射。
    - 例：不能将一个存在的域从 `analyzed` 改为 `not_analyzed`

- 请求体查询(__GET__可改为__POST__)

  - 查询语句的结构

    ```Python
    # 典型结构
    {
        QUERY_NAME: {
            ARGUMENT: VALUE,
            ARGUMENT: VALUE,...
        }
    }
    
    # 针对某个字段
    {
        QUERY_NAME: {
            FIELD_NAME: {
                ARGUMENT: VALUE,
                ARGUMENT: VALUE,...
            }
        }
    }
    ```

    

  - 空查询（查询索引库全部数据）

    ```python 
    GET /_search
    {}
    
    GET /_search
    {
        "query": {
            "match_all": {}
        }
    }
    ```

  - 指定索引库类型表的空查询（查询指定索引、类型的全部数据）

    ```
    GET /index_2014*/type1,type2/_search
    {}
    ```

  - 简单条件查询

    ```python
    GET /_search
    {
        "query": YOUR_QUERY_HERE
    }
    ```

  - 针对某个字段查询示例:

    ```python
    # 查询 `tweet` 字段中包含 `elasticsearch` 的 tweet
    GET /_search
    {
        "query": {
            "match": {
                "tweet": "elasticsearch"
            }
        }
    }
    ```

  - 复合查询:

    ```python
    #   `bool` 语句 允许在你需要的时候组合其它语句
    {
        "bool": {
            "must":     { "match": { "tweet": "elastic" }},
            "must_not": { "match": { "name":  "mary" }},
            "should":   { "match": { "tweet": "full text" }},
            "filter":   { "range": { "age" : { "gt" : 30 }} }
        }
    }
    # 复合语句可以合并其他复合语句
    {
        "bool": {
            "must": { "match": { "email": "business opportunity" }},
            "should": [
                { "match":     { "starred": true }},
                { "bool": {
                    "must":    { "match": { "folder": "inbox" }},
                    "must_not":{ "match": { "spam": true }}
                					}
                }
            ],
            "minimum_should_match": 1
        }
    }
    ```

- 查询与过滤：`query`与`filter`

  - `query`
    - 含评分机制（匹配文档内容与查询内容的相关程度）scoring query
    - 查询结果不缓存
  - `filter`
    - 不含评分机制，non-scoring query
    - 查询结果会被缓存到内存中以便快速读取
    - 目标是减少那些需要通过评分查询（scoring queries）进行检查的文档。

- 重要查询

  - `match_all`

    - 匹配所有文档

    ```python
    { "match_all": {}}
    ```

  - `match`

    - 标准查询，
    - 查询字符串型字段，用正确的分析器去分析查询字符串
    - 查询精确值字段，精确匹配给定的值

  - `multi_match`

    - 多字段查询

    ```python
    {
        "multi_match": {
            "query":    "full text search",
            "fields":   [ "title", "body" ]
        }
    }
    ```

  - `range`

    - 指定区间内的数字或者时间

    ```python
    {
        "range": {
            "age": {
                "gte":  20,
                "lt":   30
            }
        }
    }
    ```

  - `term`

    - 精确值匹配(单值)。数字、时间、布尔或者那些 `not_analyzed` 的字符串

    ```python
    { "term": { "age":    26           }}
    { "term": { "date":   "2014-09-01" }}
    { "term": { "public": true         }}
    { "term": { "tag":    "full_text"  }}
    ```

  - `terms`

    - 多值精确匹配

    ```python
    { "terms": { "tag": [ "search", "full_text", "nosql" ] }}
    ```

  - `exists`、`missing`

    - 存在查询。用于某个字段有值的情况和某个字段缺值的情况

    ```python
    {
        "exists":   {
            "field":    "title"
        }
    }
    ```

- 组合多查询

  - **`must`**
    - 文档 *必须* 匹配这些条件才能被匹配。
  - **`must_not`**
    - 文档 *必须不* 匹配这些条件才能被匹配。
  - **`should`**
    - 如果满足这些语句中的任意语句将增加 `_score` ，否则无任何影响。
    - 它们主要用于修正每个文档的相关性得分。
  - **`filter`**
    - *必须* 匹配，但它以不评分、过滤模式来进行。
    - 这些语句对评分没有贡献，只是根据过滤标准来排除或包含文档。

  -  **`bool` **
    - 将每一个子查询独自地计算文档的相关性得分进行合并，并且返回一个代表整个布尔操作的得分

  ```python
  # 查找 title 字段匹配 how to make millions 并且不被标识为 spam 的文档。那些被标识为 starred 或在2014之后的文档，将比另外那些文档拥有更高的排名。如果 两者 都满足，那么它排名将更高
  {
      "bool": {
          "must":     { "match": { "title": "how to make millions" }},
          "must_not": { "match": { "tag":   "spam" }},
          "should": [
              { "match": { "tag": "starred" }},
              { "range": { "date": { "gte": "2014-01-01" }}}
          ]
      }
  }
  ```

- 含过滤器的查询

  ```python
  # 使用各种对 filter 查询有效的优化手段来提升性能
  {
      "bool": {
          "must":     { "match": { "title": "how to make millions" }},
          "must_not": { "match": { "tag":   "spam" }},
          "should": [
              { "match": { "tag": "starred" }}
          ],
          "filter": {
            "range": { "date": { "gte": "2014-01-01" }} 
          }
      }
  }
  ```

  ```python
  # 可以在过滤标准中增加布尔逻辑
  {
      "bool": {
          "must":     { "match": { "title": "how to make millions" }},
          "must_not": { "match": { "tag":   "spam" }},
          "should": [
              { "match": { "tag": "starred" }}
          ],
          "filter": {
            "bool": { 
                "must": [
                    { "range": { "date": { "gte": "2014-01-01" }}},
                    { "range": { "price": { "lte": 29.99 }}}
                ],
                "must_not": [
                    { "term": { "category": "ebooks" }}
                ]
            }
          }
      }
  }
  ```

  - `constant_score`
    - 将一个不变的常量评分应用于所有匹配的文档

    ```python
    # 文档将按照随机顺序返回，并且每个文档都会评为零分。
    GET /_search
    {
        "query" : {
            "bool" : {
                "filter" : {
                    "term" : {
                        "user_id" : 1
                    }
                }
            }
        }
    }
    # 结果同上，文档将按照随机顺序返回，并且每个文档都会评为1分。
    GET /_search
    {
        "query" : {
            "constant_score" : {
                "filter" : {
                    "term" : {
                        "user_id" : 1
                    }
                }
            }
        }
    }
    ```

- 验证查询

  -  `validate-query` 与`explain`

    ```python
    GET /gb/tweet/_validate/query?explain 
    {
       "query": {
          "tweet" : {
             "match" : "really powerful"
          }
       }
    }
    ```

    ```python
    {
      "valid" :     false,
      "_shards" :   { ... },
      "explanations" : [ {
        "index" :   "gb",
        "valid" :   false,
        "error" :   "org.elasticsearch.index.query.QueryParsingException:
                     [gb] No query registered for [tweet]"
      } ]
    }
    ```

- 排序性与相关性

  -  默认排序是以 `_score` 降序，`_score`，float类型

  - `sort`

    - 通过时间来对 tweets 进行排序是有意义的，最新的 tweets 排在最前

    ```python
    # 
    GET /_search
    {
        "query" : {
            "bool" : {
                "filter" : { "term" : { "user_id" : 1 }}
            }
        },
        "sort": { "date": { "order": "desc" }}
    }
    # 实测
    GET /test/employee/_search
      {
          "query": {
          "match_all": {}
          },
          "sort": {"age": {"order":"desc"}}
        }
    ```

  - 相关性
  
    -  *relevance* 是用来计算全文本字段的值相对于全文本检索词相似程度的算法
    -  Elasticsearch 的相似度算法被定义为检索词频率/反向文档频率， *TF/IDF*
    -  **检索词频率**
       - 检索词在该字段出现的频率？出现频率越高，相关性也越高。 字段中出现过 5 次要比只出现过 1 次的相关性高。
    -  **反向文档频率**
       - 每个检索词在索引中出现的频率越高，相关性越低。检索词出现在多数文档中会比出现在少数文档中的权重更低。
    -  **字段长度准则**
       -  字段的长度越长，相关性越低。 检索词出现在一个短的 title 要比同样的词出现在一个长的 content 字段权重更大。
    -  __增加相关性的其他方式__
       -  短语查询中检索词的距离或模糊查询里的检索词相似度。
       -   yes|no 型子句，匹配的子句越多，相关性评分越高
  
  - __理解相关性评分标准__`explain`
  
    ```python
    # explain
    GET /test/employee/_search?explain=true
    {
      "query": {
        "match": {"about":"rock climbing"}
      }
    }
    
    "_explanation" : {
              "value" : 1.4167401,
              "description" : "sum of:",
              "details" : [
                {
                  "value" : 0.4589591,
                  "description" : "weight(about:rock in 0) [PerFieldSimilarity], result of:",
                  "details" : [
                    {
                      "value" : 0.4589591,
                      "description" : "score(freq=1.0), computed as boost * idf * tf from:",
                      "details" : [
                        {
                          "value" : 2.2,
                          "description" : "boost",
                          "details" : [ ]
                        },
                        {
                          "value" : 0.47000363,
                          "description" : "idf, computed as log(1 + (N - n + 0.5) / (n + 0.5)) from:",
                          "details" : [
                            {
                              "value" : 2,
                              "description" : "n, number of documents containing term",
                              "details" : [ ]
                            },
                            {
                              "value" : 3,
                              "description" : "N, total number of documents with field",
                              "details" : [ ]
                            }
                          ]
                        },
                        {
                          "value" : 0.44386417,
                          "description" : "tf, computed as freq / (freq + k1 * (1 - b + b * dl / avgdl)) from:",
                          "details" : [
                            {
                              "value" : 1.0,
                              "description" : "freq, occurrences of term within document",
                              "details" : [ ]
                            },
                            {
                              "value" : 1.2,
                              "description" : "k1, term saturation parameter",
                              "details" : [ ]
                            },
                            {
                              "value" : 0.75,
                              "description" : "b, length normalization parameter",
                              "details" : [ ]
                            },
                            {
                              "value" : 6.0,
                              "description" : "dl, length of field",
                              "details" : [ ]
                            },
                            {
                              "value" : 5.6666665,
                              "description" : "avgdl, average length of field",
                              "details" : [ ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  "value" : 0.95778096,
                  "description" : "weight(about:climbing in 0) [PerFieldSimilarity], result of:",
                  "details" : [
                    {
                      "value" : 0.95778096,
                      "description" : "score(freq=1.0), computed as boost * idf * tf from:",
                      "details" : [
                        {
                          "value" : 2.2,
                          "description" : "boost",
                          "details" : [ ]
                        },
                        {
                          "value" : 0.98082924,
                          "description" : "idf, computed as log(1 + (N - n + 0.5) / (n + 0.5)) from:",
                          "details" : [
                            {
                              "value" : 1,
                              "description" : "n, number of documents containing term",
                              "details" : [ ]
                            },
                            {
                              "value" : 3,
                              "description" : "N, total number of documents with field",
                              "details" : [ ]
                            }
                          ]
                        },
                        {
                          "value" : 0.44386417,
                          "description" : "tf, computed as freq / (freq + k1 * (1 - b + b * dl / avgdl)) from:",
                          "details" : [
                            {
                              "value" : 1.0,
                              "description" : "freq, occurrences of term within document",
                              "details" : [ ]
                            },
                            {
                              "value" : 1.2,
                              "description" : "k1, term saturation parameter",
                              "details" : [ ]
                            },
                            {
                              "value" : 0.75,
                              "description" : "b, length normalization parameter",
                              "details" : [ ]
                            },
                            {
                              "value" : 6.0,
                              "description" : "dl, length of field",
                              "details" : [ ]
                            },
                            {
                              "value" : 5.6666665,
                              "description" : "avgdl, average length of field",
                              "details" : [ ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            }
    
    # 返回结果含_explanation 。每个入口都包含一个 description 、 value 、 details 字段，它分别是计算的类型、计算结果和任何我们需要的计算细节
    # detail的四个desc :	
    # rock climbing 相关性评分计算的总结，检索词频率/反向文档频率或TF/IDF
    # 检索词频率，检索词 `rock climb` 在这个文档的 `about` 字段中的出现次数。
    # 反向文档频率，检索词 `rock climb` 在索引上所有文档的 `about` 字段中出现的次数。
    # 字段长度准则，在这个文档中， `about` 字段内容的长度 -- 内容越长，值越小。
    ```
  
    -  返回结果含_explanation 。每个入口都包含一个 description 、 value 、 details 字段，它分别是计算的类型、计算结果和任何我们需要的计算细节
     detail的四个desc :	
       - rock climbing 相关性评分计算的总结，检索词频率/反向文档频率或TF/IDF
       - 检索词频率，检索词 `rock climb` 在这个文档的 `about` 字段中的出现次数。
       - 反向文档频率，检索词 `rock climb` 在索引上所有文档的 `about` 字段中出现的次数。
       - 字段长度准则，在这个文档中， `about` 字段内容的长度 -- 内容越长，值越小。

- 自定义分析器

  - 一个 *分析器* 就是一个包装器，在一个包里面组合了三种函数

    - **字符过滤器 **    char_filter
      - 字符过滤器 用来 `整理` 一个尚未被分词的字符串。
      - 如：[`html清除` 字符过滤器](https://www.elastic.co/guide/en/elasticsearch/reference/5.6/analysis-htmlstrip-charfilter.html) 来移除掉所有的HTML标签
      - 一个分析器可能有0个或者多个字符过滤器。
    - **分词器 **   tokenizer
      - 一个分析器 *必须* 有一个唯一的分词器。 分词器把字符串分解成单个词条或者词汇单元。
      - 如：[`关键词` 分词器](https://www.elastic.co/guide/en/elasticsearch/reference/5.6/analysis-keyword-tokenizer.html) 完整地输出 接收到的同样的字符串，并不做任何分词。 [`空格` 分词器](https://www.elastic.co/guide/en/elasticsearch/reference/5.6/analysis-whitespace-tokenizer.html) 只根据空格分割文本 。 [`正则` 分词器](https://www.elastic.co/guide/en/elasticsearch/reference/5.6/analysis-pattern-tokenizer.html) 根据匹配正则表达式来分割文本 。
    - **词单元过滤器**   filter
      - 经过分词的 *词单元流* 会按照指定的顺序通过指定的词单元过滤器 
      - 词单元过滤器可以修改、添加或者移除词单元
      - 如： [`lowercase` 小写词过滤器和 [`stop` 词过滤器](https://www.elastic.co/guide/en/elasticsearch/reference/5.6/analysis-stop-tokenfilter.html) 

  - 自定义分析器示例

    ```python
    PUT /my_index
    {
        "settings": {
            "analysis": {
                "char_filter": {
                    "&_to_and": {
                        "type":       "mapping",
                        "mappings": [ "&=> and "]
                }},
                "filter": {
                    "my_stopwords": {
                        "type":       "stop",
                        "stopwords": [ "the", "a" ]
                }},
                "analyzer": {
                    "my_analyzer": {
                        "type":         "custom",
                        "char_filter":  [ "html_strip", "&_to_and" ],
                        "tokenizer":    "standard",
                        "filter":       [ "lowercase", "my_stopwords" ]
                }}
    }}}
    ```

  - 自定义分词器使用

    ```python
    PUT /my_index/_mapping/my_type
    {
        "properties": {
            "title": {
                "type":      "string",
                "analyzer":  "my_analyzer"
            }
        }
    }
    ```

- ####类型和映射

  - *类型* 在 Elasticsearch 中表示一类相似的文档。 类型由 *名称* —比如 `user` 或 `blogpost` —和 *映射* 组成。
  
- *映射*, 就像数据库中的 schema ，描述了文档可能具有的字段或 *属性* 、每个字段的数据类型—比如 `string`, `integer` 或 `date` ，以及Lucene是如何索引和存储这些字段的
  
    - 根对象：映射的最高一层被称为 *根对象* 
      - 一个 *properties* 节点，列出了文档中可能包含的每个字段的映射
      - 各种`元数据字段`，它们都`以一个下划线开头`，例如 `_type` 、 `_id` 和 `_source`
      - 设置项，控制如何动态处理新的字段，例如 `analyzer` 、 `dynamic_date_formats` 和 `dynamic_templates`
      - 其他设置，可以同时应用在根对象和其他 `object` 类型的字段上，例如 `enabled` 、 `dynamic` 和 `include_in_all`
    
  - 属性
  
    - **`type`** ：字段的数据类型，例如 `string` 或 `date`
    - **`index`** : 字段是否应当被当成全文来搜索（ `analyzed` ），或被当成一个准确的值（ `not_analyzed` ），还是完全不可被搜索（ `no` ）
    - **`analyzer`** ：确定在索引和搜索时全文字段使用的 `analyzer`
  
  - 元数据 `_source`字段
  
    -  `_source` 字段存储代表文档体的JSON字符串
  
    - 在请求体中指定 `_source` 参数，可以只获取特定的字段
  
      ```python
      GET /_search
      {
          "query":   { "match_all": {}},
          "_source": [ "title", "created" ]
      }
      ```
  
  - 元数据 `_all`字段
  
    - 一个把其它字段值当作一个大字符串来索引的特殊字段
  
    - 在没有指定字段时默认使用 `_all` 字段
  
    - 禁用`_all`字段
  
      ```python
      PUT /my_index/_mapping/my_type
      {
          "my_type": {
              "_all": { "enabled": false }
          }
      }
      ```
  
    - 通过 `include_in_all` 设置来逐个控制字段是否要包含在 `_all` 字段中，默认值是 `true`
  
    - 想要保留 `_all` 字段作为一个只包含某些特定字段的全文字段，例如只包含 `title`，`overview`，`summary` 和 `tags`。可以为所有字段默认禁用 `include_in_all` 选项，仅在选择的字段上启用
  
    - `_all` 字段是经过分词的 `string` 字段，仅使用`_all`字段独自的分词器 经过分词的 `string` 字段。它使用默认分词器来分析它的值，不管这个值原本所在字段指定的分词器。
  
      ```python
      PUT /my_index/my_type/_mapping
      {
          "my_type": {
              "include_in_all": false,
            	"_all": {"analyzer": "whitespace"}
              "properties": {
                  "title": {
                      "type":           "string",
                      "include_in_all": true
                  },
                  ...
              }
          }
      }
      ```
  
  - **__动态映射__**
  
    - 映射新字段可以用 `dynamic` 配置
  
      - **`true`** ：动态添加新的字段—缺省
  
      - **`false`**   : 忽略新的字段
  
      - **`strict`** ：如果遇到新字段抛出异常
  
        - 配置参数 `dynamic` 可以用在根 `object` 或任何 `object` 类型的字段上。你可以将 `dynamic` 的默认值设置为 `strict` , 而只在指定的内部对象中开启它。如下示例：
  
          - 如果遇到新字段，对象 `my_type` 就会抛出异常。
          - 内部对象 `stash` 遇到新字段就会动态创建新字段。
  
          ```Python
          PUT /my_index
          {
              "mappings": {
                  "my_type": {
                      "dynamic":      "strict", 
                      "properties": {
                          "title":  { "type": "string"},
                          "stash":  {
                              "type":     "object",
                              "dynamic":  true 
                          }
                      }
                  }
              }
          }
          ```
  
  - __自定义动态映射__       之动态模板`dynamic_templates`
  
    -  `mapping` 来指定映射规则，至少一个参数
  
    - 模板按照顺序来检测，如下示例：
  
      - `es` ：以 `_es` 结尾的字段名需要使用 `spanish` 分词器。
  
      - `en` ：所有其他字段使用 `english` 分词器。
  
        ```python
        PUT /my_index
        {
            "mappings": {
                "my_type": {
                    "dynamic_templates": [
                        { "es": {
                              "match":              "*_es", 
                              "match_mapping_type": "string",
                              "mapping": {
                                  "type":           "string",
                                  "analyzer":       "spanish"
                              }
                        }},
                        { "en": {
                              "match":              "*", 
                              "match_mapping_type": "string",
                              "mapping": {
                                  "type":           "string",
                                  "analyzer":       "english"
                              }
                        }}
                    ]
        }}}
        ```
  
    - `match` 参数只匹配字段名称， `path_match` 参数匹配字段在对象上的完整路径，所以 `address.*.name` 将匹配这样的字段：
  
      ```python
      {
          "address": {
              "city": {
                  "name": "New York"
              }
          }
      }
      ```
  
  - __缺省映射 __  `_default_`
  
    - `_default_` 映射可以方便地指定通用设置
  
    - 通常，一个索引中的所有类型共享相同的字段和设置，除非类型在自己的映射中明确覆盖这些设置，如下：
  
      ```python
      # 用 _default_ 映射为所有的类型禁用 _all 字段， 只在 blog 类型启用
      PUT /my_index
      {
          "mappings": {
              "_default_": {
                  "_all": { "enabled":  false }
              },
              "blog": {
                  "_all": { "enabled":  true  }
              }
          }
      }
      ```
  
- __重新索引__，__之零停机的情况下从旧索引迁移到新索引__

  - 重新索引情况：虽然可以增加新的类型到索引中，或者增加新的字段到类型中，但是不能添加新的分析器或者对现有的字段做改动
    - 如果你那么做的话，结果就是那些已经被索引的数据就不正确， 搜索也不能正常工作
  - 现有数据的这类改变最简单的办法就是重新索引：用新的设置创建新的索引并把文档从旧的索引复制到新的索引，
    - 重建索引方法
      - 用 [*scroll*](https://www.elastic.co/guide/cn/elasticsearch/guide/current/scroll.html) 从旧的索引检索批量文档 ，
      -  然后用 [`bulk` API](https://www.elastic.co/guide/cn/elasticsearch/guide/current/bulk.html) 把文档推送到新的索引中。

- __索引别名__

  - 索引 *别名* 就像一个快捷方式或软连接，可以指向一个或多个索引，也可以给任何一个需要索引名的API来使用。
    - 索引别名作用
      - 在运行的集群中可以无缝的从一个索引切换到另一个索引
      - 给多个索引分组 (例如， `last_three_months`)
      - 给索引的一个子集创建 `视图`
  - 两种方式管理别名：
    -  `_alias` 用于单个操作，
    -  `_aliases` 用于执行多个原子级操作

  __创建索引别名__：

  - 创建索引 my_index_v1 ，然后将别名 my_index 指向它

    ```
    PUT /my_index_v1 
    PUT /my_index_v1/_alias/my_index 
    ```

  - 检测这个别名指向哪一个索引

    ```
    GET /*/_alias/my_index
    ```

  - 检测哪些别名指向这个索引

    ```
    GET /my_index_v1/_alias/*
    ```

  - 两个检测结果应一致

    ```python
    {
        "my_index_v1" : {
            "aliases" : {
                "my_index" : { }
            }
        }
    }
    ```

  __重建索引操作__

  - 用新映射创建索引 `my_index_v2` 

    ```python
    PUT /my_index_v2
    {
        "mappings": {
            "my_type": {
                "properties": {
                    "tags": {
                        "type":   "string",
                        "index":  "not_analyzed"
                    }
                }
            }
        }
    }
    ```

  - 将数据从 `my_index_v1` 索引到 `my_index_v2`

    - 一个别名可以指向多个索引，所以我们在添加别名到新索引的同时必须从旧的索引中删除它。这个操作需要原子化，这意味着我们需要使用 `_aliases` 操作

    ```python
    POST /_aliases
    {
        "actions": [
            { "remove": { "index": "my_index_v1", "alias": "my_index" }},
            { "add":    { "index": "my_index_v2", "alias": "my_index" }}
        ]
    }
    ```

- 深入搜索

  - 相似度（word proximity）、部分匹配（partial matching）、模糊匹配（fuzzy matching）以及语言感知（language awareness）

  - 结构化搜索

    - 指有关探询那些具有内在结构数据的过程
      - 比如日期、时间和数字都是结构化的：它们有精确的格式，可以对这些格式进行逻辑操作。比较常见的操作包括比较数字或时间的范围，或判定两个值的大小。
    - 结构化查询不关心文件的相关度或评分；它简单的对文档包括或排除处理

  - 精确值查询

    - `term`

      - 处理数字（numbers）、布尔值（Booleans）、日期（dates）以及文本（text、keyword）

      - 接受一个字段名以及我们希望查找的数值，结合 `constant_score` 查询以非评分模式来执行 `term` 查询并以`1`作为统一评分

        ```python
        {
          "query": {
            "constant_score": {
              "filter": { # 过滤器查询
                	"term": {
            				"price" : 30,
          			}
              }
            }
          }
        }
        ```

      - 若用term查询字符串类型，字段类型应设为keyword

        [ES数据类型](https://blog.csdn.net/hello_world123456789/article/details/95341515)

  - 组合过滤器

    - bool过滤器

      - 为复合过滤器，可以接受多个其他过滤器作为参数，并将这些过滤器结合成各式各样的布尔（逻辑）组合

      - 三部分组成，三个可以组合使用或单独使用

        ```python
        {
           "bool" : {
              "must" :     [],
              "should" :   [],
              "must_not" : [],
           }
        }
        ```

      - **`must`**

        - 所有的语句都 *必须（must）* 匹配，与 `AND` 等价。

      - **`must_not`**

        - 所有的语句都 *不能（must not）* 匹配，与 `NOT` 等价。

      - **`should`**

        - 至少有一个语句要匹配，与 `OR` 等价。

      ```python
      # 价格为20或productID为XHDK-A-1293-#fJ3，价格不能为30
      # 需要一个 filtered 查询将所有的东西包起来
      GET /my_store/products/_search
      {
         "query" : {
            "filtered" : { 
               "filter" : {
                  "bool" : {
                    "should" : [
                       { "term" : {"price" : 20}}, 
                       { "term" : {"productID" : "XHDK-A-1293-#fJ3"}} 
                    ],
                    "must_not" : {
                       "term" : {"price" : 30} 
                    }
                 }
               }
            }
         }
      }
      ```

    - 嵌套bool过滤器

      ```python
      # productID为KDKE-B-9947-#kL5或productID为JODL-X-1937-#pV7且price为30
      GET /my_store/products/_search
      {
         "query" : {
            "filtered" : {
               "filter" : {
                  "bool" : {
                    "should" : [
                      { "term" : {"productID" : "KDKE-B-9947-#kL5"}}, 
                      { "bool" : { 
                        "must" : [
                          { "term" : {"productID" : "JODL-X-1937-#pV7"}}, 
                          { "term" : {"price" : 30}} 
                        ]
                      }}
                    ]
                 }
               }
            }
         }
      }
      ```

  - `terms`多个精确值查询

    ```python
    # price必须为20或30
    GET /my_store/products/_search
    {
        "query" : {
            "constant_score" : {
                "filter" : {
                    "terms" : { 
                        "price" : [20, 30]
                    }
                }
            }
        }
    }
    ```

    - `term`、`terms`指包含操作，而不是等值判定
      - 若待查询字段为列表类型，其中一个元素满足`term`查询条件即可

  - `range`范围查询

    - `gt`: `>` 大于（greater than）

    - `lt`: `<` 小于（less than）

    - `gte`: `>=` 大于或等于（greater than or equal to）

    - `lte`: `<=` 小于或等于（less than or equal to

      ```python
      # price大于等于20小于40
      GET /my_store/products/_search
      {
          "query" : {
              "constant_score" : {
                  "filter" : {
                      "range" : {
                          "price" : {
                              "gte" : 20,
                              "lt"  : 40
                          }
                      }
                  }
              }
          }
      }
      ```

      ```python
      # 大于当前时间减1小时
      # 大于2020年6月1号 + 1月
      # 日期计算是 日历相关（calendar aware） 的，所以它不仅知道每月的具体天数，还知道某年的总天数（闰年）等信息
      GET /my_store/products/_search
      {
      	"query": {
          "constant_score": {
            "filter": {
              "range": {
                "timestamp": {
                  "gt": "now-1h"
                  #"gt" : "2020-06-01 00:00:00||+1M"
                }
              }
            }
          }
        }
      }
      ```

  - `exists`存在查询

    ```python
    # 字段tags存在
    GET /my_index/posts/_search
    {
        "query" : {
            "constant_score" : {
                "filter" : {
                    "exists" : { "field" : "tags" }
                }
            }
        }
    }
    ```

  - `missing`缺失查询

    ```Python
    # 不存在字段tags
    GET /my_index/posts/_search
    {
        "query" : {
            "constant_score" : {
                "filter": {
                    "missing" : { "field" : "tags" }
                }
            }
        }
    }
    ```

- 缓存

    - filter会产生缓存
        - 基于使用频次自动缓存查询
        - 文档数量超过 10,000 ，
        - 或超过总文档数量的 3%

- 全文搜索(full-text search)

    - 相关性（Relevance）
      - 评价查询与其结果间的相关程度
      - 根据这种相关程度对结果排名的一种能力
        - TF/IDF 方法
        - 地理位置邻近
        - 模糊相似
        - 其他算法
    - 分析（analysis）
      - 将文本块转换为有区别的、规范化的 token 的一个过程
        - 目的：
          - （a）创建倒排索引
          - （b）查询倒排索引

- 文本查询分类

    - 所有查询会或多或少的执行相关度计算，但不是所有查询都有分析阶段。和一些特殊的完全不会对文本进行操作的查询（如 `bool` 或 `function_score` ）不同，文本查询可以划分成两大家族
    - 
    - 基于词项的查询
        - 如`term`、 `fuzzy`
            - 为底层查询，不需要分析阶段，
            - 查询只对倒排索引的词项精确匹配，但会用 TF/IDF 算法为查询结果文档相关度评分
    - 基于全文的查询
        - 如`match`、`query_string`
            - 为高层查询，它们了解字段映射的信息
                - 如果查询 `日期（date）` 或 `整数（integer）` 字段，它们会将查询字符串分别作为日期或整数对待。
                - 如果查询一个（ `not_analyzed` ）未分析的精确值字符串字段，它们会将整个查询字符串作为单个词项对待
                - 如果要查询一个（ `analyzed` ）已分析的全文字段，它们会先将查询字符串传递到一个合适的分析器，然后生成一个供查询的词项列表
                    - 一旦组成了词项列表，这个查询会对每个词项逐一执行底层的查询，再将结果合并，然后为每个文档生成一个最终的相关度评分

- 全文搜索之 `match`

    - 数据

        ```python
        POST /my_index/my_type/_bulk
        { "index": { "_id": 1 }}
        { "title": "The quick brown fox" }
        { "index": { "_id": 2 }}
        { "title": "The quick brown fox jumps over the lazy dog" }
        { "index": { "_id": 3 }}
        { "title": "The quick brown fox jumps over the quick dog" }
        { "index": { "_id": 4 }}
        { "title": "Brown fox brown dog" }
        ```

    - `match`查询

        ```python
        GET /my_index/my_type/_search
        {
            "query": {
                "match": {
                    "title": "QUICK!"
                }
            }
        }
        ```

    - `match`查询步骤

        - *检查字段类型* 。

            标题 `title` 字段是一个 `string` 类型（ `analyzed` ）已分析的全文字段，这意味着查询字符串本身也应该被分析

        - *分析查询字符串* 。

            将查询的字符串 `QUICK!` 传入标准分析器中，输出的结果是单个项 `quick` 。因为只有一个单词项，所以 `match` 查询执行的是单个底层 `term` 查询。

        - *查找匹配文档* 。

            用 `term` 查询在倒排索引中查找 `quick` 然后获取一组包含该项的文档，本例的结果是文档：1、2 和 3 。

        - *为每个文档评分* 。

            用 `term` 查询计算每个文档相关度评分 `_score` ，这是种将词频（term frequency，即词 `quick` 在相关文档的 `title` 字段中出现的频率）和反向文档频率（inverse document frequency，即词 `quick` 在所有文档的 `title` 字段中出现的频率），以及字段的长度（即字段越短相关度越高）相结合的计算方式

    - 查询结果为(不完整数据)

        ```python
        "hits": [
         {
            "_id":      "1",
            "_score":   0.5, 
            "_source": {
               "title": "The quick brown fox"
            }
         },
         {
            "_id":      "3",
            "_score":   0.44194174, 
            "_source": {
               "title": "The quick brown fox jumps over the quick dog"
            }
         },
         {
            "_id":      "2",
            "_score":   0.3125, 
            "_source": {
               "title": "The quick brown fox jumps over the lazy dog"
            }
         }
        ]
        ```

        - 文档 1 最相关，因为它的 `title` 字段更短，即 `quick` 占据内容的一大部分。
        - 文档 3 比 文档 2 更具相关性，因为在文档 3 中 `quick` 出现了两次。

    - 多词查询(https://www.elastic.co/guide/cn/elasticsearch/guide/current/match-multi-word.html)

    - 正则查询

        ```python
        GET /my_index/my_type/_search
        {
          "query": {
            "regexp": {
              "title": "[a-z]he"
            }
          }
        }
        ```

    - 查询结果

        ```python
        "hits" : [
              {
                "_index" : "my_index",
                "_type" : "my_type",
                "_id" : "1",
                "_score" : 1.0,
                "_source" : {
                  "title" : "The quick brown fox"
                }
              },
              {
                "_index" : "my_index",
                "_type" : "my_type",
                "_id" : "2",
                "_score" : 1.0,
                "_source" : {
                  "title" : "The quick brown fox jumps over the lazy dog"
                }
              },
              {
                "_index" : "my_index",
                "_type" : "my_type",
                "_id" : "3",
                "_score" : 1.0,
                "_source" : {
                  "title" : "The quick brown fox jumps over the quick dog"
                }
              }
            ]
        ```

        - query请求体不需要区分大小写

- 区分权重

    - shoulder: []
    - boost : integer

- 分析器使用优先规则

    - 查询自己定义的 `analyzer` ，否则
    - 字段映射里定义的 `search_analyzer` ，否则
    - 字段映射里定义的 `analyzer` ，否则
    - 索引设置中名为 `default_search` 的分析器，默认为
    - 索引设置中名为 `default` 的分析器，默认为
    - `standard` 标准分析器
    
- ```
    # 查看索引
    _cat/indices
    # 查看分片
    _cat/shards
    # 查看
    ```

- 



