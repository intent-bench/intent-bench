#!/usr/bin/env python3
"""Visualization generation for intent-bench experiments.

Publication-quality charts generated from experiment results.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import numpy as np  # noqa: E402

from style import COLORS, DPI, apply_style  # noqa: E402


def load_data(ledger_path: str = "results/summary.csv") -> pd.DataFrame:
    return pd.read_csv(ledger_path)


def chart_token_comparison(df: pd.DataFrame, output_dir: Path):
    """Bar chart: mean total_tokens per condition per experiment with CI."""
    pass_df = df[df["outcome"] == "PASS"]
    experiments = pass_df["experiment"].unique()

    if len(experiments) == 0:
        print("  [SKIP] token_comparison -- no PASS data")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(experiments))
    width = 0.35

    for i, condition in enumerate(["control", "treatment"]):
        means = []
        cis = []
        for exp in experiments:
            data = pass_df[(pass_df["experiment"] == exp) & (pass_df["condition"] == condition)]
            means.append(data["total_tokens"].mean() if len(data) > 0 else 0)
            cis.append(data["total_tokens"].std() * 1.96 / max(np.sqrt(len(data)), 1) if len(data) > 1 else 0)

        color = COLORS[condition]
        offset = -width / 2 + i * width
        ax.bar(
            x + offset,
            means,
            width,
            yerr=cis,
            label=condition.capitalize(),
            color=color,
            capsize=4,
            alpha=0.85,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(experiments, rotation=15)
    apply_style(
        ax,
        "Token Consumption: Control vs Treatment",
        "Experiment",
        "Total Tokens (PASS only)",
    )
    ax.legend()
    fig.tight_layout()

    for fmt in ["png", "svg"]:
        fig.savefig(output_dir / f"token_comparison.{fmt}", dpi=DPI)
    plt.close(fig)
    print("  [OK] token_comparison")


def chart_token_breakdown(df: pd.DataFrame, output_dir: Path):
    """Stacked bar: planning vs execution vs intent tool tokens per condition."""
    pass_df = df[df["outcome"] == "PASS"]
    experiments = pass_df["experiment"].unique()

    if len(experiments) == 0:
        print("  [SKIP] token_breakdown -- no PASS data")
        return

    fig, axes = plt.subplots(1, len(experiments), figsize=(6 * len(experiments), 5), squeeze=False)

    for idx, exp in enumerate(experiments):
        ax = axes[0, idx]
        for i, condition in enumerate(["control", "treatment"]):
            data = pass_df[(pass_df["experiment"] == exp) & (pass_df["condition"] == condition)]
            if len(data) == 0:
                continue

            planning = data["planning_tokens"].mean()
            execution = data["execution_tokens"].mean()
            tool = data["tool_tokens"].mean()

            bottom = 0
            for val, label, color in [
                (tool, "Intent Tools", COLORS["intent"]),
                (planning - tool, "Planning", COLORS["planning"]),
                (execution, "Execution", COLORS["execution"]),
            ]:
                if val > 0:
                    ax.bar(
                        condition.capitalize(),
                        val,
                        bottom=bottom,
                        label=label if i == 0 else "",
                        color=color,
                        alpha=0.85,
                    )
                    bottom += val

        apply_style(ax, f"Token Breakdown: {exp}", "", "Tokens")
        if idx == 0:
            ax.legend()

    fig.tight_layout()
    for fmt in ["png", "svg"]:
        fig.savefig(output_dir / f"token_breakdown.{fmt}", dpi=DPI)
    plt.close(fig)
    print("  [OK] token_breakdown")


def chart_completion_rate(df: pd.DataFrame, output_dir: Path):
    """Bar chart: PASS rates per condition per experiment."""
    no_error = df[df["outcome"] != "ERROR"]
    experiments = no_error["experiment"].unique()

    if len(experiments) == 0:
        print("  [SKIP] completion_rate -- no data")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(experiments))
    width = 0.35

    for i, condition in enumerate(["control", "treatment"]):
        rates = []
        for exp in experiments:
            data = no_error[(no_error["experiment"] == exp) & (no_error["condition"] == condition)]
            if len(data) == 0:
                rates.append(0)
            else:
                rates.append((data["outcome"] == "PASS").mean())

        color = COLORS[condition]
        offset = -width / 2 + i * width
        ax.bar(
            x + offset,
            [r * 100 for r in rates],
            width,
            label=condition.capitalize(),
            color=color,
            alpha=0.85,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(experiments, rotation=15)
    ax.set_ylim(0, 110)
    apply_style(ax, "Task Completion Rate", "Experiment", "Completion Rate (%)")
    ax.legend()
    fig.tight_layout()

    for fmt in ["png", "svg"]:
        fig.savefig(output_dir / f"completion_rate.{fmt}", dpi=DPI)
    plt.close(fig)
    print("  [OK] completion_rate")


def chart_entropy_variance(df: pd.DataFrame, output_dir: Path):
    """Box plot: entropy distribution per condition, showing variance reduction."""
    ent_df = df[df["knowledge_entropy"].notna() & (df["knowledge_entropy"] != "")].copy()
    ent_df["knowledge_entropy"] = pd.to_numeric(ent_df["knowledge_entropy"], errors="coerce")
    ent_df = ent_df.dropna(subset=["knowledge_entropy"])

    if len(ent_df) < 4:
        print("  [SKIP] entropy_variance -- insufficient data")
        return

    experiments = sorted(ent_df["experiment"].unique())
    fig, axes = plt.subplots(1, len(experiments), figsize=(5 * len(experiments), 5), squeeze=False)

    for i, exp in enumerate(experiments):
        ax = axes[0][i]
        exp_df = ent_df[ent_df["experiment"] == exp]

        ctrl_vals = exp_df[exp_df["condition"] == "control"]["knowledge_entropy"].values
        treat_vals = exp_df[exp_df["condition"] == "treatment"]["knowledge_entropy"].values

        bp = ax.boxplot(
            [ctrl_vals, treat_vals],
            tick_labels=["Control", "Treatment"],
            patch_artist=True,
            widths=0.5,
        )

        bp["boxes"][0].set_facecolor(COLORS["control"])
        bp["boxes"][0].set_alpha(0.7)
        bp["boxes"][1].set_facecolor(COLORS["treatment"])
        bp["boxes"][1].set_alpha(0.7)

        for j, (vals, color) in enumerate([(ctrl_vals, COLORS["control"]), (treat_vals, COLORS["treatment"])]):
            x_jitter = np.random.normal(j + 1, 0.04, size=len(vals))
            ax.scatter(
                x_jitter,
                vals,
                color=color,
                alpha=0.6,
                s=40,
                edgecolors="black",
                linewidths=0.5,
                zorder=3,
            )

        for j, vals in enumerate([ctrl_vals, treat_vals]):
            if len(vals) > 1 and np.mean(vals) > 0:
                cv = np.std(vals, ddof=1) / np.mean(vals)
                ax.text(
                    j + 1,
                    ax.get_ylim()[1] * 0.95,
                    f"CV={cv:.2f}",
                    ha="center",
                    fontsize=9,
                    style="italic",
                )

        ax.set_title(exp, fontsize=12, fontweight="bold")
        ax.set_ylabel("Knowledge Entropy Score")
        ax.set_ylim(0, max(ent_df["knowledge_entropy"].max() * 1.2, 6))

    fig.suptitle(
        "Entropy Variance: Intent Layer Reduces Outcome Variability",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()

    for fmt in ["png", "svg"]:
        fig.savefig(output_dir / f"entropy_variance.{fmt}", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] entropy_variance")


def chart_tool_distribution(df: pd.DataFrame, output_dir: Path):
    """Bar chart: intent tool call counts for treatment condition."""
    treatment = df[(df["condition"] == "treatment") & (df["outcome"] == "PASS")]

    if len(treatment) == 0 or treatment["tool_calls_intent"].sum() == 0:
        print("  [SKIP] tool_distribution -- no intent tool data")
        return

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        ["Intent Tools", "Other Tools"],
        [treatment["tool_calls_intent"].mean(), treatment["tool_calls_other"].mean()],
        color=[COLORS["intent"], COLORS["neutral"]],
        alpha=0.85,
    )

    apply_style(ax, "Tool Call Distribution (Treatment)", "", "Mean Tool Calls per Session")
    fig.tight_layout()

    for fmt in ["png", "svg"]:
        fig.savefig(output_dir / f"tool_distribution.{fmt}", dpi=DPI)
    plt.close(fig)
    print("  [OK] tool_distribution")


def charts_up_to_date(ledger_path: str, output_dir: Path) -> bool:
    """Check if charts are newer than inputs."""
    ledger = Path(ledger_path)
    analysis = ledger.parent / "analysis.json"
    if not ledger.exists():
        return False

    chart_files = list(output_dir.glob("*.png")) + list(output_dir.glob("*.svg"))
    if not chart_files:
        return False

    oldest_chart = min(f.stat().st_mtime for f in chart_files)
    newest_input = ledger.stat().st_mtime
    if analysis.exists():
        newest_input = max(newest_input, analysis.stat().st_mtime)

    return oldest_chart > newest_input


def main():
    force = "--force" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--force"]
    ledger_path = args[0] if args else "results/summary.csv"

    if not Path(ledger_path).exists():
        print(f"ERROR: Ledger not found: {ledger_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path("results/charts")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not force and charts_up_to_date(ledger_path, output_dir):
        print("Charts up to date, skipping.")
        sys.exit(0)

    df = load_data(ledger_path)
    if len(df) == 0:
        print("No data to visualize.")
        sys.exit(0)

    print("Generating charts...")
    chart_token_comparison(df, output_dir)
    chart_token_breakdown(df, output_dir)
    chart_completion_rate(df, output_dir)
    chart_entropy_variance(df, output_dir)
    chart_tool_distribution(df, output_dir)
    print(f"Charts written to {output_dir}/")


if __name__ == "__main__":
    main()
