use actix_web::web::Data;
use std::collections::HashMap;
use std::sync::Mutex;

// State is just a hashmap
pub type State<'a, T> = HashMap<&'a str, T>;
pub type AppState<'a, T> = Data<Mutex<State<'a, T>>>;

/// Create a new state instance and wrap in a mutex for sharing across threads
/// Further wrap into an Actix Data instance.
pub fn new_state<'a, T>() -> AppState<'a, T> {
    let state = State::<T>::new();
    Data::new(Mutex::new(state))
}

/// Sets an entry in the application state by key.
/// Returns Some(T) only if the entry exists (update operation).
/// Returns None if the entry did not alreay exist (insert operation).
#[allow(dead_code)]
pub fn set<'a, T>(data: AppState<'a, T>, key: &'a str, value: T) -> Option<T> {
    let mut hashmap = data.lock().expect("Could not acquire lock");
    hashmap.insert(key, value)
}

/// Get a copy of an application state entry by key.
/// Returns Some(T) only if the entry exists.
#[allow(dead_code)]
pub fn get<'a, T>(data: AppState<'a, T>, key: &'a str) -> Option<T>
where
    T: Clone,
{
    let hashmap = data.lock().expect("Could not acquire lock");
    Some(hashmap.get(key)?.to_owned())
}

/// Removes an entry in the application state by key.
/// Returns Some(T) only if the entry existed before removal.
#[allow(dead_code)]
pub fn delete<'a, T>(data: AppState<'a, T>, key: &'a str) -> Option<T> {
    let mut hashmap = data.lock().expect("Could not acquire lock");
    hashmap.remove(key)
}

