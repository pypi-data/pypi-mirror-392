"""
测试 Web API 和浏览器环境

展示内置的 fetch、localStorage、crypto 等 Web API 功能
"""

import never_jscore


def test_crypto_apis():
    """测试加密 API"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        ({
            md5: md5('hello'),
            sha1: sha1('hello'),
            sha256: sha256('hello'),
            btoa: btoa('hello'),
            atob: atob(btoa('hello')),
            uuid: crypto.randomUUID()
        })
    """)

    assert len(result['md5']) == 32, "MD5 应该是 32 位"
    assert len(result['sha1']) == 40, "SHA1 应该是 40 位"
    assert len(result['sha256']) == 64, "SHA256 应该是 64 位"
    assert result['btoa'] == 'aGVsbG8=', "Base64 编码正确"
    assert result['atob'] == 'hello', "Base64 解码正确"
    assert len(result['uuid']) == 36, "UUID 格式正确"

    print(f"✓ MD5: {result['md5']}")
    print(f"✓ SHA256: {result['sha256']}")
    print(f"✓ UUID: {result['uuid']}")


def test_url_encoding():
    """测试 URL 编码"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const text = '你好世界 & test=123';
        ({
            original: text,
            encoded: encodeURIComponent(text),
            decoded: decodeURIComponent(encodeURIComponent(text))
        })
    """)

    assert result['decoded'] == result['original']
    assert '%' in result['encoded']

    print(f"✓ 原始: {result['original']}")
    print(f"✓ 编码: {result['encoded']}")


def test_url_parse():
    """测试 URL 解析"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const url = new URL('https://example.com:8080/path/to/page?q=search&lang=en#section');
        ({
            href: url.href,
            protocol: url.protocol,
            hostname: url.hostname,
            port: url.port,
            pathname: url.pathname,
            search: url.search,
            hash: url.hash
        })
    """)

    assert result['protocol'] == 'https:'
    assert result['hostname'] == 'example.com'
    assert result['port'] == '8080'
    assert result['pathname'] == '/path/to/page'

    print(f"✓ URL 解析成功")
    print(f"  - hostname: {result['hostname']}")
    print(f"  - pathname: {result['pathname']}")


def test_url_search_params():
    """测试 URLSearchParams"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const params = new URLSearchParams('a=1&b=2&c=3');
        ({
            a: params.get('a'),
            b: params.get('b'),
            has_d: params.has('d'),
            toString: params.toString()
        })
    """)

    assert result['a'] == '1'
    assert result['b'] == '2'
    assert result['has_d'] == False

    print(f"✓ URLSearchParams: {result['toString']}")


def test_local_storage():
    """测试 localStorage"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        // 存储数据
        localStorage.setItem('token', 'abc123');
        localStorage.setItem('user', JSON.stringify({ id: 1, name: 'Alice' }));

        // 读取数据
        const token = localStorage.getItem('token');
        const user = JSON.parse(localStorage.getItem('user'));
        const length = localStorage.length;

        // 删除数据
        localStorage.removeItem('token');
        const tokenAfterRemove = localStorage.getItem('token');

        ({
            token,
            user,
            length,
            tokenAfterRemove
        })
    """)

    assert result['token'] == 'abc123'
    assert result['user']['name'] == 'Alice'
    assert result['length'] >= 2
    assert result['tokenAfterRemove'] is None

    print(f"✓ localStorage 读写成功")
    print(f"  - token: {result['token']}")
    print(f"  - user: {result['user']}")


def test_session_storage():
    """测试 sessionStorage"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        sessionStorage.setItem('tempData', 'temporary');
        const data = sessionStorage.getItem('tempData');

        sessionStorage.clear();
        const afterClear = sessionStorage.getItem('tempData');

        ({
            data,
            afterClear
        })
    """)

    assert result['data'] == 'temporary'
    assert result['afterClear'] is None

    print(f"✓ sessionStorage 工作正常")


def test_timers():
    """测试定时器 API"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            let counter = 0;

            // setTimeout
            await new Promise(resolve => {
                setTimeout(() => {
                    counter++;
                    resolve();
                }, 50);
            });

            // setInterval
            await new Promise(resolve => {
                let count = 0;
                const timer = setInterval(() => {
                    counter++;
                    count++;
                    if (count >= 3) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 20);
            });

            return counter;
        })()
    """)

    assert result >= 4, "定时器应该执行"

    print(f"✓ 定时器执行次数: {result}")


def test_text_encoder_decoder():
    """测试 TextEncoder/TextDecoder"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const encoder = new TextEncoder();
        const decoder = new TextDecoder();

        const text = 'Hello 世界';
        const encoded = encoder.encode(text);
        const decoded = decoder.decode(encoded);

        ({
            original: text,
            encodedLength: encoded.length,
            decoded: decoded,
            match: text === decoded
        })
    """)

    assert result['match'] == True
    assert result['decoded'] == 'Hello 世界'

    print(f"✓ TextEncoder/Decoder 正常")
    print(f"  - 编码长度: {result['encodedLength']} 字节")


def test_buffer():
    """测试 Buffer（Node.js 兼容）"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const buf1 = Buffer.from('hello');
        const buf2 = Buffer.from([72, 101, 108, 108, 111]);

        ({
            buf1String: buf1.toString(),
            buf2String: buf2.toString(),
            buf1Hex: buf1.toString('hex'),
            buf1Base64: buf1.toString('base64'),
            equal: buf1.toString() === buf2.toString()
        })
    """)

    assert result['buf1String'] == 'hello'
    assert result['buf2String'] == 'Hello'
    assert result['buf1Hex'] == '68656c6c6f'
    assert result['buf1Base64'] == 'aGVsbG8='

    print(f"✓ Buffer 工作正常")
    print(f"  - Hex: {result['buf1Hex']}")
    print(f"  - Base64: {result['buf1Base64']}")


def test_performance_api():
    """测试 Performance API"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const start = performance.now();

        // 执行一些操作
        let sum = 0;
        for (let i = 0; i < 1000; i++) {
            sum += i;
        }

        const end = performance.now();
        const elapsed = end - start;

        // 测试 mark 和 measure
        performance.mark('test-start');
        performance.mark('test-end');
        const measure = performance.measure('test', 'test-start', 'test-end');

        ({
            elapsed,
            sum,
            measureName: measure.name,
            hasTimeOrigin: typeof performance.timeOrigin === 'number'
        })
    """)

    assert result['sum'] == 499500
    assert result['elapsed'] >= 0
    assert result['measureName'] == 'test'
    assert result['hasTimeOrigin'] == True

    print(f"✓ Performance API 工作正常")
    print(f"  - 耗时: {result['elapsed']:.3f}ms")


def test_blob_api():
    """测试 Blob API"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            const blob = new Blob(['Hello', ' ', 'World'], { type: 'text/plain' });

            const text = await blob.text();
            const size = blob.size;
            const type = blob.type;

            // 测试 slice
            const sliced = blob.slice(0, 5);
            const slicedText = await sliced.text();

            return {
                text,
                size,
                type,
                slicedText
            };
        })()
    """)

    assert result['text'] == 'Hello World'
    assert result['size'] > 0
    assert result['type'] == 'text/plain'
    assert result['slicedText'] == 'Hello'

    print(f"✓ Blob API 工作正常")
    print(f"  - 内容: {result['text']}")
    print(f"  - 大小: {result['size']} 字节")


def test_formdata():
    """测试 FormData"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const form = new FormData();
        form.append('username', 'alice');
        form.append('password', 'secret');
        form.append('age', '25');

        ({
            username: form.get('username'),
            password: form.get('password'),
            hasEmail: form.has('email'),
            keys: Array.from(form.keys())
        })
    """)

    assert result['username'] == 'alice'
    assert result['password'] == 'secret'
    assert result['hasEmail'] == False
    assert 'username' in result['keys']

    print(f"✓ FormData 工作正常")
    print(f"  - 字段: {result['keys']}")


def test_event_target():
    """测试 Event 和 EventTarget"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const target = new EventTarget();
        let triggered = false;
        let eventData = null;

        target.addEventListener('custom', (e) => {
            triggered = true;
            eventData = e.type;
        });

        const event = new Event('custom');
        target.dispatchEvent(event);

        ({
            triggered,
            eventData
        })
    """)

    assert result['triggered'] == True
    assert result['eventData'] == 'custom'

    print(f"✓ Event/EventTarget 工作正常")


def test_real_world_web_api_usage():
    """实战：综合使用 Web API"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            // 1. 生成用户会话
            const sessionId = crypto.randomUUID();

            // 2. 存储到 localStorage
            localStorage.setItem('sessionId', sessionId);

            // 3. 创建签名数据
            const timestamp = Date.now();
            const data = {
                user: 'admin',
                timestamp: timestamp
            };

            // 4. 序列化数据
            const dataStr = JSON.stringify(data);

            // 5. 计算签名
            const signature = sha256(dataStr + sessionId);

            // 6. Base64 编码
            const encoded = btoa(signature);

            // 7. URL 编码（用于传输）
            const urlSafe = encodeURIComponent(encoded);

            // 8. 性能测量
            const measure = performance.now();

            return {
                sessionId,
                signature: signature.substring(0, 16) + '...',
                encoded: encoded.substring(0, 20) + '...',
                urlSafe: urlSafe.substring(0, 20) + '...',
                performanceTime: measure
            };
        })()
    """)

    assert len(result['sessionId']) == 36  # UUID
    assert 'signature' in result
    assert 'encoded' in result

    print(f"\n=== 实战：综合 Web API 使用 ===")
    print(f"✓ Session ID: {result['sessionId']}")
    print(f"✓ 签名: {result['signature']}")
    print(f"✓ Base64 编码: {result['encoded']}")
    print(f"✓ 性能时间: {result['performanceTime']:.3f}ms")


if __name__ == "__main__":
    print("=" * 60)
    print("测试 Web API 和浏览器环境")
    print("=" * 60)

    test_crypto_apis()
    test_url_encoding()
    test_url_parse()
    test_url_search_params()
    test_local_storage()
    test_session_storage()
    test_timers()
    test_text_encoder_decoder()
    test_buffer()
    test_performance_api()
    test_blob_api()
    test_formdata()
    test_event_target()
    test_real_world_web_api_usage()

    print("\n" + "=" * 60)
    print("✅ 所有 Web API 测试通过！")
    print("=" * 60)
    print("\n💡 提示：never-jscore 内置了 800+ 行 Web API polyfill")
    print("   无需额外配置即可使用浏览器和 Node.js API！")
