# plot-primes

It plots primes in a polar coordinate system. Looks real nice for wallpapers and
such.

## Run it

### Directly

- Download
[`plotprimes.py`](src/plotprimes/plotprimes.py)
and run it with Python. This script requires
[`matplotlib`](https://pypi.org/project/matplotlib/).
- OR: Install from [PyPi](https://pypi.org/project/plotprimes)
using whatever people use to install Python packages nowadays.
- OR: Install a wheel from the
[releases](https://github.com/jtompkin/plot-primes/releases) page.

### Nix

The flake exposes `plotprimes` as the default package:

```bash
nix run 'github:jtompkin/plot-primes' -- -h
```

If you're feeling spicy, you can download the
[`nix/plotprimes.py`](nix/plotprimes.py)
script and run it directly. This is a reproducible interpreted script: all you
need is Nix; it will run in an environment with all dependencies satisfied
automagically.

## Use it

### Flags

- `-n`: `int` Number of primes to plot. (default 1000)
- `-c`: `str` [Matplotlib colormap](https://matplotlib.org/stable/users/explain/colors/colormaps.html)
name. (default "twilight")

## Build it

Requires Python and [`build`](https://pypi.org/project/build/).

```bash
git clone https://github.com/jtompkin/plot-primes
cd plot-primes
python -m build
```
