from textual.widgets import Button, Label
from textual import on
import subprocess
from pathlib import Path

class In2Csv(Button):
    """Uses in2csv to convert .xlsx to .csv"""
    #make a function that uses subprocess to call in2csv
    @on(Button.Pressed)
    def xlsx_2_csv(self) -> None:
        selected_file = self.app.selected_file

        if selected_file is None:
            self.app.query_one('#status', Label).update('select a file first')
            return
        if Path(selected_file).suffix.lower() != '.xlsx':
            self.app.query_one('#status',Label).update('selected file is not an .xlsx file')
            return
        try:
            result = subprocess.run(
            ['in2csv', str(selected_file)],
            capture_output=True,
            text=True,
            check=True
        )
            self.app.query_one('#status',Label).update('conversion worked!')
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            self.app.query_one('#status', Label).update(f'conversion failed: {e.stderr}')