#!/usr/bin/env python3
import argparse
from math import log
from typing import Generator

from matplotlib import pyplot as plt
import numpy as np


def get_upper_limit(n: int) -> int:
    """Get the approximate upper limit of the `n`th prime number"""
    if n < 6:
        return 15
    return int(n * (log(n) + log(log(n)))) + 1


def get_primes(n: int) -> Generator[int]:
    """
    Get at least `n` prime numbers. Will return more than `n` numbers due to
    approximating the upper limit of the `n`th prime number. You can truncate the list
    by doing something like this:
    ```python
    n = 10000
    list(get_primes(n))[:n]
    ```
    """
    limit = get_upper_limit(n)
    is_prime = np.ones(limit, dtype=np.bool)
    is_prime[:2] = np.bool(False)
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            is_prime[i * i :: i] = np.bool(False)
    return (i for i, b in enumerate(is_prime) if b)


def plot_primes(n: int, colormap: str) -> None:
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.scatter(
        list(get_primes(n))[:n], np.arange(n), s=0.5, c=np.arange(n), cmap=colormap
    )
    ax.set_axis_off()

    fig.set_facecolor("black")
    fig.set_size_inches(11, 6)

    plt.show()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Plot prime numbers in a polar coordinate system"
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        metavar="int",
        default=1000,
        help="number of primes to plot (default 1000)",
    )
    parser.add_argument(
        "-c",
        "--colormap",
        type=str,
        metavar="str",
        default="twilight",
        help='name of colormap to use for plot (default "twilight")',
    )
    args = parser.parse_args(argv)
    plot_primes(args.number, args.colormap)


if __name__ == "__main__":
    main()
