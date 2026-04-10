from textual.app import App, ComposeResult
from textual.widgets import Label, Footer, Static
from textual.containers import Horizontal, Vertical
from tree import FilteredDirectoryTree
from button import In2Csv

class EdaExplorerApp(App):
    def __init__(self):
        super().__init__()
        self.selected_file = None

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield FilteredDirectoryTree('./')
            with Vertical():
                yield In2Csv('show column names')
                yield Label('select an .xlsx file', id='status')
                yield Static('column names appear here', id='columns') 

        yield Footer()


if __name__ == "__main__":
    app = EdaExplorerApp()
    app.run()