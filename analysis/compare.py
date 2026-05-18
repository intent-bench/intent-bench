#!/usr/bin/env python3
"""Statistical analysis for intent-bench experiments.

Computes significance tests, token efficiency ratios, and entropy
correlations from experiment results.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from scipy import stats


def load_ledger(path: str = "results/summary.csv", score_version: str = None) -> pd.DataFrame:
    """Load and validate the experiment ledger.

    If score_version is None (default), filter to the latest score_version.
    If score_version is "all", return all rows regardless of version.
    """
    df = pd.read_csv(path)
    required = [
        "experiment",
        "condition",
        "total_tokens",
        "outcome",
        "input_tokens",
        "output_tokens",
        "tool_tokens",
        "planning_tokens",
        "execution_tokens",
        "turns",
        "backtracks",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"ERROR: Missing columns: {missing}", file=sys.stderr)
        sys.exit(1)
    if "score_version" in df.columns and score_version != "all":
        if score_version is not None:
            df = df[df["score_version"].astype(str) == str(score_version)]
        else:
            latest = df["score_version"].max()
            df = df[df["score_version"] == latest]
    return df


def filter_pass(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["outcome"] == "PASS"]


def filter_no_errors(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df["outcome"].isin(["ERROR", "TIMEOUT"])]


def compute_stats(series: pd.Series) -> dict:
    if len(series) == 0:
        return {"mean": 0, "median": 0, "std": 0, "n": 0}
    return {
        "mean": round(float(series.mean()), 1),
        "median": round(float(series.median()), 1),
        "std": round(float(series.std()), 1),
        "n": int(len(series)),
    }


def bootstrap_ci(a: pd.Series, b: pd.Series, n_boot: int = 10000, alpha: float = 0.05) -> dict:
    """Bootstrap 95% CI for the ratio of means (a/b)."""
    import numpy as np

    if len(a) == 0 or len(b) == 0:
        return {"ratio": 0, "ci_lower": 0, "ci_upper": 0}

    rng = np.random.default_rng(42)
    ratios = []
    for _ in range(n_boot):
        a_sample = rng.choice(a.values, size=len(a), replace=True)
        b_sample = rng.choice(b.values, size=len(b), replace=True)
        b_mean = b_sample.mean()
        if b_mean > 0:
            ratios.append(a_sample.mean() / b_mean)

    if not ratios:
        return {"ratio": 0, "ci_lower": 0, "ci_upper": 0}

    ratios = sorted(ratios)
    lower_idx = int(alpha / 2 * len(ratios))
    upper_idx = int((1 - alpha / 2) * len(ratios))

    return {
        "ratio": round(float(a.mean() / b.mean()), 3),
        "ci_lower": round(ratios[lower_idx], 3),
        "ci_upper": round(ratios[upper_idx], 3),
    }


def analyze_experiment(df: pd.DataFrame, experiment: str) -> dict:
    """Analyze a single experiment's results."""
    exp_df = df[df["experiment"] == experiment]
    exp_clean = filter_no_errors(exp_df)
    exp_pass = filter_pass(exp_df)

    control = exp_clean[exp_clean["condition"] == "control"]
    treatment = exp_clean[exp_clean["condition"] == "treatment"]
    control_pass = exp_pass[exp_pass["condition"] == "control"]
    treatment_pass = exp_pass[exp_pass["condition"] == "treatment"]

    result = {
        "experiment": experiment,
        "runs": {
            "control": int(len(control)),
            "treatment": int(len(treatment)),
        },
        "completion_rate": {
            "control": round(len(control_pass) / max(len(control), 1), 3),
            "treatment": round(len(treatment_pass) / max(len(treatment), 1), 3),
        },
        "total_tokens": {
            "control": compute_stats(control_pass["total_tokens"]),
            "treatment": compute_stats(treatment_pass["total_tokens"]),
        },
        "turns": {
            "control": compute_stats(control_pass["turns"]),
            "treatment": compute_stats(treatment_pass["turns"]),
        },
        "backtracks": {
            "control": compute_stats(control_pass["backtracks"]),
            "treatment": compute_stats(treatment_pass["backtracks"]),
        },
    }

    # Token breakdown for treatment
    if len(treatment_pass) > 0:
        result["treatment_breakdown"] = {
            "tool_tokens": compute_stats(treatment_pass["tool_tokens"]),
            "planning_tokens": compute_stats(treatment_pass["planning_tokens"]),
            "execution_tokens": compute_stats(treatment_pass["execution_tokens"]),
        }

    # Token efficiency ratio with bootstrap CI
    if len(control_pass) > 0 and len(treatment_pass) > 0:
        result["token_efficiency"] = bootstrap_ci(
            control_pass["total_tokens"],
            treatment_pass["total_tokens"],
        )

        # Mann-Whitney U test
        u_stat, p_value = stats.mannwhitneyu(
            control_pass["total_tokens"],
            treatment_pass["total_tokens"],
            alternative="two-sided",
        )
        result["mann_whitney"] = {
            "u_statistic": round(float(u_stat), 1),
            "p_value": round(float(p_value), 4),
            "significant": p_value < 0.05,
        }

    # Completion rate significance (Fisher exact test)
    if len(control) > 0 and len(treatment) > 0:
        table = [
            [len(control_pass), len(control) - len(control_pass)],
            [len(treatment_pass), len(treatment) - len(treatment_pass)],
        ]
        _, fisher_p = stats.fisher_exact(table)
        result["completion_significance"] = {
            "fisher_p": round(float(fisher_p), 4),
            "significant": fisher_p < 0.05,
        }

    # Backtrack rates
    for cond in ["control", "treatment"]:
        cond_pass = control_pass if cond == "control" else treatment_pass
        if len(cond_pass) > 0:
            total_turns = cond_pass["turns"].sum()
            total_backtracks = cond_pass["backtracks"].sum()
            if total_turns > 0:
                result[f"backtrack_rate_{cond}"] = round(float(total_backtracks / total_turns), 3)

    # Entropy correlation
    if "knowledge_entropy" in exp_pass.columns:
        entropy_data = exp_pass[exp_pass["knowledge_entropy"].notna() & (exp_pass["knowledge_entropy"] != "")].copy()
        if len(entropy_data) >= 3:
            entropy_vals = pd.to_numeric(entropy_data["knowledge_entropy"], errors="coerce").dropna()
            token_vals = entropy_data.loc[entropy_vals.index, "total_tokens"]
            if len(entropy_vals) >= 3:
                from scipy.stats import spearmanr

                corr, p_val = spearmanr(entropy_vals, token_vals)
                result["entropy_correlation"] = {
                    "spearman_r": round(float(corr), 3),
                    "p_value": round(float(p_val), 4),
                    "n": int(len(entropy_vals)),
                }

    # Variance comparison (CV)
    if len(control_pass) > 1 and len(treatment_pass) > 1:
        ctrl_cv = control_pass["total_tokens"].std() / control_pass["total_tokens"].mean()
        treat_cv = treatment_pass["total_tokens"].std() / treatment_pass["total_tokens"].mean()
        result["variance"] = {
            "control_cv": round(float(ctrl_cv), 3),
            "treatment_cv": round(float(treat_cv), 3),
            "variance_reduction": (round(float(1 - treat_cv / ctrl_cv), 3) if ctrl_cv > 0 else 0),
        }

    # Warnings
    for cond in ["control", "treatment"]:
        n = result["runs"][cond]
        if n < 5:
            result.setdefault("warnings", []).append(f"Insufficient runs for {cond}: {n} < 5")

    return result


def print_report(results: list[dict]):
    """Print human-readable analysis report."""
    for r in results:
        print(f"{'=' * 60}")
        print(f"Experiment: {r['experiment']}")
        print(f"{'=' * 60}")
        print()

        print(f"  Runs:            control={r['runs']['control']}, treatment={r['runs']['treatment']}")
        print(
            f"  Completion rate: control={r['completion_rate']['control']:.0%},"
            f" treatment={r['completion_rate']['treatment']:.0%}"
        )

        if "completion_significance" in r:
            cs = r["completion_significance"]
            print(f"    Fisher exact p={cs['fisher_p']:.4f} (significant: {'YES' if cs['significant'] else 'NO'})")
        print()

        c = r["total_tokens"]["control"]
        t = r["total_tokens"]["treatment"]
        print("  Total tokens (PASS only):")
        print(f"    Control:   mean={c['mean']:.0f}  std={c['std']:.0f}  n={c['n']}")
        print(f"    Treatment: mean={t['mean']:.0f}  std={t['std']:.0f}  n={t['n']}")
        print()

        if "token_efficiency" in r:
            te = r["token_efficiency"]
            direction = "saves tokens" if te["ratio"] > 1.0 else "adds overhead"
            print(f"  Token efficiency ratio: {te['ratio']:.3f} ({direction})")
            print(f"    95% CI: [{te['ci_lower']:.3f}, {te['ci_upper']:.3f}]")
            print()

        if "mann_whitney" in r:
            mw = r["mann_whitney"]
            print(f"  Mann-Whitney U: U={mw['u_statistic']:.0f}, p={mw['p_value']:.4f}")
            print()

        if "variance" in r:
            v = r["variance"]
            print(f"  Variance (CV): control={v['control_cv']:.3f}, treatment={v['treatment_cv']:.3f}")
            print(f"    Variance reduction: {v['variance_reduction']:.0%}")
            print()

        if "treatment_breakdown" in r:
            tb = r["treatment_breakdown"]
            print("  Treatment token breakdown:")
            print(f"    Intent tools:     mean={tb['tool_tokens']['mean']:.0f}")
            print(f"    Planning tokens:  mean={tb['planning_tokens']['mean']:.0f}")
            print(f"    Execution tokens: mean={tb['execution_tokens']['mean']:.0f}")
            print()

        if "warnings" in r:
            for w in r["warnings"]:
                print(f"  WARNING: {w}")
            print()


def compute_input_hash(ledger_path: str) -> str:
    h = hashlib.sha256()
    h.update(Path(ledger_path).read_bytes())
    h.update(Path(__file__).read_bytes())
    return h.hexdigest()


def check_cache(output_path: Path, input_hash: str) -> bool:
    if not output_path.exists():
        return False
    try:
        cached = json.loads(output_path.read_text())
        if isinstance(cached, dict) and "meta" in cached:
            return cached["meta"].get("input_hash") == input_hash
    except (json.JSONDecodeError, KeyError):
        pass
    return False


def main():
    force = "--force" in sys.argv
    all_versions = "--all-versions" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ledger_path = args[0] if args else "results/summary.csv"

    if not Path(ledger_path).exists():
        print(f"ERROR: Ledger not found: {ledger_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(ledger_path).parent / "analysis.json"

    input_hash = compute_input_hash(ledger_path)
    if not force and check_cache(output_path, input_hash):
        print("Analysis unchanged, skipping.")
        sys.exit(0)

    sv = "all" if all_versions else None
    df = load_ledger(ledger_path, score_version=sv)

    if len(df) == 0:
        print("No experiment data to analyze.")
        sys.exit(0)

    experiments = df["experiment"].unique()
    results = [analyze_experiment(df, exp) for exp in experiments]

    print_report(results)

    score_versions = sorted(df["score_version"].unique().tolist()) if "score_version" in df.columns else []
    output = {
        "meta": {
            "input_hash": input_hash,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "ledger": ledger_path,
            "score_versions": score_versions,
        },
        "experiments": results,
    }
    output_path.write_text(json.dumps(output, indent=2, default=str))
    print(f"Analysis written to {output_path}")


if __name__ == "__main__":
    main()
