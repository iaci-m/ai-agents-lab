"""由真实的 results.csv 生成报告所需文件。

读取当前工作目录的 results.csv（不在这一步重新投针、不编造结果），
生成：
- results-table.tex  ：可直接 input 的 LaTeX 表格（n、crossings、pi_estimate）。
- results.png        ：不同 n 对应估计值的静态图，含真实 pi 参考线。
- results-params.tex ：可直接 input 的短文字，显示实际 seed、各组 n、针长与线间距。

直接运行：``uv run --locked python render_results.py``
输出写入当前工作目录。图坐标轴使用英文，避免图像中文字体成为额外安装任务。
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # 无显示环境下也能出图

import matplotlib.pyplot as plt  # noqa: E402  (需先设置后端)

CSV_PATH = Path("results.csv")
TABLE_PATH = Path("results-table.tex")
PARAMS_PATH = Path("results-params.tex")
FIGURE_PATH = Path("results.png")


def load_rows(csv_path: Path = CSV_PATH) -> list[dict]:
    """读取 results.csv，返回按 n 升序排列的行。"""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"找不到 {csv_path}。请先运行 `uv run --locked python experiment.py` 生成真实结果。"
        )
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{csv_path} 没有数据行，无法生成图表与参数。")
    for row in rows:
        row["n"] = int(row["n"])
        row["seed"] = int(row["seed"])
        row["crossings"] = int(row["crossings"])
        row["pi_estimate"] = float(row["pi_estimate"])
        row["needle_length"] = float(row["needle_length"])
        row["line_spacing"] = float(row["line_spacing"])
    rows.sort(key=lambda r: r["n"])
    return rows


def write_table(rows: Sequence[dict], path: Path = TABLE_PATH) -> None:
    """写出可直接 input 的 LaTeX 表格（放在 report.tex 的 center 环境内）。"""
    lines = [
        "% 本文件由 render_results.py 依据 results.csv 自动生成，请勿手改。",
        r"\begin{tabular}{rrr}",
        r"\toprule",
        r"投针数 $n$ & 相交数 $K$ & 估计值 $\widehat{\pi}$ \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['n']} & {row['crossings']} & {row['pi_estimate']:.6f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt_number(value: float) -> str:
    """整数值显示成 1.0 这样，避免丢了小数位；非整数用紧凑表示。"""
    if value == int(value):
        return f"{value:.1f}"
    return f"{value:g}"


def write_params(rows: Sequence[dict], path: Path = PARAMS_PATH) -> None:
    """写出可直接 input 的短文字，显示 CSV 中的实际 seed、n、针长与线间距。"""
    seeds = sorted({row["seed"] for row in rows})
    seed_text = "、".join(f"${s}$" for s in seeds)
    ns = [row["n"] for row in rows]
    # 数字留在文本模式，中文顿号也留在文本模式，避免 CJK 标点进入公式。
    n_text = "、".join(f"{n}" for n in ns)
    length_text = _fmt_number(rows[0]["needle_length"])
    spacing_text = _fmt_number(rows[0]["line_spacing"])

    text = (
        f"本次实验使用随机种子 seed = {seed_text}，"
        f"投针数分别为 $n =$ {n_text}；"
        f"针长 $L = {length_text}$，平行线间距 $d = {spacing_text}$。\n"
    )
    path.write_text(text, encoding="utf-8")


def write_figure(rows: Sequence[dict], path: Path = FIGURE_PATH) -> None:
    """绘制估计值随 n 变化的折线图，并画出真实 pi 参考线（英文坐标轴）。"""
    ns = [row["n"] for row in rows]
    estimates = [row["pi_estimate"] for row in rows]

    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=150)
    ax.axhline(math.pi, color="crimson", linestyle="--", linewidth=1.2,
               label=f"true $\\pi \\approx {math.pi:.4f}$")
    ax.plot(ns, estimates, marker="o", color="tab:blue", label="estimate from simulation")
    for n, est in zip(ns, estimates):
        ax.annotate(f"{est:.4f}", (n, est), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8)

    ax.set_xscale("log")
    ax.set_xlabel("number of needles  n  (log scale)")
    ax.set_ylabel(r"estimated $\hat{\pi}$")
    ax.set_title("Buffon's needle: pi estimate vs. n")
    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> int:
    rows = load_rows()
    write_table(rows)
    write_params(rows)
    write_figure(rows)
    print(f"已由 {CSV_PATH} 生成 {TABLE_PATH}、{PARAMS_PATH}、{FIGURE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
