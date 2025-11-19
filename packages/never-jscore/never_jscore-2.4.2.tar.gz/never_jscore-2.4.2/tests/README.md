# never-jscore 测试套件

本目录包含 never-jscore v2.4.2 的完整测试用例，展示所有核心功能的使用方法。

## 运行所有测试

```bash
python tests/run_all_tests.py
```

## 测试文件列表

### 1. `test_browser_protection.py` - 浏览器环境防检测 ⭐⭐⭐
**测试内容：**
- Deno 对象隐藏
- 浏览器全局对象（window, document, navigator, location）
- 函数显示为 `[native code]`
- Chrome 浏览器特征（chrome 对象）
- 综合环境检测绕过

**关键功能：** 隐藏 Deno 运行时特征，模拟真实浏览器环境

---

### 2. `test_proxy_logging.py` - Proxy 日志系统 ⭐⭐⭐
**测试内容：**
- `$proxy()` 创建代理对象
- `$getProxyLogs()` 获取访问日志
- `$proxyGlobal()` 代理全局对象
- 函数调用监控
- 逆向工程实战场景

**关键功能：** 监控对象属性访问，分析加密库调用链

---

### 3. `test_random_seed.py` - 确定性随机数 ⭐⭐⭐
**测试内容：**
- `Math.random()` 种子控制
- `crypto.randomUUID()` 种子控制
- 可重现加密调试
- 动态签名生成

**关键功能：** 使用固定种子让随机数可重现，调试包含随机 nonce 的加密算法

---

### 4. `test_hook_interception.py` - Hook 拦截系统 ⭐⭐⭐
**测试内容：**
- `$return()` 提前返回
- Hook 加密函数
- Hook XMLHttpRequest
- 提取中间值
- Token 密钥提取

**关键功能：** 在任意位置拦截 JS 执行，提取加密参数和密钥

---

### 5. `test_async_promise.py` - Promise 和异步
**测试内容：**
- Promise 链式调用
- async/await
- setTimeout/setInterval + Promise
- 嵌套异步
- 微任务与宏任务

**关键功能：** 完整支持 Promise/async/await，自动等待异步操作

---

### 6. `test_web_apis.py` - Web API
**测试内容：**
- 加密 API（md5, sha256, crypto）
- localStorage/sessionStorage
- URL 处理
- Buffer、Blob
- Performance API

**关键功能：** 内置 800+ 行 Web API polyfill，零配置使用浏览器 API

---

### 7. `test_context_management.py` - Context 管理 ⭐⭐
**测试内容：**
- with 语句正确用法
- 循环中的 Context 使用
- Context 复用 vs 重新创建
- 性能对比
- 常见陷阱

**关键功能：** 避免 HandleScope 错误，掌握正确的 Context 管理模式

**关键示例：**
```python
# ✅ 正确：复用 Context
ctx = never_jscore.Context()
for i in range(1000):
    ctx.call("func", [i])
del ctx

# ❌ 错误：循环中直接用 with
for i in range(100):  # 会崩溃！
    with never_jscore.Context() as ctx:
        ctx.evaluate(...)
```

---

### 8. `test_multithreading.py` - 多线程使用 ⭐⭐
**测试内容：**
- ThreadPoolExecutor 使用
- ThreadLocal + Context 复用
- 性能对比（单线程 vs 多线程）
- 线程隔离性
- 错误处理

**关键功能：** 在多线程环境中安全使用 never-jscore

**最佳实践：**
```python
import threading
from concurrent.futures import ThreadPoolExecutor

thread_local = threading.local()

def get_context():
    if not hasattr(thread_local, 'ctx'):
        thread_local.ctx = never_jscore.Context()
        thread_local.ctx.compile(js_code)
    return thread_local.ctx

def worker(data):
    ctx = get_context()  # 每个线程复用自己的 Context
    return ctx.call("process", [data])

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(worker, data_list))
```

---

### 9. `test_xmlhttprequest.py` - XMLHttpRequest ⭐
**测试内容：**
- xhr.open() / xhr.send()
- 请求头设置
- 响应处理
- POST JSON 数据
- Hook 拦截请求

**关键功能：** 完整的 XMLHttpRequest API，可发送真实 HTTP 请求

**示例：**
```python
result = ctx.evaluate("""
    (async () => {
        return new Promise((resolve) => {
            const xhr = new XMLHttpRequest();
            xhr.onload = () => resolve(JSON.parse(xhr.responseText));
            xhr.open('GET', 'https://api.example.com/data');
            xhr.send();
        });
    })()
""")
```

---

### 10. `test_memory_and_performance.py` - 内存监控和性能调优 ⭐⭐
**测试内容：**
- 内存泄漏检测
- **V8 堆统计信息 (get_heap_statistics)** ⭐
- **V8 堆快照导出 (take_heap_snapshot)** ⭐
- 批量处理 + GC
- 性能分析
- Context 创建开销
- 调试技巧

**关键功能：** 优化内存使用，提升性能，调试问题

**V8 堆监控：**
```python
# 获取 V8 堆统计信息
heap_stats = ctx.get_heap_statistics()
print(f"总堆大小: {heap_stats['total_heap_size'] / 1024 / 1024:.2f} MB")
print(f"已使用堆: {heap_stats['used_heap_size'] / 1024 / 1024:.2f} MB")
print(f"堆大小限制: {heap_stats['heap_size_limit'] / 1024 / 1024:.2f} MB")
print(f"使用率: {heap_stats['used_heap_size'] / heap_stats['total_heap_size'] * 100:.1f}%")

# 导出 Chrome DevTools 堆快照
ctx.take_heap_snapshot("heap_snapshot.heapsnapshot")
# 然后在 Chrome DevTools -> Memory -> Load 加载快照分析
```

**优化技巧：**
```python
# 1. 定期触发 GC
ctx = never_jscore.Context()
for i in range(1000):
    ctx.call("process", [i])
    if i % 100 == 0:
        ctx.gc()  # 每 100 次清理一次

# 2. 获取统计信息
stats = ctx.get_stats()
print(f"call: {stats['call_count']} 次")

# 3. 启用日志调试
ctx = never_jscore.Context(enable_logging=True)
```

---

## 快速开始

### 运行单个测试
```bash
python tests/test_browser_protection.py
python tests/test_hook_interception.py
```

### 运行所有测试
```bash
python tests/run_all_tests.py
```

预期输出：
```
============================================================
测试结果总结
============================================================
[通过] 浏览器环境防检测
[通过] Proxy 日志系统
[通过] 确定性随机数
[通过] Hook 拦截系统
[通过] Promise 和异步功能
[通过] Web API 和浏览器环境
[通过] Context 上下文管理
[通过] 多线程使用
[通过] XMLHttpRequest
[通过] 内存监控和性能调优

总计: 10/10 测试通过
```

---

## 常见用法速查

### 1. 调试动态加密
```python
# 使用固定种子让加密结果可重现
ctx = never_jscore.Context(random_seed=12345)
result1 = ctx.call("encrypt", ["data"])
result2 = ctx.call("encrypt", ["data"])
assert result1 == result2  # 完全相同！
```

### 2. 拦截加密参数
```python
result = ctx.evaluate("""
    const originalEncrypt = CryptoLib.encrypt;
    CryptoLib.encrypt = function(plaintext, key) {
        $return({ plaintext, key });  # 提取密钥！
    };
    login('admin', 'password');
""")
print(f"密钥: {result['key']}")
```

### 3. 监控属性访问
```python
ctx.evaluate("""
    $proxyGlobal('navigator', { name: 'Nav' });
    checkBrowser();  // 执行检测脚本
    const logs = $getProxyLogs({ target: 'Nav' });
    console.log('访问:', logs);
""")
```

### 4. 多线程并行
```python
def process(data):
    ctx = never_jscore.Context()
    result = ctx.call("encrypt", [data])
    del ctx
    return result

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process, data_list))
```

---

## 测试覆盖的核心功能

### 浏览器环境模拟
- ✅ Deno 特征隐藏
- ✅ 浏览器全局对象完整
- ✅ 函数显示为 [native code]
- ✅ Chrome 浏览器特征

### 逆向工程工具
- ✅ Proxy 日志监控
- ✅ Hook 拦截系统
- ✅ 确定性随机数

### 现代 JavaScript
- ✅ Promise/async/await
- ✅ setTimeout/setInterval
- ✅ fetch/XMLHttpRequest
- ✅ 完整的事件循环

### 性能和稳定性
- ✅ Context 管理最佳实践
- ✅ 多线程支持
- ✅ 内存优化
- ✅ 性能调优

---

## 贡献测试

欢迎贡献更多测试用例！

### 添加新测试：
1. 在 `tests/` 创建 `test_*.py`
2. 遵循现有测试风格
3. 在 `run_all_tests.py` 中添加
4. 确保可以独立运行
5. 提交 PR

---

## 许可证

MIT License - 详见项目根目录的 LICENSE 文件
