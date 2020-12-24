import json
import re

import docx
import pandas as pd

from engine_factory import EngineFactory



CHINESE_NUMBER_DICT = {
    1: '一',
    2: '二',
    3: '三',
    4: '四',
    5: '五',
    6: '六',
    7: '七',
    8: '八',
    9: '九'
}


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

def get_game_name_by_id(doc_name, game_id: int):
    document = docx.Document(doc_name)
    paragraph_id = None
    for i, p in enumerate(document.paragraphs):
        pattern = re.compile(f'第{CHINESE_NUMBER_DICT[game_id]}局')
        if re.search(pattern, p.text):
            paragraph_id = i + 1
            break
    template = document.paragraphs[paragraph_id].text.split('：')[-1]
    return re.sub('vs\.?', 'vs.', template)


def get_game_data(doc_name, game_id: int):
    vote_table_id = (game_id - 1) * 2
    action_table_id = (game_id - 1) * 2 + 1

    vote_df = pd.DataFrame(read_table(doc_name, vote_table_id))
    action_df = pd.DataFrame(read_table(doc_name, action_table_id))

    factory = EngineFactory()
    name = get_game_name_by_id(doc_name, game_id)
    cleaned_data = {"template": name}
    parser = factory.construct(name)
    parser.read_data(action_df, vote_df)
    cleaned_data["data"] = parser.parse()

    return cleaned_data



def write_cleaned_data(cleaned_data, dest):
    with open(dest, 'w+') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)



if __name__ == '__main__':
    doc_name = "/mnt/d/BoardGame/Autumn/data/HCSSA 桌游社狼人杀游戏裁判表 0919.docx"
    game_id = 3

    new_name = doc_name.split()[-1].split('.')[0]
    dest = f'./cleaned_data/{new_name}-{game_id}-new.json'

    cleaned_data = get_game_data(doc_name, game_id)
    write_cleaned_data(cleaned_data, dest)
