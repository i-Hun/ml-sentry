import logging
import time


def log_metrics(
    func_name: str,
    start_time: float,
    start_rss: int,
    peak_rss: int,
    start_py: int | None,
    peak_py: int | None,
    args_str: str | None,
) -> None:
    duration = time.perf_counter() - start_time

    prefix = func_name
    if args_str:
        prefix += f" | {args_str}"

    if start_py is not None and peak_py is not None:
        logging.info(
            ("%s :: %.2fs | Py peak %.2f MB | Py Δ %.2f MB | RSS peak %.2f MB | RSS Δ %.2f MB"),
            prefix,
            duration,
            peak_py / (1024**2),
            (peak_py - start_py) / (1024**2),
            peak_rss / (1024**2),
            (peak_rss - start_rss) / (1024**2),
        )
    else:
        logging.info(
            "%s :: %.2fs | RSS peak %.2f MB | RSS Δ %.2f MB",
            prefix,
            duration,
            peak_rss / (1024**2),
            (peak_rss - start_rss) / (1024**2),
        )
