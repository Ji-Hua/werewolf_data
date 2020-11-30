import json
import re

import docx
import pandas as pd

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

# NOTE:
# FORMATTED_ROW = {
#     'name': "",
#     'seat': "",
#     'character': "",
#     'death_round': "",
#     'death_method': "",
#     'votes': {},
#     'actions': {},
#     'badge': {}
# }

ROLE_SKILL_DICT = {
    '狼人': '猎杀',
    '预言家': '查验',
    '猎人': '枪杀',
    '守卫': '守护',
    '白痴': '神志',
    '混血儿': '选混',
    '梦魇': '恐惧',
    '通灵师': '查验',
    '机械狼': '魔仿',
    '猎魔人': '狩猎',
    '魔狼': '重创',
}
def format_night_action(action, role):
    if role in ROLE_SKILL_DICT:
        match = re.search("\d+", action)
        if match:
            target = int(match.group(0))
        else:
            target = None
        ability = ROLE_SKILL_DICT[role]
    elif role == '女巫':
        match = re.search(r"(\D+)(\d+)", action)
        if match:
            if '救' in match.group(1):
                ability = "解救"
            elif '毒' in match.group(1):
                ability = "毒杀"
            else:
                raise ValueError(f'{action} is not valid for 女巫')
            target = int(match.group(2))
        else:
            ability = "用药"
            target = None
    else:
        raise ValueError(f'{role} {action}')    
    return (ability, target)


def format_day_action(action):
    clean_results = {'badge': None, 'explode': None,
    'death': None, 'banish': None, 'shot': None}
    descs = action.split('，')
    for desc in descs:
        sheriff_match = re.search(r'(\d+)警长', desc)
        if sheriff_match:
            clean_results['badge'] = int(sheriff_match.group(1))
            continue

        banish_match = re.search(r'(\d+)出局', desc)
        if banish_match:
            clean_results['banish'] = int(banish_match.group(1))
            continue
        
        shot_match = re.search(r'(\d+)\w*枪杀(\d+)', desc)
        if shot_match:
            clean_results['shot'] = {
                'source': int(shot_match.group(1)),
                'target': int(shot_match.group(2))
            }
            continue

        explode_match = re.search(r'(\d+)自爆', desc)
        if explode_match:
            clean_results['explode'] = int(explode_match.group(1))
        
        death_match = re.search('(\S+)[双,三,四,五]?死', desc)
        if death_match:
            text = re.sub('\D+', ' ', death_match.group(1))
            death_seats = [int(s) for s in text.split()]
            clean_results['death'] = death_seats

    return clean_results

def create_role_seat_dict(action_df):
    roles = action_df.loc[0]
    reverse_map = {}
    for i, seats in enumerate(roles):
        if i == 0:
            continue

        role = action_df.columns[i]
        # handle special case like ‘狼兄 狼弟’
        if ' ' in role:
            role_names = role.split()
            seat_tokens = seats.split()
            if len(role_names) != len(seat_tokens):
                raise ValueError('Role size and seat size do not match')
            for r, s in zip(role_names, seat_tokens):
                reverse_map[r] = int(s)
        
        else:
            try:
                seat = int(seats)
                cleaned_seat = seat
            except ValueError:
                tokens = seats.split()
                cleaned_seat = []
                for t in tokens:
                    seat = int(t)
                    cleaned_seat.append(seat)
            reverse_map[role] = cleaned_seat
    
    return reverse_map

ABILITY_CAN_KILL_AT_NIGHT = ['毒杀', '猎杀']

def process_game_date(action_df, vote_df):
    clean_data = {}
    names = vote_df.loc[0]
    for i, name in enumerate(names):
        if i > 0:
            clean_data[i] = {'name': name, 'seat': i,
                'role': '平民'} # set default

    role_map = create_role_seat_dict(action_df)
    for role, seats in role_map.items():
        if isinstance(seats, list):
            for seat in seats:
                clean_data[seat]['role'] = role
        else:
            seat = seats
            clean_data[seat]['role'] = role

    for i in range(1, vote_df.shape[0]):
        row = vote_df.loc[i]
        round = row[0]
        for seat, ballot in enumerate(row):
            if seat == 0:
                continue
            votes =  clean_data[seat].get('votes', {})
            votes[round] = ballot
            clean_data[seat]['votes'] = votes

    raw_roles = list(action_df.columns)[1:]
    night_deaths = {}
    previous_round = None
    for i in range(1, action_df.shape[0]):
        row = action_df.loc[i]
        round = row['角色']
        if '夜' in round:
            night_deaths[round] = {}
            for role in raw_roles:
                if ' ' in role:
                    raise Exception(f'Invalid role: {role}')
                role_seat = role_map[role]
                action = row[role]
                ability, target = format_night_action(action, role)
                if ability in ABILITY_CAN_KILL_AT_NIGHT:
                    night_deaths[round][target] = f"{night_deaths[round].get(target, '')} {ability}".strip()
                if target:
                    target_role = clean_data[target]['role']
                    if isinstance(role_seat, list):
                        for s in role_seat:
                            action_dict = clean_data[s].get('actions', {})
                            action_dict[round] = {'ability': ability, 'target_seat': target, 'target_role': target_role}
                            clean_data[s]['actions'] = action_dict

                    else:
                        action_dict = clean_data[role_seat].get('actions', {})
                        action_dict[round] = {'ability': ability, 'target_seat': target, 'target_role': target_role}
                        clean_data[role_seat]['actions'] = action_dict
        elif '天' in round:
            action = row[1]
            cleaned_actions = format_day_action(action)
            if cleaned_actions['badge']:
                clean_data[cleaned_actions['badge']]['badge'] = round
            if cleaned_actions['banish']:
                clean_data[cleaned_actions['banish']]['death_round'] = round
                clean_data[cleaned_actions['banish']]['death_method'] = '放逐'
            if cleaned_actions['explode']:
                clean_data[cleaned_actions['explode']]['death_round'] = round
                clean_data[cleaned_actions['explode']]['death_method'] = '自爆'
            if cleaned_actions['shot']:
                source, target = cleaned_actions['shot']['source'], cleaned_actions['shot']['target']
                target_role = clean_data[target]['role']
                clean_data[target]['death_round'] = round
                clean_data[target]['death_method'] = '枪杀'
                action_dict = clean_data[source].get('actions', {})
                action_dict[round] = {'ability': '枪杀', 'target_seat': target, 'target_role': target_role}
                clean_data[source]['actions'] = action_dict
            if cleaned_actions['death']:
                death_targets = cleaned_actions['death']
                for t in death_targets:
                    death_method = night_deaths[previous_round][t]
                    clean_data[t]['death_round'] = previous_round
                    clean_data[t]['death_method'] = death_method
        else:
            raise ValueError(round)

        previous_round = round
    
    return clean_data



def get_game_data(doc_name, game_id: int):
    vote_table_id = (game_id - 1) * 2
    action_table_id = (game_id - 1) * 2 + 1

    vote_df = pd.DataFrame(read_table(doc_name, vote_table_id))
    action_df = pd.DataFrame(read_table(doc_name, action_table_id))

    cleaned_data = process_game_date(action_df, vote_df)

    return cleaned_data



def write_cleaned_data(cleaned_data, dest):
    with open(dest, 'w+') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)



if __name__ == '__main__':
    doc_name = "./data/HCSSA 桌游社狼人杀游戏裁判表 0905.docx"
    game_id = 1

    new_name = doc_name.split()[-1].split('.')[0]
    dest = f'./cleaned_data/{new_name}-{game_id}.json'

    cleaned_data = get_game_data(doc_name, game_id)
    write_cleaned_data(cleaned_data, dest)
    
