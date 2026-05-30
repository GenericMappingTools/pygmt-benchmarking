"""
Benchmark PyGMT and matplotlib when plotting a Cartesian 2-D xarray DataArray.
"""

import statistics
import time
from pathlib import Path

import numpy as np
import pygmt
import xarray as xr
from pygmt.params import Axis, Frame, Position

import matplotlib.pyplot as plt  # noqa: E402


OUTPUT_DIR = Path("plots/xarray")
REPEATS = 10
INCS = (0.05, 0.01, 0.005)
REGION = [-5, 5, -5, 5]
CMAP = "turbo"


def ackley(x, y):
    """Ackley function."""
    return (
        -20 * np.exp(-0.2 * np.sqrt(0.5 * (x**2 + y**2)))
        - np.exp(0.5 * (np.cos(2 * np.pi * x) + np.cos(2 * np.pi * y)))
        + np.exp(1)
        + 20
    )


def create_dataarray(inc: float) -> xr.DataArray:
    """Create a Cartesian 2-D DataArray using the Ackley function."""
    x = np.arange(REGION[0], REGION[1] + inc, inc)
    y = np.arange(REGION[2], REGION[3] + inc, inc)
    xx, yy = np.meshgrid(x, y)
    return xr.DataArray(
        ackley(xx, yy),
        coords={"y": y, "x": x},
        dims=("y", "x"),
        name="ackley",
    )


def plot_matplotlib(data: xr.DataArray):
    """Create a Cartesian 2-D image plot with matplotlib."""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300)
    image = ax.imshow(
        data.values,
        origin="lower",
        extent=[REGION[0], REGION[1], REGION[2], REGION[3]],
        cmap=CMAP,
    )
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Ackley function")
    return fig


def save_matplotlib(fig, output: Path) -> None:
    """Save a matplotlib figure and release it."""
    fig.savefig(output)
    plt.close(fig)


def plot_pygmt(data: xr.DataArray) -> pygmt.Figure:
    """Create a Cartesian 2-D image plot with PyGMT."""
    fig = pygmt.Figure()
    fig.grdimage(
        grid=data,
        region=REGION,
        projection="X6i/6i",
        cmap=CMAP,
        frame=Frame(
            axes="WSne",
            title="Ackley function",
            xaxis=Axis(annot=True, tick=True, label="x"),
            yaxis=Axis(annot=True, tick=True, label="y"),
        ),
    )
    return fig


def save_pygmt(fig: pygmt.Figure, output: Path) -> None:
    """Save a PyGMT figure."""
    fig.savefig(output)


def benchmark(
    name: str,
    plot_func,
    save_func,
    data: xr.DataArray,
    output_dir: Path,
    repeats: int,
) -> tuple[list[float], list[float]]:
    """Time repeated xarray plot creation and figure export runs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Warm up each backend once before recording timings.
    fig = plot_func(data)
    save_func(fig, output_dir / f"{name}_warmup.png")

    plot_timings = []
    save_timings = []
    for run_id in range(repeats):
        output = output_dir / f"{name}_{run_id + 1}.pdf"

        start = time.perf_counter()
        fig = plot_func(data)
        plot_timings.append(time.perf_counter() - start)

        start = time.perf_counter()
        save_func(fig, output)
        save_timings.append(time.perf_counter() - start)

    return plot_timings, save_timings


def format_summary(name: str, timings: list[float]) -> str:
    """Format benchmark timing statistics."""
    mean = statistics.fmean(timings)
    median = statistics.median(timings)
    minimum = min(timings)
    maximum = max(timings)
    return (
        f"{name:10s} "
        f"mean={mean:.4f}s "
        f"median={median:.4f}s "
        f"min={minimum:.4f}s "
        f"max={maximum:.4f}s"
    )


def main() -> None:
    """Run the Cartesian xarray plotting benchmark."""
    print(f"Running {REPEATS} timed run(s) per backend")
    print(f"Writing PNG files to {OUTPUT_DIR}")

    for inc in INCS:
        data = create_dataarray(inc)
        inc_label = f"inc_{inc:g}".replace(".", "p")
        print(f"Grid increment: {inc:g}")

        print("Benchmarking matplotlib...", flush=True)
        plot_timings, save_timings = benchmark(
            name=f"matplotlib_{inc_label}",
            plot_func=plot_matplotlib,
            save_func=save_matplotlib,
            data=data,
            output_dir=OUTPUT_DIR,
            repeats=REPEATS,
        )
        print(format_summary("matplotlib plot", plot_timings))
        print(format_summary("matplotlib savefig", save_timings))

        print("Benchmarking pygmt...", flush=True)
        plot_timings, save_timings = benchmark(
            name=f"pygmt_{inc_label}",
            plot_func=plot_pygmt,
            save_func=save_pygmt,
            data=data,
            output_dir=OUTPUT_DIR,
            repeats=REPEATS,
        )
        print(format_summary("pygmt plot", plot_timings))
        print(format_summary("pygmt savefig", save_timings))


if __name__ == "__main__":
    main()
