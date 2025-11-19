"""
测试 Hook 拦截系统 ($return, $exit)

展示如何在关键点拦截 JS 执行并提取中间结果，用于逆向工程
"""

import never_jscore


def test_basic_return():
    """测试基本的 $return 功能"""
    ctx = never_jscore.Context()

    # 使用 $return 提前返回
    result = ctx.evaluate("""
        function longCalculation() {
            const step1 = 10 + 20;
            const step2 = step1 * 2;

            // 提前返回中间结果
            $return({ step1, step2 });

            // 下面的代码不会执行
            const step3 = step2 * 100;
            return step3;
        }

        longCalculation()
    """)

    assert result['step1'] == 30, "应该返回 step1"
    assert result['step2'] == 60, "应该返回 step2"
    assert 'step3' not in result, "step3 不应该存在（已提前返回）"

    print(f"✓ 提前返回: step1={result['step1']}, step2={result['step2']}")


def test_return_alias():
    """测试 $exit 别名"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        function test() {
            $exit('early exit');
            return 'should not reach here';
        }
        test()
    """)

    assert result == 'early exit', "$exit 应该提前返回"
    print(f"✓ $exit 别名工作正常: {result}")


def test_hook_encryption_function():
    """Hook 加密函数，拦截加密参数"""
    ctx = never_jscore.Context()

    # 模拟目标网站的加密库
    ctx.compile("""
        function encryptData(plaintext, key) {
            // 复杂的加密逻辑...
            const encrypted = btoa(plaintext + ':' + key);
            return encrypted;
        }

        function sendRequest(data) {
            const encrypted = encryptData(data.username + ':' + data.password, 'SECRET_KEY');
            // 发送加密数据...
            return { encrypted };
        }
    """)

    # Hook encryptData 函数，拦截加密前的参数
    result = ctx.evaluate("""
        // 保存原始函数
        const originalEncrypt = encryptData;

        // Hook 函数
        encryptData = function(plaintext, key) {
            // 拦截参数，提前返回
            $return({
                hooked: true,
                plaintext: plaintext,
                key: key,
                timestamp: Date.now()
            });
        };

        // 执行目标函数（会触发 Hook）
        sendRequest({ username: 'admin', password: '123456' })
    """)

    assert result['hooked'] == True, "应该触发 Hook"
    assert 'admin:123456' in result['plaintext'], "应该拦截到明文参数"
    assert result['key'] == 'SECRET_KEY', "应该拦截到密钥"

    print(f"\n=== Hook 加密函数 ===")
    print(f"✓ 拦截到明文: {result['plaintext']}")
    print(f"✓ 拦截到密钥: {result['key']}")
    print(f"✓ 时间戳: {result['timestamp']}")


def test_hook_xhr_send():
    """Hook XMLHttpRequest.send，拦截请求数据"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        // Hook XMLHttpRequest.send
        const originalSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function(body) {
            // 拦截请求体
            $return({
                hooked: 'XMLHttpRequest.send',
                method: this._method,
                url: this._url,
                headers: this._headers,
                body: body
            });
        };

        // 模拟发送请求
        const xhr = new XMLHttpRequest();
        xhr.open('POST', 'https://api.example.com/login');
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({
            username: 'test',
            password: 'secret',
            captcha: '1234'
        }))
    """)

    assert result['hooked'] == 'XMLHttpRequest.send'
    assert result['method'] == 'POST'
    assert result['url'] == 'https://api.example.com/login'
    assert 'test' in result['body']

    print(f"\n=== Hook XMLHttpRequest ===")
    print(f"✓ 拦截到请求: {result['method']} {result['url']}")
    print(f"✓ 请求头: {result['headers']}")
    print(f"✓ 请求体: {result['body'][:100]}...")


def test_hook_with_condition():
    """条件 Hook：只拦截特定情况"""
    ctx = never_jscore.Context()

    ctx.compile("""
        function processUser(userId) {
            if (userId === 12345) {
                // 只拦截特定用户
                $return({
                    intercepted: true,
                    userId: userId,
                    reason: 'Target user detected'
                });
            }

            // 正常处理其他用户
            return { userId, processed: true };
        }
    """)

    # 测试普通用户（不拦截）
    result1 = ctx.call("processUser", [999])
    assert result1['processed'] == True
    assert 'intercepted' not in result1

    # 测试目标用户（拦截）
    result2 = ctx.call("processUser", [12345])
    assert result2['intercepted'] == True
    assert 'processed' not in result2

    print(f"\n=== 条件 Hook ===")
    print(f"✓ 普通用户 999: {result1}")
    print(f"✓ 目标用户 12345: {result2}")


def test_extract_intermediate_value():
    """提取中间计算结果"""
    ctx = never_jscore.Context()

    # 模拟复杂的签名生成算法
    ctx.compile("""
        function generateSignature(params) {
            // 步骤 1: 参数排序
            const sorted = Object.keys(params).sort().map(k => k + '=' + params[k]).join('&');

            // 步骤 2: 添加时间戳
            const timestamp = Date.now();
            const message = sorted + '&timestamp=' + timestamp;

            // 步骤 3: 添加盐值
            const salt = 'SECRET_SALT';
            const withSalt = message + '&salt=' + salt;

            // 步骤 4: 计算哈希
            const hash = md5(withSalt);

            // 步骤 5: 最终签名
            const signature = hash.toUpperCase();

            return signature;
        }
    """)

    # 提取中间步骤
    result = ctx.evaluate("""
        // 重写函数以提取中间值
        const original = generateSignature;
        generateSignature = function(params) {
            const sorted = Object.keys(params).sort().map(k => k + '=' + params[k]).join('&');
            const timestamp = Date.now();
            const message = sorted + '&timestamp=' + timestamp;
            const salt = 'SECRET_SALT';
            const withSalt = message + '&salt=' + salt;

            // 提取中间结果
            $return({
                step1_sorted: sorted,
                step2_timestamp: timestamp,
                step3_message: message,
                step4_withSalt: withSalt
            });
        };

        // 执行
        generateSignature({ user: 'admin', action: 'login' })
    """)

    assert 'action=login&user=admin' in result['step1_sorted']
    assert 'timestamp=' in result['step3_message']
    assert 'SECRET_SALT' in result['step4_withSalt']

    print(f"\n=== 提取中间计算值 ===")
    print(f"✓ 步骤1 排序: {result['step1_sorted']}")
    print(f"✓ 步骤2 时间戳: {result['step2_timestamp']}")
    print(f"✓ 步骤3 消息: {result['step3_message'][:60]}...")
    print(f"✓ 步骤4 加盐: {result['step4_withSalt'][:60]}...")


def test_hook_in_async_function():
    """在异步函数中使用 Hook"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async function() {
            // 模拟异步加密
            const key = await Promise.resolve('async-key-123');

            const data = 'sensitive-data';

            // 在加密前拦截
            $return({
                hooked: 'async-context',
                key: key,
                data: data
            });

            // 不会执行
            const encrypted = btoa(data + key);
            return encrypted;
        })()
    """)

    assert result['hooked'] == 'async-context'
    assert result['key'] == 'async-key-123'
    assert result['data'] == 'sensitive-data'

    print(f"\n=== 异步函数中的 Hook ===")
    print(f"✓ 成功拦截异步执行")
    print(f"✓ 密钥: {result['key']}")
    print(f"✓ 数据: {result['data']}")


def test_hook_timer_callback():
    """在定时器回调中使用 Hook"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async function() {
            let capturedData = null;

            setTimeout(() => {
                // 模拟定时器中的加密操作
                const secret = 'timer-secret-' + Math.random();

                // 拦截并返回
                $return({
                    source: 'setTimeout',
                    secret: secret,
                    timestamp: Date.now()
                });
            }, 100);

            // 等待定时器执行（必须在异步环境）
            await new Promise(resolve => setTimeout(resolve, 200));
        })()
    """)

    assert result['source'] == 'setTimeout'
    assert 'timer-secret-' in result['secret']

    print(f"\n=== 定时器回调中的 Hook ===")
    print(f"✓ 拦截来源: {result['source']}")
    print(f"✓ 密钥: {result['secret']}")


def test_multiple_hooks():
    """多个 Hook 点"""
    ctx = never_jscore.Context()

    ctx.compile("""
        const hooks = [];

        function step1(data) {
            hooks.push({ step: 1, data });
            return data.toUpperCase();
        }

        function step2(data) {
            hooks.push({ step: 2, data });
            return btoa(data);
        }

        function step3(data) {
            hooks.push({ step: 3, data });
            return md5(data);
        }

        function pipeline(input) {
            const r1 = step1(input);
            const r2 = step2(r1);
            const r3 = step3(r2);
            return r3;
        }
    """)

    # 在 step2 处拦截
    result = ctx.evaluate("""
        // Hook step2
        const original = step2;
        step2 = function(data) {
            hooks.push({ step: 'HOOK', data });

            // 拦截并返回所有历史记录
            $return({
                interceptedAt: 'step2',
                currentData: data,
                history: hooks
            });
        };

        pipeline('hello')
    """)

    assert result['interceptedAt'] == 'step2'
    assert result['currentData'] == 'HELLO'
    assert len(result['history']) >= 2

    print(f"\n=== 多个 Hook 点 ===")
    print(f"✓ 拦截位置: {result['interceptedAt']}")
    print(f"✓ 当前数据: {result['currentData']}")
    print(f"✓ 历史记录: {result['history']}")


def test_real_world_token_extraction():
    """实战：提取 Token 生成逻辑"""
    ctx = never_jscore.Context()

    # 模拟某个网站的 Token 生成
    ctx.compile("""
        const TokenGenerator = {
            secret: 'SUPER_SECRET_KEY_12345',

            generateToken(userId, timestamp) {
                const raw = userId + '|' + timestamp + '|' + this.secret;
                const hash = sha256(raw);
                const token = btoa(hash);
                return token;
            }
        };

        function login(username, password) {
            const userId = btoa(username);
            const timestamp = Date.now();
            const token = TokenGenerator.generateToken(userId, timestamp);

            return {
                success: true,
                token: token
            };
        }
    """)

    # Hook Token 生成，提取密钥
    result = ctx.evaluate("""
        // Hook generateToken
        const original = TokenGenerator.generateToken;
        TokenGenerator.generateToken = function(userId, timestamp) {
            // 拦截并返回所有参数和密钥
            $return({
                hooked: 'TokenGenerator.generateToken',
                userId: userId,
                timestamp: timestamp,
                secret: this.secret,  // 提取密钥！
                rawMessage: userId + '|' + timestamp + '|' + this.secret
            });
        };

        // 执行登录（会触发 Hook）
        login('admin', 'password123')
    """)

    assert result['hooked'] == 'TokenGenerator.generateToken'
    assert result['secret'] == 'SUPER_SECRET_KEY_12345'  # 成功提取密钥！
    assert '|' in result['rawMessage']

    print(f"\n=== 实战：提取 Token 密钥 ===")
    print(f"✓ 用户ID: {result['userId']}")
    print(f"✓ 时间戳: {result['timestamp']}")
    print(f"✓ 密钥: {result['secret']}")  # 关键信息！
    print(f"✓ 原始消息: {result['rawMessage'][:60]}...")


if __name__ == "__main__":
    print("=" * 60)
    print("测试 Hook 拦截系统")
    print("=" * 60)

    test_basic_return()
    test_return_alias()
    test_hook_encryption_function()
    test_hook_xhr_send()
    test_hook_with_condition()
    test_extract_intermediate_value()
    test_hook_in_async_function()
    test_hook_timer_callback()
    test_multiple_hooks()
    test_real_world_token_extraction()

    print("\n" + "=" * 60)
    print("✅ 所有 Hook 拦截测试通过！")
    print("=" * 60)
    print("\n💡 提示：使用 $return() 可以在任意位置拦截 JS 执行")
    print("   这是逆向工程中提取中间结果的强大工具！")
