use std::cell::RefCell;

/// JavaScript 执行结果存储
///
/// 用于在 Rust 和 JavaScript 之间传递执行结果。
/// 通过 Deno Core 的 op 机制，JavaScript 可以将结果存储到这里。
pub struct ResultStorage {
    pub value: RefCell<Option<String>>,
    early_return: RefCell<bool>,  // 标记是否是提前返回（用于Hook拦截）
    terminated: RefCell<bool>,    // 标记是否应该终止runtime
}

impl ResultStorage {
    pub fn new() -> Self {
        Self {
            value: RefCell::new(None),
            early_return: RefCell::new(false),
            terminated: RefCell::new(false),
        }
    }

    pub fn clear(&self) {
        *self.value.borrow_mut() = None;
        *self.early_return.borrow_mut() = false;
        *self.terminated.borrow_mut() = false;
    }

    pub fn store(&self, value: String) {
        *self.value.borrow_mut() = Some(value);
    }

    pub fn take(&self) -> Option<String> {
        self.value.borrow_mut().take()
    }

    /// 标记为提前返回（Hook拦截）
    pub fn mark_early_return(&self) {
        *self.early_return.borrow_mut() = true;
    }

    /// 检查是否是提前返回
    pub fn is_early_return(&self) -> bool {
        *self.early_return.borrow()
    }

    /// 标记为已终止（强制停止runtime）
    pub fn mark_terminated(&self) {
        *self.terminated.borrow_mut() = true;
    }

    /// 检查是否应该终止
    pub fn is_terminated(&self) -> bool {
        *self.terminated.borrow()
    }
}

impl Default for ResultStorage {
    fn default() -> Self {
        Self::new()
    }
}
