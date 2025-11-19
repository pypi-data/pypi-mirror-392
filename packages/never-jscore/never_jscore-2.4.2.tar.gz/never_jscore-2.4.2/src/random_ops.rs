// random_ops.rs - Operations for controlling random number generation
use deno_core::{extension, op2, OpState};
use rand::SeedableRng;

#[op2(fast)]
/// Set the random seed for deterministic random number generation
///
/// # Arguments
/// * `seed` - The seed value (u64)
///
/// # Example
/// ```javascript
/// Deno.core.ops.op_set_random_seed(12345);
/// Math.random(); // Will be deterministic
/// ```
pub fn op_set_random_seed(state: &mut OpState, seed: u32) {
    if let Some(rng_state) = state.try_borrow_mut::<crate::random_state::RngState>() {
        rng_state.seed = Some(seed as u64);
        rng_state.seeded_rng = Some(rand::rngs::StdRng::seed_from_u64(seed as u64));
    }
}

#[op2(fast)]
/// Reset to non-deterministic random number generation
pub fn op_reset_random_seed(state: &mut OpState) {
    if let Some(rng_state) = state.try_borrow_mut::<crate::random_state::RngState>() {
        rng_state.seed = None;
        rng_state.seeded_rng = None;
    }
}

#[op2(fast)]
/// Get current random seed (returns 0 if not set)
pub fn op_get_random_seed(state: &mut OpState) -> u32 {
    state
        .try_borrow::<crate::random_state::RngState>()
        .and_then(|s| s.seed)
        .unwrap_or(0) as u32
}

extension!(
    random_ops,
    ops = [
        op_set_random_seed,
        op_reset_random_seed,
        op_get_random_seed,
    ],
    state = |state| {
        // Initialize RngState for every runtime
        state.put(crate::random_state::RngState::default());
    },
);
