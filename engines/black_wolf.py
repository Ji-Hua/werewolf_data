import re

from .base_parser_engine import BaseParserEngine

# 1127-1
class BlackWolfEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "黑狼王"]
        self.werewolf_group_roles.append("黑狼王")
        self.werewolf_camp_roles.append("黑狼王")
    
    def _parse_magician_action(self, action_text):
        match = re.search("空|不", action_text)
        if match:
            return ("交换", None)
        match = re.findall("\d+", action_text)
        if match:
            return ("交换", [int(t) for t in match])
        return "交换", None
            
    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == "女巫":
            return self._parse_witch_action(action_text)
        elif role == "猎人":
            return self._parse_hunter_action(action_text)
        elif role == "预言家":
            return self._parse_seer_action(action_text)
        elif role == "魔术师":
            return self._parse_magician_action(action_text)
        elif role == "黑狼王":
            return self._parse_hunter_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
        
