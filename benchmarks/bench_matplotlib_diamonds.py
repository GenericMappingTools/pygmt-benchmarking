"""
Benchmark PyGMT and matplotlib when plotting the diamonds dataset.
"""

import statistics
import time
from pathlib import Path

import pandas as pd
import pygmt
import matplotlib.pyplot as plt  # noqa: E402


COLORS = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd")
BACKENDS = ("matplotlib", "pygmt")
OUTPUT_DIR = Path("plots/diamonds")
REPEATS = 10
DIAMONDS_DATA_URL = (
    "https://github.com/mwaskom/seaborn-data/raw/master/diamonds.csv"
)
CUT_ORDER = ("Fair", "Good", "Very Good", "Premium", "Ideal")

# Matplotlib interprets scatter ``s`` as marker area in points squared, while PyGMT's
# circle style uses marker diameter. Keep one diameter-like value here and convert
# it for matplotlib inside ``plot_matplotlib``.
MARKER_SIZE_POINTS = 2


def load_diamonds_data() -> pd.DataFrame:
    """Load the diamonds dataset from seaborn's example-data repository."""
    return pd.read_csv(DIAMONDS_DATA_URL)


def plot_matplotlib(data: pd.DataFrame):
    """Create the diamonds scatter plot with matplotlib."""
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

    for cut_id, cut_name in enumerate(CUT_ORDER):
        cut_data = data[data["cut"] == cut_name]
        ax.scatter(
            cut_data["carat"],
            cut_data["price"],
            label=cut_name,
            s=MARKER_SIZE_POINTS**2,
            marker="o",
            color=COLORS[cut_id],
            alpha=0.5,
            linewidths=0,
        )
    ax.set_xlabel("Carat")
    ax.set_ylabel("Price (USD)")
    ax.set_title("Diamond price by carat")
    ax.legend(title="Cut", frameon=False, markerscale=4)
    return fig


def save_matplotlib(fig, output: Path) -> None:
    """Save a matplotlib figure and release it."""
    fig.savefig(output)
    plt.close(fig)


def plot_pygmt(data: pd.DataFrame) -> pygmt.Figure:
    """Create the diamonds scatter plot with PyGMT.
    """
    fig = pygmt.Figure()
    fig.basemap(
        region=[0, 5.5, 0, 20000],
        projection="X6i/4i",
        frame=pygmt.params.Frame(
            axes="WSne",
            title="Diamond price by carat",
            xaxis=pygmt.params.Axis(annot=True, tick=True, label="Carat"),
            yaxis=pygmt.params.Axis(annot=True, tick=True, label="Price (USD)"),
        )
    )
    for cut_id, cut_name in enumerate(CUT_ORDER):
        cut_data = data[data["cut"] == cut_name]
        fig.plot(
            x=cut_data["carat"],
            y=cut_data["price"],
            style=f"c{MARKER_SIZE_POINTS}p",
            fill=f"{COLORS[cut_id]}@50",
            label=cut_name,
        )
    fig.legend(position=pygmt.params.Position("TR", offset=0.1))
    return fig


def save_pygmt(fig: pygmt.Figure, output: Path) -> None:
    """Save a PyGMT figure."""
    fig.savefig(output)


def benchmark(
    name: str,
    plot_func,
    save_func,
    data: pd.DataFrame,
    output_dir: Path,
    repeats: int,
) -> tuple[list[float], list[float]]:
    """Time repeated plot creation and figure export runs.

    The first call is an untimed warmup. It absorbs one-time backend setup such as font
    discovery, and data downloading.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Warm up each backend once before recording timings.
    fig = plot_func(data)
    save_func(fig, output_dir / f"{name}_warmup.png")

    plot_timings = []
    save_timings = []
    for run_id in range(repeats):
        output = output_dir / f"{name}_{run_id + 1}.png"

        start = time.perf_counter()
        fig = plot_func(data)
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
    """Run the diamonds plotting benchmark."""
    data = load_diamonds_data()
    plotters = {
        "matplotlib": plot_matplotlib,
        "pygmt": plot_pygmt,
    }
    savers = {
        "matplotlib": save_matplotlib,
        "pygmt": save_pygmt,
    }

    print(f"Running {REPEATS} timed run(s) per backend")
    print(f"Writing PNG files to {OUTPUT_DIR}")

    for backend in BACKENDS:
        print(f"Benchmarking {backend}...", flush=True)
        plot_timings, save_timings = benchmark(
            name=backend,
            plot_func=plotters[backend],
            save_func=savers[backend],
            data=data,
            output_dir=OUTPUT_DIR,
            repeats=REPEATS,
        )
        print(format_summary(f"{backend} plot", plot_timings))
        print(format_summary(f"{backend} savefig", save_timings))


if __name__ == "__main__":
    main()
