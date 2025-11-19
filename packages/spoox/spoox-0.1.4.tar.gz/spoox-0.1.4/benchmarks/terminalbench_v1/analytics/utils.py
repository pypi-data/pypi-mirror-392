import json
import math
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize


def collect_and_concat_tb_logs_and_agentu_logs(run: str) -> dict:
    print(f"\n-- collecting and concatenating {run} logs")
    run_dir = Path.cwd().parent / run

    # get tb results data
    tb_results_dir = run_dir / [d for d in run_dir.iterdir() if d.is_dir() and d.name.endswith("_terminal_bench_logs")][0]
    tb_results_data = json.loads((tb_results_dir / "results.json").read_text())

    # collect tb tasks and logging data
    tb_data = dict()
    for result in tb_results_data['results']:
        tb_data[result['instruction']] = {
            'task_id': result['task_id'],
            'instruction': result['instruction'],
            'is_resolved': bool(result['is_resolved']),
            'failure_mode': result['failure_mode'],
            'total_input_tokens': int(result['total_input_tokens'] or 0),
            'total_output_tokens': int(result['total_output_tokens'] or 0)
        }
    resolved_count = len([d for d in tb_data.values() if d['is_resolved']])
    unresolved_count = len([d for d in tb_data.values() if not d['is_resolved']])
    print(f"-> tb results number of collected results: {len(tb_data.keys())} "
          f"(resolved: {resolved_count}; unresolved: {unresolved_count})")
    assert (resolved_count + unresolved_count) == len(tb_data.keys())

    # collect agentu logging data
    agentu_data = dict()
    for f in run_dir.iterdir():
        if f.is_file() and f.name.endswith("_exec_meta_data.json"):
            logs = json.loads(f.read_text())
            agentu_data[logs['task_instruction']] = logs
    print(f"-> agentu results number of collected results: {len(agentu_data.keys())}")
    assert len(agentu_data.keys()) == len(tb_data.keys())

    # concat both log dicts and use task_ids as keys and not instruction text
    logs_data = dict()
    matches = 0
    no_matches = 0
    for k, v in tb_data.items():
        logs_data[k] = v
        if k in agentu_data:
            matches += 1
            logs_data[k] = v | agentu_data[k]
        else:
            no_matches += 1
    logs_data = {v['task_id']: v for k, v in logs_data.items()}
    print(f"-> concatenated logs number of collected results: {len(logs_data.keys())}")
    print(f"-> concatenated logs: {matches} matches; {no_matches} no matches")
    assert len(logs_data.keys()) == len(tb_data.keys()) == len(agentu_data.keys())
    assert no_matches == 0
    return logs_data


def calc_stats(logs: dict) -> dict:

    stats = dict()

    # accuracy
    n = len(logs)
    solved_c = len([t for t in logs if t['is_resolved']])
    stats['accuracy'] = solved_c / n

    # mean_total_prompt_tokens
    mtpt = mean(sum(t['agent_usage_stats']['prompt_tokens']) for t in logs)
    stats['mean_total_prompt_tokens'] = mtpt

    # mean_total_input_tokens
    mtit = mean(sum(t['agent_usage_stats']['completion_tokens']) for t in logs)
    stats['mean_total_completion_tokens'] = mtit

    # mean_llm_calls
    mlc = mean(t['agent_usage_stats']['llm_calls_count'] for t in logs)
    stats['mean_llm_calls'] = mlc

    # mean_exec_time_min
    metm = mean(t['exec_time'] for t in logs)
    stats['mean_exec_time_min'] = metm

    return stats




def plot_comparing_multiple_runs_two_attributes(data: list[dict], attr_1: str, attr_2: str):
    """
    expected data example:
    data = [
        {"label": "Singleton", "accuracy": [5, 4, 6], "in_tokens": [50, 40, 60]},
        {"label": "MAS-S", "accuracy": [7, 6, 7.5], "in_tokens": [500, 400, 600]},
    ]
    attr_1 = "accuracy"
    attr_2 = "in_tokens"
    """

    xs = list(range(len(data)))
    labels = [d.get("label", str(i)) for i, d in enumerate(data)]
    fig, ax1 = plt.subplots()

    # --- compute means per experiment ---
    y1_means = [mean(d[attr_1]) for d in data]
    y2_means = [mean(d[attr_2]) for d in data]

    # ---- Accuracy scatter on left axis ----
    for i, d in enumerate(data):
        ax1.scatter([i] * len(d[attr_1]), d[attr_1], color="tab:blue", alpha=0.5, label=attr_1 if i == 0 else "",
                    marker="x")
    ax1.plot(xs, y1_means, marker="o", linestyle="-", markersize=4, label=f"{attr_1} mean",
             color="tab:blue")  # mean points + connecting line (left axis)
    ax1.set_ylabel(attr_1, color="tab:blue")
    ax1.tick_params(axis="y")

    # ---- Costs scatter on right axis ----
    ax2 = ax1.twinx()  # create second y-axis
    for i, d in enumerate(data):
        ax2.scatter([i] * len(d[attr_2]), d[attr_2], color="tab:orange", alpha=0.7, label=attr_2 if i == 0 else "",
                    marker="x")
    ax2.plot(xs, y2_means, marker="o", linestyle="-", markersize=4, label=f"{attr_2} mean",
             color="tab:orange")  # mean points + connecting line (left axis)
    ax2.set_ylabel(attr_2, color="tab:orange")
    ax2.tick_params(axis="y")

    # ---- Shared x-axis formatting ----
    ax1.set_xticks(xs)
    ax1.set_xticklabels(labels)
    ax1.set_title(f"{attr_1} vs {attr_2}")

    # ---- Legends ----
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right")

    fig.tight_layout()
    plt.show()


import math
from statistics import mean
import matplotlib.pyplot as plt

import math
from statistics import mean
import matplotlib.pyplot as plt

def plot_multi_comparing_runs_two_attributes(
        data: list[dict],
        attr_pairs: list[tuple[str, ...]],
        title: str | None = None,
        ylims: list[tuple[float | None, float | None]] | None = None,
):
    """
    Plot single- or dual-axis comparisons for given attribute pairs.

    Parameters
    ----------
    data : list of dict
        Each dict holds experiment results, e.g.
        {"label": "MAS-S", "accuracy": [7,6,7.5], "in_tokens": [500,400,600]}
    attr_pairs : list of tuples
        Tuples of attributes to compare.
        - ("a",)   -> single-axis plot for 'a'
        - ("a","b")-> dual-axis plot with left 'a', right 'b'
    title : str, optional
        Global figure title
    ylims : list of (ymin, ymax), optional
        One tuple per plot in attr_pairs.
        If None, no limits applied.
        Example: [(0,1), (None,1000), ...]
    """
    if not attr_pairs:
        raise ValueError("attr_pairs must contain at least one tuple, e.g. ('accuracy',) or ('accuracy','in_tokens').")

    if ylims is not None and len(ylims) != len(attr_pairs):
        raise ValueError("ylims must have the same length as attr_pairs")

    xs = list(range(len(data)))
    labels = [d.get("label", str(i)) for i, d in enumerate(data)]

    n = len(attr_pairs)
    ncols = 2
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4.2 * nrows), squeeze=False)

    for idx, pair in enumerate(attr_pairs):
        r, c = divmod(idx, ncols)
        ax1 = axes[r][c]

        ymin, ymax = (ylims[idx] if ylims else (None, None))

        if len(pair) == 1:
            # --- single axis ---
            attr_1 = pair[0]
            y1_means = [mean(d[attr_1]) for d in data]

            for i, dct in enumerate(data):
                ax1.scatter([i] * len(dct[attr_1]), dct[attr_1],
                            alpha=0.5, marker="x", color="tab:blue",
                            label=(attr_1 if i == 0 else ""))
            ax1.plot(xs, y1_means, marker="o", linestyle="--", markersize=4,
                     label=f"{attr_1} mean", color="tab:blue")

            ax1.set_ylabel(attr_1, color="tab:blue")
            ax1.tick_params(axis="y")
            if ymin is not None or ymax is not None:
                ax1.set_ylim(bottom=ymin, top=ymax)

            ax1.set_xticks(xs)
            ax1.set_xticklabels(labels)
            #ax1.set_title(attr_1)

            l1, lab1 = ax1.get_legend_handles_labels()
            if l1:
                ax1.legend(l1, lab1, loc="lower right", fontsize=9)

        elif len(pair) == 2:
            # --- dual axis ---
            attr_1, attr_2 = pair
            y1_means = [mean(d[attr_1]) for d in data]
            y2_means = [mean(d[attr_2]) for d in data]

            # left
            for i, dct in enumerate(data):
                ax1.scatter([i] * len(dct[attr_1]), dct[attr_1],
                            alpha=0.5, marker="x", color="tab:blue",
                            label=(attr_1 if i == 0 else ""))
            ax1.plot(xs, y1_means, marker="o", linestyle="--", markersize=4,
                     label=f"{attr_1} mean", color="tab:blue")
            ax1.set_ylabel(attr_1, color="tab:blue")
            ax1.tick_params(axis="y")
            if ymin is not None or ymax is not None:
                ax1.set_ylim(bottom=ymin, top=ymax)

            # right
            ax2 = ax1.twinx()
            for i, dct in enumerate(data):
                ax2.scatter([i] * len(dct[attr_2]), dct[attr_2],
                            alpha=0.5, marker="x", color="tab:orange",
                            label=(attr_2 if i == 0 else ""))
            ax2.plot(xs, y2_means, marker="o", linestyle="--", markersize=4,
                     label=f"{attr_2} mean", color="tab:orange")
            ax2.set_ylabel(attr_2, color="tab:orange")
            ax2.tick_params(axis="y")
            if ymin is not None or ymax is not None:
                ax2.set_ylim(bottom=ymin, top=ymax)

            ax1.set_xticks(xs)
            ax1.set_xticklabels(labels)
            #ax1.set_title(f"{attr_1} vs {attr_2}")

            l1, lab1 = ax1.get_legend_handles_labels()
            l2, lab2 = ax2.get_legend_handles_labels()
            if l1 or l2:
                ax1.legend(l1 + l2, lab1 + lab2, loc="lower right", fontsize=9)

        else:
            raise ValueError(f"Each tuple must have length 1 or 2, got: {pair}")

    # hide unused subplots
    for k in range(n, nrows * ncols):
        r, c = divmod(k, ncols)
        axes[r][c].axis("off")

    if title:
        fig.suptitle(title, y=0.995, fontsize=14)
    fig.tight_layout()
    plt.show()

def plot_task_correctness_colored_bars(data: dict[int, list[float]], vmin=0.0, vmax=1.0, edge=False):
    """
        Each key -> stacked bar.
          - Segments have height = value
          - Values sorted descending so high (green) at bottom, low (orange) at top
          - Color maps 1 -> green, 0 -> orange
        """
    # sort bars by total height
    items = sorted(data.items(), key=lambda kv: sum(kv[1]), reverse=True)

    x = np.arange(len(items))

    # colormap: 0 = orange, 1 = green
    cmap = LinearSegmentedColormap.from_list("orange_to_green", ["darkorange", "darkgreen"])
    norm = Normalize(vmin=vmin, vmax=vmax)

    fig, ax = plt.subplots()

    for xi, (key, values) in enumerate(items):
        bottom = 0
        # sort values descending → green at bottom, orange at top
        for v in sorted(values, reverse=True):
            vv_clip = np.clip(float(v), vmin, vmax)
            color = cmap(norm(vv_clip))
            ax.bar(
                xi, 2, bottom=bottom,  # fixed height=1 # todo should be 1 not 2 -> required cause of subset 40
                color=color if key != 0 else "lightgrey", edgecolor="black", linewidth=0.6 if edge else 0
            )
            bottom += 1

    # x labels
    ax.set_xticks(x)
    ax.set_xticklabels([str(k) for k, _ in items])
    ax.set_ylabel("tasks count")
    ax.set_title("task solver appropriately (1 = task solved by the appropriate agents | 0 = task not solved by the appropriate agents)")

    # colorbar
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, pad=0.01)
    cbar.set_label("appropriate scoring")

    plt.tight_layout()
    plt.show()