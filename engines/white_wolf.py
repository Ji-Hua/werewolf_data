import re

from .base_parser_engine import BaseParserEngine

# 1127-2
class WhiteWolfEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "白狼王"]
        self.werewolf_group_roles.append("白狼王")
        self.werewolf_camp_roles.append("白狼王")
    
    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == "女巫":
            return self._parse_witch_action(action_text)
        elif role == "预言家":
            return self._parse_seer_action(action_text)
        elif role == "守卫":
            return self._parse_guard_action(action_text)
        elif role == "骑士":
            return None, None
        elif role == "白狼王":
            return None, None
        else:
            raise ValueError(f'{role} {action_text}')
        
    def _parse_whitewolf(self, match, round):
        source = int(match.group(1))
        target = int(match.group(2))
        target_role = self.clean_data[target]['role']

        self.clean_data[target]['death_method'] = '白狼王击杀'
        self.clean_data[target]['death_round'] = round
        action_dict = self.clean_data[source].get('actions', {})
        action_dict[round] = {'ability': '自爆击杀', 'target_seat': target,
            'target_role': target_role}
        self.clean_data[source]['actions'] = action_dict
    
    def _parse_knight(self, match, round):
        source = int(match.group(1))
        target = int(match.group(2))
        target_role = self.clean_data[target]['role']
        
        if target_role == "狼人" or target_role == "白狼王":
            self.clean_data[target]['death_method'] = '骑士决斗击杀'
            self.clean_data[target]['death_round'] = round
        else:
            self.clean_data[source]['death_method'] = '骑士决斗自杀'
            self.clean_data[source]['death_round'] = round
            
        action_dict = self.clean_data[source].get('actions', {})
        action_dict[round] = {'ability': '决斗', 'target_seat': target,
            'target_role': target_role}
        self.clean_data[source]['actions'] = action_dict
