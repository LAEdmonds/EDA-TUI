from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Label, Footer, Header, Button, Select
from textual.containers import Horizontal, Vertical
from textual import on
from tree import FilteredDirectoryTree
from plot_widget import DataPlot
from pathlib import Path
import subprocess
import csv


class EdaExplorerApp(App):
    """EDA from your terminal — a data journalism TUI."""

    CSS_PATH = "style.tcss"

    BINDINGS = [
        ("q", "quit", "Quit")  
    ]
    # makes code reactive to user
    selected_file = reactive(None)
    active_csv_text = reactive("")
    column_names = reactive(list)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            yield FilteredDirectoryTree("./data", id="file-tree")
            with Vertical(id="right-panel"):
                yield Label(
                    "Select a .csv or .xlsx file from the tree on the left",
                    id="status",
                )
                # Load button in the toolbar 
                with Horizontal(id="button-row"):
                    yield Button("Load / Convert", id="load-btn", variant="primary")
                with Horizontal(id="lower-panel"):
                    # Controls sidebar: X col, Y col, plot type, plot button
                    with Vertical(id="controls-panel"):
                        yield Label("X Axis", classes="axis-label")
                        yield Select(options=[], id="x-col")
                        yield Label("Y Axis", classes="axis-label")
                        yield Select(options=[], id="y-col")
                        yield Label("Plot Type", classes="axis-label")
                        yield Select(
                            options=[
                                ("Line",      "line"),
                                ("Bar",       "bar"),
                                ("Scatter",   "scatter"),
                                ("Histogram", "hist"),
                            ],
                            value="line",
                            id="plot-type",
                        )
                        yield Button(
                            "Plot",
                            id="plot-btn",
                            variant="success",
                            disabled=True,
                        )
                    yield DataPlot(id="data-plot")
        yield Footer()

    def watch_selected_file(self, path: Path | None) -> None:
        if path:
            self.query_one("#status", Label).update(
                f"{path.name}  —  press 'Load / Convert' to inspect"
            )

    def watch_column_names(self, names: list) -> None:
        options = [(name, name) for name in names]
        self.query_one("#x-col", Select).set_options(options)
        self.query_one("#y-col", Select).set_options(options)
        self.query_one("#plot-btn", Button).disabled = len(names) == 0

    # events
    @on(FilteredDirectoryTree.FileSelected)
    def on_file_selected(self, event: FilteredDirectoryTree.FileSelected) -> None:
        self.selected_file = Path(event.path)
        self.active_csv_text = ""
        self.column_names = []

    @on(Button.Pressed, "#load-btn")
    def load_file(self) -> None:
        if self.selected_file is None:
            self.query_one("#status", Label).update("Select a file first")
            return

        path = self.selected_file
        self.query_one("#status", Label).update(f"Loading {path.name} ...")

        try:
            if path.suffix.lower() == ".xlsx":
                result = subprocess.run(
                    ["in2csv", str(path)],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                )
                csv_text = result.stdout
            elif path.suffix.lower() == ".csv":
                csv_text = path.read_text(encoding="utf-8", errors="replace")
            else:
                self.query_one("#status", Label).update(
                    f"Unsupported file type: {path.suffix}"
                )
                return

            self.active_csv_text = csv_text

            cols_result = subprocess.run(
                ["csvcut", "-n"],
                input=csv_text,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            names = [
                line.split(":", 1)[1].strip()
                for line in cols_result.stdout.strip().splitlines()
                if ":" in line
            ]
            self.column_names = names

            row_count = max(csv_text.count("\n") - 1, 0)
            self.query_one("#status", Label).update(
                f"{path.name}  ·  {len(names)} columns  ·  ~{row_count} rows"
                "  —  pick X and Y columns, then press 'Plot'"
            )

        except subprocess.TimeoutExpired:
            self.query_one("#status", Label).update("Error: command timed out")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            self.query_one("#status", Label).update(f"Error: {error_msg}")
        except Exception as exc:
            self.query_one("#status", Label).update(f"Error: {exc}")

    @on(Button.Pressed, "#plot-btn")
    def plot_selected(self) -> None:
        x_col = self.query_one("#x-col", Select).value
        y_col = self.query_one("#y-col", Select).value
        plot_type = str(self.query_one("#plot-type", Select).value)

        # Select.BLANK means the user hasn't chosen yet
        if x_col is Select.BLANK or y_col is Select.BLANK:
            self.query_one("#status", Label).update(
                "Choose both an X and a Y column before plotting"
            )
            return
        if not self.active_csv_text:
            self.query_one("#status", Label).update("Load a file first")
            return

        x_col = str(x_col)
        y_col = str(y_col)

        # parse csv to build X and Y lists, skipping bad Y values
        reader = csv.DictReader(self.active_csv_text.splitlines())
        x_values = []
        y_values = []
        skipped = 0

        for row in reader:
            raw_y = row.get(y_col, "").strip()
            raw_x = row.get(x_col, "").strip()
            try:
                y_values.append(float(raw_y))
                # X can be numeric or a string label (e.g. dates, names)
                try:
                    x_values.append(float(raw_x))
                except ValueError:
                    x_values.append(raw_x)
            except ValueError:
                skipped += 1

        self.query_one(DataPlot).replot_xy(
            x_col, y_col, x_values, y_values, plot_type
        )

        note = f"  ({skipped} row(s) skipped — non-numeric Y)" if skipped else ""
        self.query_one("#status", Label).update(
            f"Plotted: {y_col} vs {x_col}{note}"
        )


if __name__ == "__main__":
    EdaExplorerApp().run()