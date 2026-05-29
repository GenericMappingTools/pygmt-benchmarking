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

The benchmarks were run on a MacBook Pro (Apple M5, 32GB RAM) running macOS Tahoe 26.1.

### Benchmark 1: Diamonds Dataset

The diamonds benchmark compares PyGMT and matplotlib when plotting the seaborn diamonds
dataset.

| Mode | matplotlib | PyGMT | Ratio |
| --- | --- | --- | --- |
| Plot | 0.0184s | 0.0299s | 0.6x |
| Plot and Save | 0.1213s | 0.8311s | 0.15x |

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for
details.
