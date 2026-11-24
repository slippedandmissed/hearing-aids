//! Profiles: one TOML file that the desktop tool reads at run time and the XIAO firmware bakes in at build time.
//!
//! ```toml
//! preset = "conductive"        # start from a built-in preset (default "passthrough")
//! limit_dbfs = -20.0           # then override any field; tables merge field by field
//! [feedback]
//! delay = 12
//! ```
//! Arrays (`bands`, `crossover_hz`, `eq`) are replaced whole, so give every entry in full.
use hearing_dsp::Config;
use toml::{Table, Value};

/// A built-in preset by name.
pub fn preset(name: &str) -> Result<Config, String> {
    match name {
        "passthrough" => Ok(Config::PASSTHROUGH),
        "conductive" => Ok(Config::CONDUCTIVE_GUESS),
        other => Err(format!("unknown preset {other:?} (known: passthrough, conductive)")),
    }
}

fn merge(base: &mut Table, over: Table) {
    for (k, v) in over {
        match (base.get_mut(&k), v) {
            (Some(Value::Table(b)), Value::Table(o)) => merge(b, o),
            (Some(_), v) => {
                base.insert(k, v);
            }
            // `check_keys` has already rejected keys the base does not have.
            (None, _) => {}
        }
    }
}

/// Every key in `over` must exist in `base`, otherwise a typo would silently do nothing.
fn check_keys(base: &Table, over: &Table, path: &str) -> Result<(), String> {
    for (k, v) in over {
        let here = if path.is_empty() { k.clone() } else { format!("{path}.{k}") };
        match (base.get(k), v) {
            (None, _) => return Err(format!("unknown setting {here:?}")),
            (Some(Value::Table(b)), Value::Table(o)) => check_keys(b, o, &here)?,
            _ => {}
        }
    }
    Ok(())
}

/// Parse a profile's text.
pub fn parse(text: &str) -> Result<Config, String> {
    let mut over: Table = text.parse().map_err(|e| format!("profile: {e}"))?;
    let name = match over.remove("preset") {
        None => "passthrough".to_string(),
        Some(Value::String(s)) => s,
        Some(_) => return Err("preset must be a string".into()),
    };
    let mut base = to_table(&preset(&name)?)?;
    check_keys(&base, &over, "")?;
    merge(&mut base, over);
    Value::Table(base).try_into().map_err(|e| format!("profile: {e}"))
}

pub fn load(path: &str) -> Result<Config, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{path}: {e}"))?;
    parse(&text).map_err(|e| format!("{path}: {e}"))
}

fn to_table(cfg: &Config) -> Result<Table, String> {
    match Value::try_from(cfg).map_err(|e| e.to_string())? {
        Value::Table(t) => Ok(t),
        _ => Err("config is not a table".into()),
    }
}

/// Round floats to 6 significant digits so printed profiles read as written (an `f32` widened to `f64` otherwise
/// prints as 0.10000000149011612).
fn tidy(v: &mut Value) {
    match v {
        Value::Float(x) => *x = format!("{:.6e}", *x).parse().unwrap_or(*x),
        Value::Array(a) => a.iter_mut().for_each(tidy),
        Value::Table(t) => t.iter_mut().for_each(|(_, v)| tidy(v)),
        _ => {}
    }
}

/// A complete profile as TOML text, for use as a starting point.
pub fn to_toml(cfg: &Config) -> Result<String, String> {
    let mut v = Value::Table(to_table(cfg)?);
    tidy(&mut v);
    toml::to_string_pretty(&v).map_err(|e| e.to_string())
}

/// The Rust expression for a `Config` (the `Debug` output is valid struct-literal syntax once the types are in
/// scope), for `include!` in a `const`.
pub fn to_rust(cfg: &Config) -> String {
    format!("{cfg:#?}")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_profile_is_the_passthrough_preset() {
        assert_eq!(parse("").unwrap(), Config::PASSTHROUGH);
    }

    #[test]
    fn preset_then_override() {
        let c = parse("preset = \"conductive\"\nlimit_dbfs = -25.0\n[feedback]\ndelay = 9\n").unwrap();
        assert_eq!(c.limit_dbfs, -25.0);
        assert_eq!(c.feedback.delay, 9);
        assert_eq!(c.feedback.taps, Config::CONDUCTIVE_GUESS.feedback.taps, "untouched fields keep the preset");
        assert_eq!(c.bands, Config::CONDUCTIVE_GUESS.bands);
    }

    #[test]
    fn a_typo_is_an_error_not_a_silent_no_op() {
        assert!(parse("limit_dbf = -20.0").unwrap_err().contains("limit_dbf"));
        assert!(parse("[feedback]\ndelai = 3").unwrap_err().contains("feedback.delai"));
        assert!(parse("preset = \"loud\"").is_err());
    }

    #[test]
    fn printed_toml_round_trips() {
        for p in [Config::PASSTHROUGH, Config::CONDUCTIVE_GUESS] {
            let text = to_toml(&p).unwrap();
            let back = parse(&text).unwrap();
            // 6 significant digits: compare the fields that matter with a tolerance.
            assert!((back.limit_dbfs - p.limit_dbfs).abs() < 1e-3);
            assert_eq!(back.feedback.taps, p.feedback.taps);
            for (a, b) in back.bands.iter().zip(&p.bands) {
                assert!((a.gain_db - b.gain_db).abs() < 1e-3 && a.ratio == b.ratio);
            }
        }
    }

    #[test]
    fn wrong_type_is_reported() {
        assert!(parse("limit_dbfs = \"quiet\"").is_err());
    }

    #[test]
    fn rust_source_names_the_fields() {
        let s = to_rust(&Config::PASSTHROUGH);
        assert!(s.starts_with("Config {") && s.contains("limit_dbfs: -18.2"), "{s}");
    }
}
