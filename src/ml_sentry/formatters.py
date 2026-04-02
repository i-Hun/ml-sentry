from collections.abc import Callable, Iterable


def smart_format_args(
    func: Callable,
    args: tuple,
    kwargs: dict,
    *,
    max_length: int = 200,
) -> str:
    """Smart formatting of args/kwargs for ML/debug-friendly logging."""

    try:
        import numpy as np
    except ImportError:
        np = None

    try:
        import pandas as pd
    except ImportError:
        pd = None

    try:
        import polars as pl
    except ImportError:
        pl = None

    def safe_repr(obj: object) -> str:
        try:
            s = repr(obj)
        except Exception:
            return "<unreprable>"

        if len(s) > max_length:
            return s[:max_length] + "..."
        return s

    def format_bytes(n: int) -> str:
        return f"{n / (1024**2):.1f}MB"

    def format_value(v: object) -> str:
        # --- numpy ---
        if np is not None and isinstance(v, np.ndarray):
            return f"ndarray(shape={v.shape}, dtype={v.dtype})"

        # --- pandas ---
        if pd is not None:
            if isinstance(v, pd.DataFrame):
                cols_preview = list(v.columns[:5])
                return f"DataFrame(shape={v.shape}, cols={cols_preview}...)"
            if isinstance(v, pd.Series):
                return f"Series(len={len(v)}, name={v.name})"

        # --- polars ---
        if pl is not None:
            # DataFrame
            if isinstance(v, pl.DataFrame):
                cols_preview = v.columns[:5]
                try:
                    size = format_bytes(v.estimated_size())
                except Exception:
                    size = "?"

                return f"PolarsDF(shape={v.shape}, cols={cols_preview}..., size={size})"

            # LazyFrame
            if isinstance(v, pl.LazyFrame):
                try:
                    plan = v.explain(optimized=True)
                    plan = " ".join(plan.split())  # compact
                    if len(plan) > max_length:
                        plan = plan[:max_length] + "..."
                except Exception:
                    plan = "?"

                return f"PolarsLazyFrame(plan={plan})"

            # Series
            if isinstance(v, pl.Series):
                return f"PolarsSeries(len={v.len()}, name={v.name})"

        # --- dict ---
        if isinstance(v, dict):
            return f"dict(len={len(v)})"

        # --- iterable ---
        if isinstance(v, Iterable) and not isinstance(v, (str, bytes)):
            try:
                length = len(v)  # type: ignore
                preview = list(v)[:3]
                return f"{type(v).__name__}(len={length}, preview={preview})"
            except Exception:
                return f"{type(v).__name__}"

        # --- fallback ---
        return safe_repr(v)

    parts = []

    arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]

    for i, value in enumerate(args):
        name = arg_names[i] if i < len(arg_names) else f"arg{i}"
        parts.append(f"{name}={format_value(value)}")

    for k, v in kwargs.items():
        parts.append(f"{k}={format_value(v)}")

    return ", ".join(parts)
