###book入库

```python
# book使用入库脚本时数据需解析为以下结构：
{
  'period' : str，
  'subject': str,
  'press_version': str,
  'grade': str,
  'chapters': [
    {
      'name': str,
      'chapters': [
        {
          'name': str,
          # 若为最内层节点，chapters改为knowledges
          'chapters': [
            {
              'name': str
            }
          ]
        }
      ]
    }
  ]
}
```

