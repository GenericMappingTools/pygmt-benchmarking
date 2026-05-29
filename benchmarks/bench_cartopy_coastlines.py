"""
Benchmark PyGMT and cartopy when plotting simple global coastlines.
"""

import statistics
import time
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pygmt

import matplotlib.pyplot as plt  # noqa: E402


BACKENDS = ("cartopy", "pygmt")
OUTPUT_DIR = Path("plots/coastlines")
REPEATS = 10
RESOLUTION = "low"
CARTOPY_RESOLUTIONS = {
    "low": "110m",
    "medium": "50m",
    "high": "10m",
}
PYGMT_RESOLUTIONS = {
    "low": "c",
    "medium": "l",
    "high": "i",
}
LAND_COLOR = "#cccccc"
WATER_COLOR = "#b9d9ea"


def plot_cartopy(resolution: str):
    """Create a simple global coastline plot with cartopy."""
    fig = plt.figure(figsize=(6, 4), dpi=300)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
    ax.set_global()
    ax.add_feature(cfeature.LAND, facecolor=LAND_COLOR)
    ax.add_feature(cfeature.OCEAN, facecolor=WATER_COLOR)
    ax.coastlines(
        resolution=CARTOPY_RESOLUTIONS[resolution],
        linewidth=0.5,
    )
    ax.gridlines(color="0.8", linewidth=0.4)
    return fig


def save_cartopy(fig, output: Path) -> None:
    """Save a cartopy/matplotlib figure and release it."""
    fig.savefig(output)
    plt.close(fig)


def plot_pygmt(resolution: str) -> pygmt.Figure:
    """Create a simple global coastline plot with PyGMT."""
    fig = pygmt.Figure()
    fig.coast(
        region="g",
        projection="R15c",
        resolution=PYGMT_RESOLUTIONS[resolution],
        land=LAND_COLOR,
        water=WATER_COLOR,
        shorelines="1/0.5p,black",
        frame="afg",
    )
    return fig


def save_pygmt(fig: pygmt.Figure, output: Path) -> None:
    """Save a PyGMT figure."""
    fig.savefig(output)


def benchmark(
    name: str,
    plot_func,
    save_func,
    output_dir: Path,
    repeats: int,
    resolution: str,
) -> tuple[list[float], list[float]]:
    """Time repeated coastline plot creation and figure export runs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Warm up each backend once before recording timings.
    fig = plot_func(resolution)
    save_func(fig, output_dir / f"{name}_warmup.png")

    plot_timings = []
    save_timings = []
    for run_id in range(repeats):
        output = output_dir / f"{name}_{run_id + 1}.png"

        start = time.perf_counter()
        fig = plot_func(resolution)
        plot_timings.append(time.perf_counter() - start)

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
    """Run the coastline plotting benchmark."""
    plotters = {
        "cartopy": plot_cartopy,
        "pygmt": plot_pygmt,
    }
    savers = {
        "cartopy": save_cartopy,
        "pygmt": save_pygmt,
    }

    print(f"Running {REPEATS} timed run(s) per backend")
    print(f"Using {RESOLUTION} coastline resolution")
    print(f"Writing PNG files to {OUTPUT_DIR}")
    for backend in BACKENDS:
        print(f"Benchmarking {backend}...", flush=True)
        plot_timings, save_timings = benchmark(
            name=f"{backend}_{RESOLUTION}",
            plot_func=plotters[backend],
            save_func=savers[backend],
            output_dir=OUTPUT_DIR,
            repeats=REPEATS,
            resolution=RESOLUTION,
        )
        print(format_summary(f"{backend} plot", plot_timings))
        print(format_summary(f"{backend} savefig", save_timings))


if __name__ == "__main__":
    main()
