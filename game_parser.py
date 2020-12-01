import re
from typing import ItemsView

import pandas as pd


ROLE_SKILL_DICT = {
    '狼人': '猎杀',
    '预言家': '查验',
    '猎人': '枪杀',
    '守卫': '守护',
    '白痴': '神志',
    '混血儿': '选混',
    '野孩子': '选混',
    '梦魇': '恐惧',
    '通灵师': '查验',
    '机械狼': '魔仿',
    '猎魔人': '狩猎',
    '魔狼': '重创',
    '九尾妖狐': '尾巴',
    '黑蝙蝠': '庇护',  #TODO: 反噬？
    '狼美人': '魅惑',
    '武僧': '负伤',
    '恶魔': '查验',
    '恶灵骑士': '反噬',
    '隐狼': '猎杀' #TODO: 觉醒？
}

ABILITY_CAN_KILL_AT_NIGHT = ['毒杀', '猎杀', '魅惑', '反噬']

class GameParser:

    def __init__(self, action_df, vote_df):
        self.action_df = action_df
        self.vote_df = vote_df

        self.clean_data = {}
        self.role_map = {}
        # some actions are conducted as a team so we also
        # need the raw roles
        self.raw_roles = [r for r in list(action_df.columns)[1:] if r != '-']

        # to identify death method, since one person could
        # be hunted and poisoned
        self.night_deaths = {}
    
    def format_night_action(self, action, role):
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
        elif role == '小女孩':
            match = re.search(r"看\s*(\S+)", action)
            ability = '偷看'
            target = None
            if match:
                target = match.group(1)
        elif role == '邪恶商人':
            match = re.search(r"(\w+)->(\d+)", action)
            ability = '交易'
            target = None
            if match:
                target = (match.group(1), int(match.group(2)))
        else:
            raise ValueError(f'{role} {action}')    
        return (ability, target)

    def create_role_seat_dict(self):
        roles = self.action_df.loc[0]
        self.role_map = {}
        for i, seats in enumerate(roles):
            if i == 0:
                continue

            role = self.action_df.columns[i]
            # handle special case like ‘狼兄 狼弟’
            if ' ' in role:
                role_names = role.split()
                seat_tokens = seats.split()
                if len(role_names) != len(seat_tokens):
                    raise ValueError('Role size and seat size do not match')
                for r, s in zip(role_names, seat_tokens):
                    self.role_map[r] = int(s)
            elif role == '-':
                continue
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
                self.role_map[role] = cleaned_seat

    def parse_name_seat(self):
        names = self.vote_df.loc[0]
        for i, name in enumerate(names):
            if i > 0:
                self.clean_data[i] = {'name': name, 'seat': i,
                    'role': '平民'} # set default
        
        self.create_role_seat_dict()
        for role, seats in self.role_map.items():
            if isinstance(seats, list):
                for seat in seats:
                    self.clean_data[seat]['role'] = role
            else:
                seat = seats
                self.clean_data[seat]['role'] = role
    
    def parse_vote_results(self):
        for i in range(1, self.vote_df.shape[0]):
            row = self.vote_df.loc[i]
            round = row[0]
            for seat, ballot in enumerate(row):
                if seat == 0:
                    continue
                votes = self.clean_data[seat].get('votes', {})
                votes[round] = ballot
                self.clean_data[seat]['votes'] = votes
    
    def parse_night_actions(self, round, row):
        self.night_deaths[round] = {}
        for role in self.raw_roles:
            if ' ' in role:
                raise Exception(f'Invalid role: {role}')
            role_seat = self.role_map[role]
            action = row[role]
            ability, target = self.format_night_action(action, role)
            if ability in ABILITY_CAN_KILL_AT_NIGHT:
                method = f"{self.night_deaths[round].get(target, '')} {ability}".strip()
                self.night_deaths[round][target] = method
            if target:
                if isinstance(role_seat, list):
                    target_role = self.clean_data[target]['role']
                    for s in role_seat:
                        action_dict = self.clean_data[s].get('actions', {})
                        action_dict[round] = {'ability': ability,
                            'target_seat': target, 'target_role': target_role}
                        self.clean_data[s]['actions'] = action_dict

                else:
                    action_dict = self.clean_data[role_seat].get('actions', {})
                    if ability == '尾巴':
                        action_dict[round] = {'ability': ability, 'number': target}
                    elif ability == '偷看':
                        action_dict[round] = {'ability': ability, 'target': target}
                    elif ability == '交易':
                        target_role = self.clean_data[target[-1]]['role']
                        action_dict[round] = {'ability': ability, 'item': target[0],
                            'target': target[-1], 'target_role': target_role}
                    else:
                        target_role = self.clean_data[target]['role']
                        action_dict[round] = {'ability': ability, 'target_seat': target,
                            'target_role': target_role}
                    self.clean_data[role_seat]['actions'] = action_dict


    def parse_day_actions(self, row, round, previous_round):
        # Just use one cell since replica
        descs = row[1].split('，')
        for desc in descs:
            sheriff_match = re.search(r'(\d+)警长', desc)
            if sheriff_match:
                player = int(sheriff_match.group(1))
                self.clean_data[player]['badge'] = round
                continue

            banish_match = re.search(r'(\d+)出局', desc)
            if banish_match:
                target = int(banish_match.group(1))
                self.clean_data[target]['death_round'] = round
                self.clean_data[target]['death_method'] = '放逐'
                continue
            
            shot_match = re.search(r'(\d+)\w*枪杀(\d+)', desc)
            if shot_match:
                source = int(shot_match.group(1))
                target = int(shot_match.group(2))
                target_role = self.clean_data[target]['role']
                self.clean_data[target]['death_round'] = round
                self.clean_data[target]['death_method'] = '枪杀'
                action_dict = self.clean_data[source].get('actions', {})
                action_dict[round] = {'ability': '枪杀', 'target_seat': target,
                    'target_role': target_role}
                self.clean_data[source]['actions'] = action_dict
                continue

            explode_match = re.search(r'(\d+)\S*自爆', desc)
            if explode_match:
                player = int(explode_match.group(1))
                self.clean_data[player]['death_round'] = round
                self.clean_data[player]['death_method'] = '自爆'
            
            love_match = re.search(r'(\d+)\S*殉情', desc)
            if love_match:
                player = int(love_match.group(1))
                self.clean_data[player]['death_round'] = round
                self.clean_data[player]['death_method'] = '殉情'
            
            death_match = re.search('(\S+)[双,三,四,五]?死', desc)
            if death_match:
                text = re.sub('\D+', ' ', death_match.group(1))
                death_targets = [int(s) for s in text.split()]
                for t in death_targets:
                    death_method = self.night_deaths[previous_round][t]
                    self.clean_data[t]['death_round'] = previous_round
                    self.clean_data[t]['death_method'] = death_method

    
    def parse(self):
        self.parse_name_seat()
        self.parse_vote_results()

        previous_round = None
        num_round = self.action_df.shape[0]
        for i in range(1, num_round):
            row = self.action_df.loc[i]
            # NOTE: I know this header is weird, blame pandas
            round = row['角色']
            if '夜' in round:
                self.parse_night_actions(round, row)
            elif '天' in round:
                self.parse_day_actions(row, round, previous_round)
            else:
                raise ValueError(round)

            previous_round = round
        
        return self.clean_data
