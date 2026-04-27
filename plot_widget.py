from textual_plotext import PlotextPlot


class DataPlot(PlotextPlot):
    """Renders an X-vs-Y EDA plot inside the TUI via textual-plotext."""

    def on_mount(self) -> None:
        self.plt.title("Load a file, pick X and Y columns, then press Plot")
        self.plt.theme("dark")

    def replot_xy(self, x_col, y_col, x_values, y_values, plot_type="line"):
        """
        Render a new plot.

        x_col, y_col  — column name strings used for axis labels and title
        x_values      — list of floats or strings (strings become bar labels)
        y_values      — list of floats
        plot_type     — "line", "bar", "scatter", or "hist"
        """
        self.plt.clear_figure()
        self.plt.theme("dark")

        if not y_values:
            self.plt.title("No numeric data found in the Y column")
            self.refresh()
            return

        if plot_type == "line":
            self.plt.plot(x_values, y_values, label=y_col)
        elif plot_type == "bar":
            self.plt.bar(x_values, y_values, label=y_col)
        elif plot_type == "scatter":
            self.plt.scatter(x_values, y_values, label=y_col)
        elif plot_type == "hist":
            # Histogram only uses Y — X column is ignored
            self.plt.hist(y_values, label=y_col)
            self.plt.xlabel(y_col)
            self.plt.ylabel("count")
            self.plt.title(f"Distribution of {y_col}")
            self.refresh()
            return

        self.plt.title(f"{y_col}  vs  {x_col}")
        self.plt.xlabel(x_col)
        self.plt.ylabel(y_col)
        self.refresh()