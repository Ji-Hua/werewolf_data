import re

from .base_parser_engine import BaseParserEngine


class MysticWolfCrowEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "隐狼"]
        self.werewolf_camp_roles = ["狼人", "隐狼"]
        self.deadly_abilities.append('猎杀（觉醒）')

    def _parse_mystic_wolf_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '猎杀（觉醒）'
        return (ability, target)
    
    def _parse_crow_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '诅咒'
        return (ability, target)
    
    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == "女巫":
            return self._parse_witch_action(action_text)
        elif role == "预言家":
            return self._parse_seer_action(action_text)
        elif role == "猎人":
            return self._parse_hunter_action(action_text)
        elif role == "乌鸦":
            return self._parse_crow_action(action_text)
        elif role == "隐狼":
            return self._parse_mystic_wolf_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
