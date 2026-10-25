import tkinter as tk
from tkinter import ttk

import contextlib
import io

from request_generator import (
    generate_patterned_requests,
    generate_random_requests,
    generate_mixed_requests,
)
from integrated_scheduler import compare_modes
from intelligent_scheduler import run_simulation
import metrics


BG = "#F5F0E8"
PANEL_BG = "#EDE8DC"
ACCENT = "#C4A882"
ACCENT_HOVER = "#B8956E"
TEXT_PRIMARY = "#3D2B1F"
TEXT_SECONDARY = "#6B5744"
BORDER = "#D4C4B0"
BAR_COLORS = ["#C4A882", "#A67C5B", "#8B5E3C", "#D4B896", "#E8D5BC"]

HEAD_START = 53
NUM_TRACKS = 200
CACHE_SIZE = 8
PREDICTION_MODE = "SSTF + Adaptive Cache + Prediction"
MIN_BAR_HEIGHT = 20

MODE_LABELS = {
    "Plain SSTF": "Plain SSTF",
    "SSTF + LRU Cache": "SSTF + LRU",
    "SSTF + LRU Cache + Prediction": "SSTF + LRU + Predict",
    "SSTF + Adaptive Cache + Prediction": "SSTF + Adaptive",
}


class DiskSchedulingUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Simulator")
        self.root.geometry("800x750")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self._build_controls()
        self._build_chart()
        self._build_stats()
        self._build_chart2()
        self._build_stats2()

        self.run_simulation()

    # ---------- layout ----------

    def _build_controls(self):
        bar = tk.Frame(self.root, bg=BG, pady=12, padx=16)
        bar.pack(side="top", fill="x")

        title = tk.Label(
            bar, text="Disk Scheduling Simulator", bg=BG, fg=TEXT_PRIMARY,
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(side="left")

        controls = tk.Frame(bar, bg=BG)
        controls.pack(side="right")

        tk.Label(controls, text="Pattern:", bg=BG, fg=TEXT_SECONDARY,
                  font=("Segoe UI", 10)).pack(side="left", padx=(0, 4))
        self.pattern_var = tk.StringVar(value="Patterned")
        pattern_menu = ttk.Combobox(
            controls, textvariable=self.pattern_var, values=["Patterned", "Random", "Mixed"],
            state="readonly", width=10,
        )
        pattern_menu.pack(side="left", padx=(0, 12))

        tk.Label(controls, text="Requests:", bg=BG, fg=TEXT_SECONDARY,
                  font=("Segoe UI", 10)).pack(side="left", padx=(0, 4))
        self.count_var = tk.StringVar(value="100")
        count_menu = ttk.Combobox(
            controls, textvariable=self.count_var, values=["50", "100", "200"],
            state="readonly", width=6,
        )
        count_menu.pack(side="left", padx=(0, 12))

        self.run_button = tk.Button(
            controls, text="Run Simulation", command=self.run_simulation,
            bg=ACCENT, fg=TEXT_PRIMARY, activebackground=ACCENT_HOVER,
            font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=6,
            cursor="hand2",
        )
        self.run_button.pack(side="left")
        self.run_button.bind("<Enter>", lambda e: self.run_button.configure(bg=ACCENT_HOVER))
        self.run_button.bind("<Leave>", lambda e: self.run_button.configure(bg=ACCENT))

    def _build_chart(self):
        frame = tk.Frame(self.root, bg=PANEL_BG, highlightbackground=BORDER,
                          highlightthickness=1)
        frame.pack(side="top", fill="both", expand=True, padx=16, pady=(0, 8))

        self.chart_title = tk.Label(
            frame, text="Total Head Movement by Algorithm", bg=PANEL_BG,
            fg=TEXT_PRIMARY, font=("Segoe UI", 12, "bold"), pady=6,
        )
        self.chart_title.pack(side="top")

        self.canvas = tk.Canvas(frame, bg=PANEL_BG, height=220, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=True, padx=12, pady=(0, 10))

    def _build_stats(self):
        frame = tk.Frame(self.root, bg=BG, padx=16, pady=4)
        frame.pack(side="top", fill="x")

        self.box_best = self._make_stat_box(frame, "Best Algorithm")
        self.box_hit_rate = self._make_stat_box(frame, "Cache Hit Rate")
        self.box_seeks_avoided = self._make_stat_box(frame, "Seeks Avoided")

    def _build_chart2(self):
        frame = tk.Frame(self.root, bg=PANEL_BG, highlightbackground=BORDER,
                          highlightthickness=1)
        frame.pack(side="top", fill="both", expand=True, padx=16, pady=6)

        self.chart2_title = tk.Label(
            frame, text="Head Movement: Cache & Prediction Modes", bg=PANEL_BG,
            fg=TEXT_PRIMARY, font=("Segoe UI", 12, "bold"), pady=6,
        )
        self.chart2_title.pack(side="top")

        self.canvas2 = tk.Canvas(frame, bg=PANEL_BG, height=220, highlightthickness=0)
        self.canvas2.pack(side="top", fill="both", expand=True, padx=12, pady=(0, 10))

    def _build_stats2(self):
        frame = tk.Frame(self.root, bg=BG, padx=16, pady=10)
        frame.pack(side="top", fill="x")

        self.box_useful = self._make_stat_box(frame, "Useful Prefetches")
        self.box_wasted = self._make_stat_box(frame, "Wasted Prefetches")
        self.box_verdict = self._make_stat_box(frame, "Predictor Verdict")

    def _make_stat_box(self, parent, label_text):
        box = tk.Frame(parent, bg=PANEL_BG, highlightbackground=BORDER,
                        highlightthickness=1, padx=12, pady=10)
        box.pack(side="left", fill="both", expand=True, padx=6)

        tk.Label(box, text=label_text, bg=PANEL_BG, fg=TEXT_SECONDARY,
                  font=("Segoe UI", 10)).pack(side="top", anchor="w")
        value_label = tk.Label(box, text="--", bg=PANEL_BG, fg=TEXT_PRIMARY,
                                 font=("Segoe UI", 18, "bold"))
        value_label.pack(side="top", anchor="w", pady=(4, 0))
        return value_label

    # ---------- behavior ----------

    def run_simulation(self):
        count = int(self.count_var.get())
        pattern = self.pattern_var.get()
        if pattern == "Random":
            requests = generate_random_requests(count, num_tracks=NUM_TRACKS, seed=42)
        elif pattern == "Mixed":
            requests = generate_mixed_requests(count, num_tracks=NUM_TRACKS, seed=42)
        else:
            requests = generate_patterned_requests(count, num_tracks=NUM_TRACKS, seed=42)

        movements = metrics.compare_algorithms(requests, NUM_TRACKS, HEAD_START)
        self._draw_bar_chart(self.canvas, movements)

        with contextlib.redirect_stdout(io.StringIO()):
            integrated = compare_modes(
                requests, head_start=HEAD_START, cache_size=CACHE_SIZE, num_tracks=NUM_TRACKS
            )
        mode_movements = {
            MODE_LABELS[name]: stats["head_movement"] for name, stats in integrated.items()
        }
        self._draw_bar_chart(self.canvas2, mode_movements, zoom=True, show_pct_vs_first=True)

        prediction_run = run_simulation(
            requests, cache_size=CACHE_SIZE, use_predictor=True,
            head_start=HEAD_START, num_tracks=NUM_TRACKS,
        )
        self._update_stats(movements, integrated, prediction_run)

    def _draw_bar_chart(self, canvas, data, zoom=False, show_pct_vs_first=False):
        """
        Draw a bar chart of `data` ({label: value}) onto `canvas`.

        zoom: when True, the Y axis starts at (min(values) - 50)
        instead of 0, so similar-sized bars (e.g. the 4 cache/
        prediction modes) show a visually obvious height difference
        instead of looking like four nearly-identical full-height bars.

        show_pct_vs_first: when True, a second line under each bar's
        value shows that bar's percentage change relative to the
        first bar (the baseline mode), e.g. "-1.8%".
        """
        canvas.delete("all")
        canvas.update_idletasks()

        width = canvas.winfo_width() or 740
        height = canvas.winfo_height() or 220
        margin_bottom = 40
        margin_top = 30
        margin_side = 30

        names = list(data.keys())
        values = list(data.values())
        max_value = max(values) if values else 1
        baseline_value = values[0] if values else 0

        if zoom and values:
            axis_min = max(0, min(values) - 50)
        else:
            axis_min = 0
        axis_range = max_value - axis_min

        chart_height = height - margin_bottom - margin_top
        chart_width = width - 2 * margin_side
        bar_gap = 20
        bar_width = (chart_width - bar_gap * (len(names) - 1)) / len(names)

        for i, (name, value) in enumerate(zip(names, values)):
            x0 = margin_side + i * (bar_width + bar_gap)
            x1 = x0 + bar_width
            scaled_height = ((value - axis_min) / axis_range) * chart_height if axis_range else 0
            bar_height = max(scaled_height, MIN_BAR_HEIGHT) if value > axis_min else 0
            y1 = height - margin_bottom
            y0 = y1 - bar_height

            color = BAR_COLORS[i % len(BAR_COLORS)]
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=BORDER)

            value_text = str(value)
            if show_pct_vs_first:
                pct = ((value - baseline_value) / baseline_value * 100) if baseline_value else 0
                value_text = f"{value} ({pct:+.1f}%)"

            canvas.create_text(
                (x0 + x1) / 2, y0 - 10, text=value_text,
                fill=TEXT_PRIMARY, font=("Segoe UI", 9, "bold"),
            )
            canvas.create_text(
                (x0 + x1) / 2, y1 + 16, text=name,
                fill=TEXT_SECONDARY, font=("Segoe UI", 9),
            )

        canvas.create_line(margin_side, height - margin_bottom,
                            width - margin_side, height - margin_bottom,
                            fill=BORDER, width=1)

    def _update_stats(self, movements, integrated, prediction_run):
        best_name = min(movements, key=movements.get)
        best_value = movements[best_name]
        self.box_best.configure(text=f"{best_name} ({best_value})")

        prediction_stats = integrated[PREDICTION_MODE]
        self.box_hit_rate.configure(text=f"{prediction_stats['hit_rate']:.1%}")
        self.box_seeks_avoided.configure(text=str(prediction_stats["seeks_avoided"]))

        useful = prediction_run["useful_prefetches"]
        wasted = prediction_run["wasted_prefetches"]
        self.box_useful.configure(text=str(useful))
        self.box_wasted.configure(text=str(wasted))

        verdict = "Good" if useful > wasted else "Needs Warmup"
        self.box_verdict.configure(text=verdict)


def main():
    root = tk.Tk()
    DiskSchedulingUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
