"""蒲丰投针实验：真实取样、相交判断与圆周率估计。

本模块可被 import；import 时不启动实验、不写文件。
直接运行（``uv run --locked python experiment.py``）时，
按默认参数对 n=1000/10000/100000，seed=42 各做一次独立实验，
并把真实参数与结果写入当前工作目录的 results.csv。
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from typing import Sequence

# CSV 表头顺序，同时也是 simulate() 返回字典的字段顺序。
FIELDS = (
    "seed", "n", "crossings", "pi_estimate", "needle_length", "line_spacing"
)
DEFAULT_SIZES = (1000, 10000, 100000)
DEFAULT_SEED = 42
DEFAULT_LENGTH = 0.5
DEFAULT_SPACING = 1.0


def _check_geometry(length: float, spacing: float) -> None:
    """校验几何参数；不合法时抛 ValueError，不静默改参数。"""
    if spacing <= 0:
        raise ValueError(f"spacing 必须为正数，收到 {spacing!r}")
    if length <= 0:
        raise ValueError(f"length 必须为正数，收到 {length!r}")
    if length > spacing:
        raise ValueError(f"要求 0 < length <= spacing，收到 length={length!r}, spacing={spacing!r}")


def crosses_line(distance: float, angle: float, length: float = 0.5, spacing: float = 1.0) -> bool:
    """判断一根针是否与平行线相交（接触也算相交）。

    输入范围：``0 <= distance <= spacing/2``，``0 <= angle <= pi/2``。
    相交判据：``distance <= (length/2) * sin(angle)``。
    几何参数越界或非法时抛 ValueError，不静默改参数。
    """
    _check_geometry(length, spacing)
    if not 0 <= distance <= spacing / 2:
        raise ValueError(f"要求 0 <= distance <= spacing/2 = {spacing / 2!r}，收到 {distance!r}")
    if not 0 <= angle <= math.pi / 2:
        raise ValueError(f"要求 0 <= angle <= pi/2，收到 {angle!r}")
    return distance <= (length / 2) * math.sin(angle)


def estimate_pi(n: int, crossings: int, length: float = 0.5, spacing: float = 1.0) -> float:
    """由投针数 n 与相交数 crossings 估计圆周率：``2*length*n/(spacing*crossings)``。

    n 为正整数；crossings 为整数且 ``0 <= crossings <= n``。
    crossings=0 时无法估计，抛 ValueError。
    """
    _check_geometry(length, spacing)
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError(f"n 必须为正整数，收到 {n!r}")
    if not isinstance(crossings, int) or isinstance(crossings, bool) or not 0 <= crossings <= n:
        raise ValueError(f"crossings 必须为整数且 0 <= crossings <= n={n}，收到 {crossings!r}")
    if crossings == 0:
        raise ValueError("crossings=0 时无法用 2*length*n/(spacing*crossings) 估计圆周率")
    return 2 * length * n / (spacing * crossings)


def simulate(n: int, seed: int = 42, length: float = 0.5, spacing: float = 1.0) -> dict:
    """做 n 次独立投针，返回本次实验的真实参数与结果。

    随机数生成器在取样循环外只用 seed 初始化一次；
    循环内持续取样，不会在每次投针时重设 seed。
    distance ~ U[0, spacing/2] 与 angle ~ U[0, pi/2] 相互独立。
    """
    _check_geometry(length, spacing)
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError(f"n 必须为正整数，收到 {n!r}")

    rng = random.Random(seed)  # 循环外只初始化一次
    crossings = 0
    half_spacing = spacing / 2
    half_pi = math.pi / 2
    for _ in range(n):
        distance = rng.uniform(0.0, half_spacing)
        angle = rng.uniform(0.0, half_pi)
        if crosses_line(distance, angle, length=length, spacing=spacing):
            crossings += 1

    if crossings == 0:
        raise ValueError(
            f"本次模拟 n={n} 没有一次相交，无法估计圆周率；请增大 n 或更换 seed。"
        )

    return {
        "seed": seed,
        "n": n,
        "crossings": crossings,
        "pi_estimate": estimate_pi(n, crossings, length=length, spacing=spacing),
        "needle_length": length,
        "line_spacing": spacing,
    }


def run_experiment(
    sizes: Sequence[int] = DEFAULT_SIZES,
    seed: int = DEFAULT_SEED,
    length: float = DEFAULT_LENGTH,
    spacing: float = DEFAULT_SPACING,
    output: str = "results.csv",
) -> list[dict]:
    """对每个 n 做一次独立实验（各自只初始化一次 seed），写入 CSV 并返回结果。"""
    rows: list[dict] = []
    for n in sizes:
        result = simulate(n, seed=seed, length=length, spacing=spacing)
        rows.append(result)
        print(
            f"n={result['n']:>7}  相交={result['crossings']:>7}  "
            f"估计 pi={result['pi_estimate']:.6f}"
        )

    with open(output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDS))
        writer.writeheader()
        writer.writerows(rows)
    print(f"已写入 {output}（{len(rows)} 行）")
    return rows


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="蒲丰投针：估计圆周率并写出 results.csv")
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED, help=f"随机种子（默认 {DEFAULT_SEED}）"
    )
    parser.add_argument(
        "--n", type=int, action="append", dest="sizes",
        help="投针数，可重复指定；默认 1000 10000 100000",
    )
    parser.add_argument("--length", type=float, default=DEFAULT_LENGTH, help="针长（默认 0.5）")
    parser.add_argument("--spacing", type=float, default=DEFAULT_SPACING, help="平行线间距（默认 1.0）")
    parser.add_argument("--output", default="results.csv", help="输出 CSV 路径（默认 results.csv）")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    sizes = tuple(args.sizes) if args.sizes else DEFAULT_SIZES
    run_experiment(
        sizes=sizes,
        seed=args.seed,
        length=args.length,
        spacing=args.spacing,
        output=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
