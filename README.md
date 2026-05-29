# pygmt-benchmarking

Benchmarks comparing PyGMT with tools in the Python visualization and geospatial
analysis ecosystem.

## Environment

To set up the environment for running the benchmarks, run the following commands:

```bash
conda env create -f environment.yml
conda activate pygmt-benchmarking
```

## Benchmarks

The benchmarks were run on a MacBook Pro (Apple M5, 32GB RAM) running macOS
Tahoe 26.1.

### Benchmark 1: Diamonds Dataset

The diamonds benchmark compares PyGMT and matplotlib when plotting the seaborn
diamonds dataset. It reports plotting time and `savefig` time separately.

Run the benchmark:

```bash
python benchmarks/bench_matplotlib_diamonds.py
```

| Step | matplotlib | PyGMT | PyGMT / matplotlib |
| --- | --- | --- | --- |
| Plotting | 0.021 | 0.028 | 0.75x |
| Savefig | 0.13 | 1.135 | 0.11x |

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for
details.
