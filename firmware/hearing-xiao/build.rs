//! Two jobs: put memory.x where the linker finds it (cargo runs the linker from the workspace root, not this
//! directory), and turn `profiles/device.toml` into a `const` Rust expression (`$OUT_DIR/profile.rs`).
use std::{env, fs, path::PathBuf};

fn main() {
    let out = PathBuf::from(env::var_os("OUT_DIR").unwrap());
    fs::copy("memory.x", out.join("memory.x")).unwrap();
    println!("cargo:rustc-link-search={}", out.display());
    println!("cargo:rerun-if-changed=memory.x");

    let profile = "../profiles/device.toml";
    println!("cargo:rerun-if-changed={profile}");
    let cfg = hearing_profile::load(profile).unwrap_or_else(|e| panic!("{e}"));
    fs::write(out.join("profile.rs"), hearing_profile::to_rust(&cfg)).unwrap();
}
