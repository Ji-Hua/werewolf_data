import re

from .base_parser_engine import BaseParserEngine


class GhostKnightEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "恶灵骑士"]
        self.werewolf_group_roles.append("恶灵骑士")
        self.werewolf_camp_roles.append("恶灵骑士")
        self.deadly_abilities.append("反噬")

    def _parse_ghost_knight_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '反噬'
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
        elif role == "守卫":
            return self._parse_guard_action(action_text)
        elif role == "恶灵骑士":
            return self._parse_ghost_knight_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
    
    def _parse_death(self, match, round):
        text = re.sub('\D+', ' ', match.group(1))
        death_targets = [int(s) for s in text.split()]
        for t in death_targets:
            previous_round = self._get_previous_round(round)
            death_method = self.night_deaths[previous_round][t]
            self.clean_data[t]['death_round'] = previous_round
            self.clean_data[t]['death_method'] = death_method
