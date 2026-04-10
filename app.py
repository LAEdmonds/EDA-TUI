from textual.app import App, ComposeResult
from textual.widgets import Label, Footer
from textual.containers import Horizontal
from tree import FilteredDirectoryTree
from button import In2Csv

class EdaExplorerApp(App):
    def __init__(self):
        super().__init__()
        self.selected_file = None

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield FilteredDirectoryTree('./')
            yield In2Csv('convert with in2csv')
            yield Label('no file selected yet', id='status')
        
        yield Footer()


if __name__ == "__main__":
    app = EdaExplorerApp()
    app.run()