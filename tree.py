from pathlib import Path
from typing import Iterable

from textual.widgets import DirectoryTree, Label
from textual import on

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        allowed_files = {".csv",".xlsx"}

        return [
            path 
            for path in paths 
            if not path.name.startswith(".") 
            and (path.is_dir() or path.suffix.lower() in allowed_files)
        ]
    

    @on(DirectoryTree.FileSelected)
    def handle_file_selection(self, event: DirectoryTree.FileSelected) -> None:
        file_name = Path(str(event.path)).name
        self.app.query_one('#path-display', Label).update(f'Selected: {file_name}')