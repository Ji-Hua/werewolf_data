import json

import docx
import pandas as pd

from game_parser import GameParser

def read_table(doc_name, table_id: int):
    # Load the first table from your document. In your example file,
    # there is only one table, so I just grab the first one.
    document = docx.Document(doc_name)
    table = document.tables[table_id]

    # Data will be a list of rows represented as dictionaries
    # containing each row's data.
    data = []

    keys = None
    for i, row in enumerate(table.rows):
        text = (cell.text for cell in row.cells)

        # Establish the mapping based on the first row
        # headers; these will become the keys of our dictionary
        if i == 0:
            keys = tuple(text)
            continue

        # Construct a dictionary for this row, mapping
        # keys to values for this row
        row_data = dict(zip(keys, text))
        data.append(row_data)
    
    return data

def get_game_data(doc_name, game_id: int):
    vote_table_id = (game_id - 1) * 2
    action_table_id = (game_id - 1) * 2 + 1

    vote_df = pd.DataFrame(read_table(doc_name, vote_table_id))
    action_df = pd.DataFrame(read_table(doc_name, action_table_id))

    parser = GameParser(action_df, vote_df)
    cleaned_data = parser.parse()

    return cleaned_data



def write_cleaned_data(cleaned_data, dest):
    with open(dest, 'w+') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)



if __name__ == '__main__':
    doc_name = "/mnt/d/BoardGame/Autumn/data/HCSSA 桌游社狼人杀游戏裁判表 0919.docx"
    game_id = 4

    new_name = doc_name.split()[-1].split('.')[0]
    dest = f'./cleaned_data/{new_name}-{game_id}.json'

    cleaned_data = get_game_data(doc_name, game_id)
    write_cleaned_data(cleaned_data, dest)
    
