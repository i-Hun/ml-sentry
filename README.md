# ml-sentry

> Lightweight profiling decorator for ML & data pipelines
> Track execution time, real memory usage, and inspect data shapes — with zero boilerplate.

---

## Features

*  **Execution time tracking**
*  **Python memory peak** (via `tracemalloc`)
*  **Real RSS peak** (process-level, includes NumPy / Torch)
*  **Smart argument logging**

  * `numpy` → shape + dtype
  * `pandas` → shape + columns
  * `polars` → shape + estimated size
  * `LazyFrame` → execution plan
* **Async support**
* **Production-ready (modular, low overhead)**
* **Safe logging (truncated, no crashes on repr)**

---

## Installation

```bash
pip install ml-sentry
```

---

## Quick Start

```python
import logging
from ml_sentry import track

logging.basicConfig(level=logging.INFO)


@track(log_args=True)
def foo(n: int):
    return [i * 2 for i in range(n)]


foo(1_000_000)
```

### Output

```
foo | n=1000000 ::
0.08s | RSS peak 120.50 MB | RSS Δ 80.20 MB
```

---

## Polars Support

### DataFrame

```python
@track(log_args=True)
def process(df):
    return df.select("user_id")
```

```
process | df=PolarsDF(shape=(1_000_000, 5), size=120.5MB) ::
0.42s | RSS peak 300.00 MB | RSS Δ 180.00 MB
```

---

### LazyFrame

```python
@track(log_args=True)
def pipeline(df):
    return (
        df
        .filter(pl.col("user_id") > 10)
        .groupby("user_id")
        .agg(pl.count())
        .collect()
    )
```

```
pipeline | df=PolarsLazyFrame(plan=FILTER → GROUPBY → AGGREGATE ...) ::
0.12s | RSS peak 220.00 MB | RSS Δ 150.00 MB
```

---

## Configuration

```python
@track(
    use_tracemalloc=False,  # track Python heap
    rss_interval=0.01,      # sampling frequency
    log_args=True,          # log arguments
    max_arg_length=200,     # truncate long repr
)
```

---

## What Gets Measured

| Metric     | Description                 |
| ---------- | --------------------------- |
| `time`     | Execution duration          |
| `Py peak`  | Python heap peak            |
| `RSS peak` | Real process memory peak |
| `RSS Δ`    | Memory growth               |

---

## Benchmarks

### Setup

* Python 3.12
* 1M rows dataset
* pandas + numpy pipeline

### Results

| Mode                 | Overhead |
| -------------------- | -------- |
| No profiling         | baseline |
| RSS only             | +1–2%    |
| RSS + tracemalloc    | +5–10%   |
| RSS (0.001 interval) | +10–15%  |

---

## Performance Notes

### `tracemalloc`

* Tracks only Python objects
* Adds overhead (~5–10%)

Use with caution for heavy NumPy / Torch:


---

### RSS Sampling

* Uses background thread
* Accuracy depends on interval

| Interval | Accuracy | Overhead    |
| -------- | -------- | ----------- |
| 0.001    | high     | high        |
| 0.01     | balanced | recommended |
| 0.1      | low      | minimal     |

---

## Supported Types

| Type        | Output Example          |
| ----------- | ----------------------- |
| numpy array | `shape=(1000, 128)`     |
| pandas df   | `shape=(1000, 10)`      |
| polars df   | `size=120MB`            |
| LazyFrame   | `plan=FILTER → GROUPBY` |
| list        | `len=1000`              |

---


## Limitations

* GPU memory not tracked
* tracemalloc ignores NumPy internals
* RSS peak is sampled (not exact kernel-level peak)

---

## Roadmap

* [ ] Prometheus integration
* [ ] JSON structured logging
* [ ] Airflow plugin
* [ ] Memory leak detection
* [ ] Torch / GPU support

---

## Contributing

PRs welcome.
Focus areas:

* new formatters (torch, spark, etc.)
* performance improvements
* integrations

---

## License

MIT
