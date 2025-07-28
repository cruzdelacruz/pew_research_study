from pathlib import Path
import pandas as pd
import csv

class CsvUtil():
    def __init__(self, 
                 path_to_csv: Path
    ):
        self.path_to_csv = path_to_csv
        if not self.path_to_csv.exists():
            raise FileNotFoundError(f'{self.path_to_csv} not found')
    
    def fill_forward(self,
                     col_name: str
    ) -> Path:
        """Perform a fill forward on a column

        Args:
            col_name (str): column that you want to fill forward

        Returns:
            Path: Path to the output file
        """
        new_rows = []
        with self.path_to_csv.open('r', newline='', encoding='utf-8', errors='replace') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)
            if col_name not in header:
                raise ValueError(f'{col_name} is not a valid header in {self.path_to_csv}')
            new_rows.append(header)
            header_map = {
                v:k for k,v in enumerate(header)
            }
            last_known_value = None
            for row in reader:
                value_to_ffill = row[header_map[col_name]]
                if not pd.isna(value_to_ffill) and value_to_ffill != "":
                    last_known_value = value_to_ffill
                else:
                    row[header_map[col_name]] = last_known_value
                new_rows.append(row)
        
        output_filename = f'{self.path_to_csv.stem}_ffilled'
        output_filepath = self.path_to_csv.parent.joinpath(output_filename).with_suffix('.csv')
        with output_filepath.open('w', newline='', encoding='utf-8') as out_file:
            writer = csv.writer(out_file)
            writer.writerows(new_rows)
        
        print(f'Wrote {output_filepath}')

    def to_dict(
            self
    ) -> list[dict]:
        """Return CSV file as a python list of dicts
        
        Returns:
            list[dict]: List of dictionaries representing CSV rows
        """
        with self.path_to_csv.open('r', newline='', encoding='utf-8') as csv_file:
            return list(csv.DictReader(csv_file))