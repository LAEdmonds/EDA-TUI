from pathlib import Path
from typing import Iterable

from textual.widgets import DirectoryTree 
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
        self.app.selected_file = Path(event.path) 