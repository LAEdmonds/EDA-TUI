from textual.app import App, ComposeResult
from textual.widgets import Label, Footer

from tree import FilteredDirectoryTree

class EdaExplorerApp(App):
    def compose(self) -> ComposeResult:
        yield FilteredDirectoryTree('./')
        yield Label('select a file to see its path', id='path-display')
        yield Footer()


if __name__ == "__main__":
    app = EdaExplorerApp()
    app.run()