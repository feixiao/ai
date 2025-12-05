# 以下代码示例演示如何使用 InMemoryStore 来实现记忆的存储、获取和搜索操作。

from langgraph.store.memory import InMemoryStore

# 实际嵌入函数的占位符
def embed(texts: list[str]) -> list[list[float]]:
   # 在实际应用中，使用适当的嵌入模型
   return [[1.0, 2.0] for _ in texts]

# 初始化内存存储。对于生产环境，请使用基于数据库的存储方式。
store = InMemoryStore(index={"embed": embed, "dims": 2})

# 为特定用户和应用上下文定义命名空间
user_id = "my-user"
application_context = "chitchat"
namespace = (user_id, application_context)

# 1. 将记忆放入存储
store.put(
   namespace,
   "a-memory",  # 此记忆的键
   {
       "rules": [
           "User likes short, direct language",
           "User only speaks English & python",
       ],
       "my-key": "my-value",
   },
)

# 2. 通过其命名空间和键获取记忆
item = store.get(namespace, "a-memory")
print("Retrieved Item:", item)

# 3. 在命名空间内搜索记忆，按内容过滤并按与查询的向量相似性排序。
items = store.search(
   namespace,
   filter={"my-key": "my-value"},
   query="language preferences"
)
print("Search Results:", items)