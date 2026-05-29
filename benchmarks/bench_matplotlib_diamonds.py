"""
Benchmark PyGMT and matplotlib when plotting the diamonds dataset.

This benchmark can time either plot construction only or the complete plotting
workflow: create a fresh figure, draw the scatter plot, add labels/legend, and write
the figure to disk. Dataset loading is intentionally outside the timed section so the
results focus on plotting and rendering rather than network or CSV parsing time.
"""

import argparse
import statistics
import time
from pathlib import Path

import pandas as pd
import pygmt
import matplotlib.pyplot as plt  # noqa: E402


COLORS = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd")
BACKENDS = ("matplotlib", "pygmt")
MODES = ("plot", "save")
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


def plot_matplotlib(data: pd.DataFrame, output: Path, save: bool) -> None:
    """Create and render the diamonds scatter plot with matplotlib.

    The function deliberately creates a new figure on each call so repeated runs
    measure the full plotting workflow, matching the PyGMT function below. Set
    ``save`` to false to measure plot construction without file export.
    """
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
    if save:
        fig.savefig(output)
    plt.close(fig)


def plot_pygmt(data: pd.DataFrame, output: Path, save: bool) -> None:
    """Create and render the diamonds scatter plot with PyGMT.

    PyGMT accepts tabular data directly. Passing only the two plotted columns keeps
    this comparable to the x/y arrays handed to matplotlib. Set ``save`` to false to
    measure plot construction without file export.
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
    if save:
        fig.savefig(output)


def benchmark(
    name: str,
    plot_func,
    data: pd.DataFrame,
    output_dir: Path,
    repeats: int,
    save: bool,
) -> list[float]:
    """Time repeated plot creation and rendering runs.

    The first call is an untimed warmup. It absorbs one-time backend setup such as
    font discovery, GMT session initialization, and dynamic library loading.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Warm up each backend once before recording timings.
    plot_func(data, output_dir / f"{name}_warmup.png", save)

    timings = []
    for run_id in range(repeats):
        output = output_dir / f"{name}_{run_id + 1}.png"
        start = time.perf_counter()
        plot_func(data, output, save)
        timings.append(time.perf_counter() - start)

    return timings


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


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Benchmark PyGMT and matplotlib diamonds scatter plotting."
    )
    parser.add_argument(
        "--backend",
        choices=(*BACKENDS, "all"),
        default="all",
        help="plotting backend to benchmark",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=10,
        help="number of timed runs per backend",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("plots/diamonds"),
        help="directory for rendered PNG files",
    )
    parser.add_argument(
        "--mode",
        choices=(*MODES, "both"),
        default="both",
        help="benchmark plot construction, plot-and-save, or both",
    )
    return parser.parse_args()


def main() -> None:
    """Run the diamonds plotting benchmark."""
    args = parse_args()
    if args.repeats < 1:
        raise SystemExit("--repeats must be at least 1")

    data = load_diamonds_data()
    selected_backends = BACKENDS if args.backend == "all" else (args.backend,)
    plotters = {
        "matplotlib": plot_matplotlib,
        "pygmt": plot_pygmt,
    }
    selected_modes = MODES if args.mode == "both" else (args.mode,)

    print(f"Running {args.repeats} timed run(s) per backend")
    if "save" in selected_modes:
        print(f"Writing PNG files to {args.output_dir}")
    for mode in selected_modes:
        save = mode == "save"
        print(f"Mode: {mode}")
        for backend in selected_backends:
            print(f"Benchmarking {backend}...", flush=True)
            timings = benchmark(
                name=f"{backend}_{mode}",
                plot_func=plotters[backend],
                data=data,
                output_dir=args.output_dir,
                repeats=args.repeats,
                save=save,
            )
            print(format_summary(backend, timings))


if __name__ == "__main__":
    main()
