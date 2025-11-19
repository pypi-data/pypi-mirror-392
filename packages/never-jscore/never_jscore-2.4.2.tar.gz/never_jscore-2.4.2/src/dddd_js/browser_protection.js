// ============================================
// Browser Environment Protection System
// 浏览器环境保护系统 - 防止环境检测
// ============================================

(function() {
    'use strict';

    const log = (...args) => {
        if (typeof globalThis.__NEVER_JSCORE_LOGGING__ !== 'undefined' && globalThis.__NEVER_JSCORE_LOGGING__) {
            console.log('[BrowserProtection]', ...args);
        }
    };

    log('Initializing browser environment protection...');

    // ============================================
    // 1. 隐藏 Deno 特征
    // ============================================

    // 保存原始 Deno 对象（仅内部使用）
    const __internalDeno = globalThis.Deno;

    // 删除全局 Deno
    delete globalThis.Deno;

    // 重新定义为 undefined（防止检测 'Deno' in window）
    Object.defineProperty(globalThis, 'Deno', {
        value: undefined,
        writable: false,
        enumerable: false,
        configurable: false
    });

    // 内部访问 Deno 的安全方法
    globalThis.__getDeno = function() {
        return __internalDeno;
    };

    log('Deno object hidden');

    // ============================================
    // 2. 原生函数保护 - toString 伪装
    // ============================================

    /**
     * 让函数的 toString() 返回看起来像原生代码
     */
    function makeNative(func, name) {
        const nativeString = `function ${name}() { [native code] }`;

        Object.defineProperty(func, 'toString', {
            value: function() {
                return nativeString;
            },
            writable: false,
            enumerable: false,
            configurable: false
        });

        Object.defineProperty(func, 'name', {
            value: name,
            writable: false,
            enumerable: false,
            configurable: true
        });

        return func;
    }

    /**
     * 批量保护对象的方法
     */
    function protectObjectMethods(obj, objName) {
        if (!obj) return;

        for (const key of Object.getOwnPropertyNames(obj)) {
            try {
                const value = obj[key];
                if (typeof value === 'function') {
                    makeNative(value, key);
                }
            } catch (e) {
                // 某些属性可能无法访问，忽略
            }
        }

        // 保护原型链
        const proto = Object.getPrototypeOf(obj);
        if (proto && proto !== Object.prototype) {
            for (const key of Object.getOwnPropertyNames(proto)) {
                try {
                    const value = proto[key];
                    if (typeof value === 'function') {
                        makeNative(value, key);
                    }
                } catch (e) {
                    // 忽略
                }
            }
        }

        log(`Protected methods of ${objName}`);
    }

    // ============================================
    // 3. 浏览器特有对象的原型链保护
    // ============================================

    /**
     * 确保原型链符合浏览器规范
     */
    function fixPrototypeChain(obj, expectedProto) {
        try {
            if (Object.getPrototypeOf(obj) !== expectedProto) {
                Object.setPrototypeOf(obj, expectedProto);
            }
        } catch (e) {
            log(`Cannot fix prototype of ${obj.constructor.name}:`, e.message);
        }
    }

    // ============================================
    // 4. 属性描述符保护
    // ============================================

    /**
     * 确保属性描述符符合浏览器标准
     */
    function protectPropertyDescriptors(obj, properties) {
        for (const [key, descriptor] of Object.entries(properties)) {
            try {
                Object.defineProperty(obj, key, {
                    ...descriptor,
                    configurable: descriptor.configurable !== undefined ? descriptor.configurable : false
                });
            } catch (e) {
                log(`Cannot protect property ${key}:`, e.message);
            }
        }
    }

    // ============================================
    // 5. Navigator 对象保护
    // ============================================

    if (typeof navigator !== 'undefined') {
        // 确保 navigator 不可配置
        const navigatorDescriptor = Object.getOwnPropertyDescriptor(globalThis, 'navigator');
        if (navigatorDescriptor && navigatorDescriptor.configurable) {
            Object.defineProperty(globalThis, 'navigator', {
                value: navigator,
                writable: false,
                enumerable: true,
                configurable: false
            });
        }

        // 保护 navigator 的方法
        protectObjectMethods(navigator, 'navigator');

        // 确保关键属性不可修改
        const navigatorProps = {
            userAgent: { writable: false, enumerable: true, configurable: false },
            platform: { writable: false, enumerable: true, configurable: false },
            language: { writable: false, enumerable: true, configurable: false },
            webdriver: { writable: false, enumerable: true, configurable: false }
        };

        protectPropertyDescriptors(navigator, navigatorProps);
    }

    // ============================================
    // 6. Window/GlobalThis 对象保护
    // ============================================

    // 确保 window === globalThis（浏览器特征）
    if (typeof window === 'undefined') {
        globalThis.window = globalThis;
    }

    // 确保 self === globalThis
    if (typeof self === 'undefined') {
        globalThis.self = globalThis;
    }

    // 确保 top === globalThis（在非 iframe 环境）
    if (typeof top === 'undefined') {
        globalThis.top = globalThis;
    }

    // 确保 parent === globalThis
    if (typeof parent === 'undefined') {
        globalThis.parent = globalThis;
    }

    // 保护 window 的原生方法
    const windowMethods = [
        'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
        'requestAnimationFrame', 'cancelAnimationFrame',
        'fetch', 'btoa', 'atob'
    ];

    for (const method of windowMethods) {
        if (typeof globalThis[method] === 'function') {
            makeNative(globalThis[method], method);
        }
    }

    // ============================================
    // 7. Document 对象保护
    // ============================================

    if (typeof document !== 'undefined') {
        protectObjectMethods(document, 'document');

        // 确保 document.documentElement 存在
        if (!document.documentElement) {
            Object.defineProperty(document, 'documentElement', {
                value: { tagName: 'HTML', nodeName: 'HTML' },
                writable: false,
                enumerable: true,
                configurable: false
            });
        }
    }

    // ============================================
    // 8. Console 对象保护
    // ============================================

    if (typeof console !== 'undefined') {
        const consoleMethods = ['log', 'warn', 'error', 'info', 'debug', 'trace', 'dir', 'table'];

        for (const method of consoleMethods) {
            if (typeof console[method] === 'function') {
                makeNative(console[method], method);
            }
        }

        // 确保 console.toString() 返回正确格式
        Object.defineProperty(console, 'toString', {
            value: function() {
                return '[object Console]';
            },
            writable: false,
            enumerable: false,
            configurable: false
        });
    }

    // ============================================
    // 9. XMLHttpRequest 保护
    // ============================================

    if (typeof XMLHttpRequest !== 'undefined') {
        makeNative(XMLHttpRequest, 'XMLHttpRequest');
        protectObjectMethods(XMLHttpRequest.prototype, 'XMLHttpRequest.prototype');
    }

    // ============================================
    // 10. Function.prototype.toString 保护
    // ============================================

    const originalFunctionToString = Function.prototype.toString;

    Function.prototype.toString = new Proxy(originalFunctionToString, {
        apply(target, thisArg, args) {
            // 如果函数已经被保护（有自定义 toString），使用它
            const ownToString = Object.getOwnPropertyDescriptor(thisArg, 'toString');
            if (ownToString && ownToString.value !== Function.prototype.toString) {
                return ownToString.value.call(thisArg);
            }

            // 否则使用原始实现
            return target.apply(thisArg, args);
        }
    });

    // 保护 toString 本身
    makeNative(Function.prototype.toString, 'toString');

    // ============================================
    // 11. Chrome/WebKit 特有属性
    // ============================================

    // chrome 对象（Chrome 浏览器特征）
    if (typeof chrome === 'undefined') {
        globalThis.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };

        Object.defineProperty(globalThis, 'chrome', {
            value: globalThis.chrome,
            writable: false,
            enumerable: true,
            configurable: false
        });
    }

    // ============================================
    // 12. 隐藏特征检测函数
    // ============================================

    /**
     * 检测当前环境是否暴露了 Node/Deno 特征
     * @returns {Array} 检测到的问题列表
     */
    globalThis.__checkEnvironment = function() {
        const issues = [];

        // 检查 Deno
        if (typeof Deno !== 'undefined' && Deno !== undefined) {
            issues.push('Deno object is visible');
        }

        // 检查 process (Node.js)
        if (typeof process !== 'undefined' && process.versions && process.versions.node) {
            issues.push('Node.js process object detected');
        }

        // 检查 require (Node.js/CommonJS)
        if (typeof require === 'function') {
            issues.push('require() function detected');
        }

        // 检查 module (Node.js)
        if (typeof module !== 'undefined' && module.exports) {
            issues.push('module.exports detected');
        }

        // 检查 __dirname, __filename (Node.js)
        if (typeof __dirname !== 'undefined') {
            issues.push('__dirname detected');
        }

        // 检查 window
        if (typeof window === 'undefined') {
            issues.push('window is undefined');
        } else if (window !== globalThis) {
            issues.push('window !== globalThis');
        }

        // 检查 navigator
        if (typeof navigator === 'undefined') {
            issues.push('navigator is undefined');
        } else {
            if (navigator.userAgent.includes('Node.js') || navigator.userAgent.includes('Deno')) {
                issues.push('User-Agent contains Node.js/Deno');
            }
        }

        // 检查 document
        if (typeof document === 'undefined') {
            issues.push('document is undefined');
        }

        return issues;
    };

    // ============================================
    // 13. 自动检测并报告
    // ============================================

    const issues = globalThis.__checkEnvironment();
    if (issues.length > 0) {
        log('Environment protection warnings:');
        issues.forEach(issue => log('  -', issue));
    } else {
        log('Environment protection complete - no issues detected');
    }

    // ============================================
    // 14. 导出保护函数（供用户调用）
    // ============================================

    /**
     * 保护自定义对象，使其看起来像浏览器原生对象
     * @param {Object} obj - 要保护的对象
     * @param {String} name - 对象名称
     * @param {Object} options - 保护选项
     */
    globalThis.$protect = function(obj, name, options = {}) {
        const {
            methods = true,      // 保护方法
            properties = true,   // 保护属性
            prototype = true,    // 保护原型
            freeze = false       // 是否冻结对象
        } = options;

        if (methods) {
            protectObjectMethods(obj, name);
        }

        if (properties && options.propertyDescriptors) {
            protectPropertyDescriptors(obj, options.propertyDescriptors);
        }

        if (prototype && options.expectedProto) {
            fixPrototypeChain(obj, options.expectedProto);
        }

        if (freeze) {
            Object.freeze(obj);
        }

        log(`Protected object: ${name}`);
        return obj;
    };

    /**
     * 使函数看起来像原生函数
     * @param {Function} func - 要保护的函数
     * @param {String} name - 函数名
     */
    globalThis.$makeNative = makeNative;

    log('Browser protection system loaded');

})();
