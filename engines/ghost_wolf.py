import re

from .base_parser_engine import BaseParserEngine


class GhostWolfEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "鬼狼"]
        self.werewolf_group_roles.append("鬼狼")
        self.werewolf_camp_roles.append("鬼狼")

    def _parse_ghost_wolf_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '阴魂'
        return (ability, target)
    
    def _parse_bewitcher_action(self, action_text):
        if action_text == "补药":
            ability = "补药"
            target = self.role_map["女巫"]
        else:
            target = self._parse_general_action(action_text)
            ability = "蛊惑"
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
        elif role == "蛊惑师":
            return self._parse_bewitcher_action(action_text)
        elif role == "鬼狼":
            return self._parse_ghost_wolf_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')