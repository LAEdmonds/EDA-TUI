from pathlib import Path
import csv

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Label, Select, Static

from plot_widget import DataPlot
from tree import FilteredDirectoryTree

import pandas as pd


class EdaExplorerApp(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [("q", "quit", "Quit")]

    selected_file = reactive(None)
    active_csv_text = reactive("")
    column_names = reactive(list)

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main"):
            yield FilteredDirectoryTree("./data", id="file-tree")

            with Vertical(id="right-panel"):
                yield Label("Select a file", id="status")

                # Load button in the toolbar
                with Horizontal(id="button-row"):
                    yield Button("Load / Convert", id="load-btn", variant="primary")
                    yield Button("Missing", id="stats-missing-btn")
                    yield Button("Headers", id="stats-headers-btn")

                with Horizontal(id="lower-panel"):
                    # Controls sidebar: X col, Y col, plot type, plot button
                    with Vertical(id="controls-panel"):
                        yield Label("X Axis")
                        yield Select(options=[], id="x-col")

                        yield Label("Y Axis")
                        yield Select(options=[], id="y-col")

                        yield Label("Plot Type")
                        yield Select(
                            options=[
                                ("Line", "line"),
                                ("Bar", "bar"),
                                ("Scatter", "scatter"),
                                ("Histogram", "hist"),
                            ],
                            value="line",
                            id="plot-type",
                        )

                        yield Button("Plot", id="plot-btn", variant="success", disabled=True)

                    with Vertical(id="display-panel"):
                        yield Label("Output")
                        with VerticalScroll(id="stats-panel"):
                            yield Static("Load a file first.", id="stats-output")

                        yield DataPlot(id="data-plot")

        yield Footer()

    def _status(self, msg):
        self.query_one("#status", Label).update(msg)

    def _output(self, msg):
        self.query_one("#stats-output", Static).update(msg)

    def watch_selected_file(self, path):
        self.active_csv_text = ""
        self.column_names = []
        self.query_one("#plot-btn", Button).disabled = True
        self._output("Load a file first.")

        if path:
            self._status(f"{path.name} ready")

    def watch_column_names(self, names):
        opts = [(n, n) for n in names]
        self.query_one("#x-col", Select).set_options(opts)
        self.query_one("#y-col", Select).set_options(opts)
        self.query_one("#plot-btn", Button).disabled = not names

     # events
    def _load_file(self, path: Path) -> str:
        if path.suffix.lower() == ".csv":
            return path.read_text(encoding="utf-8", errors="replace")

        df = pd.read_excel(path)
        return df.to_csv(index=False)

    def _parse_rows(self, text: str):
        return list(csv.DictReader(text.splitlines()))

    @on(Button.Pressed, "#load-btn")
    def load_file(self):
        if not self.selected_file:
            self._status("Select a file first")
            return

        path = Path(self.selected_file)
        csv_text = self._load_file(path)

        rows = self._parse_rows(csv_text)

        if not rows:
            self._status("Invalid or empty file")
            return

        self.active_csv_text = csv_text
        self.column_names = list(rows[0].keys())

        self._status(f"{path.name} loaded")

    @on(Button.Pressed, "#stats-missing-btn")
    def missing(self):
        if not self.column_names:
            self._output("Load a file first.")
            return

        reader = csv.DictReader(self.active_csv_text.splitlines())

        counts = {c: 0 for c in self.column_names}

        for row in reader:
            for c in self.column_names:
                if row.get(c, "") == "":
                    counts[c] += 1

        self._output(
            "Missing values:\n" +
            "\n".join(f"{c}: {counts[c]}" for c in self.column_names)
        )

    @on(Button.Pressed, "#stats-headers-btn")
    def headers(self):
        if not self.column_names:
            self._output("Load a file first.")
            return

        self._output("\n".join(self.column_names))

    def _to_float(self, v):
        try:
            return float(v.replace(",", "").strip())
        except:
            return None

    @on(Button.Pressed, "#plot-btn")
    def plot_selected(self):
        x_col = str(self.query_one("#x-col", Select).value)
        y_col = str(self.query_one("#y-col", Select).value)
        plot_type = str(self.query_one("#plot-type", Select).value)

        # parse csv to build X and Y lists, skipping bad Y values
        reader = csv.DictReader(self.active_csv_text.splitlines())

        xs, ys = [], []
        skipped = 0

        for row in reader:
            yv = self._to_float(row.get(y_col, ""))
            if yv is None:
                skipped += 1
                continue

            xv = row.get(x_col, "")
            # X can be numeric or a string label (e.g. dates, names)
            try:
                xs.append(float(xv))
            except:
                xs.append(xv)

            ys.append(yv)

        self.query_one(DataPlot).replot_xy(x_col, y_col, xs, ys, plot_type)

        self._status(f"Plotted {y_col} vs {x_col} ({skipped} skipped)")


if __name__ == "__main__":
    EdaExplorerApp().run()