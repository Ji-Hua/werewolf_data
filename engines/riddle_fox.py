import re

from .base_parser_engine import BaseParserEngine


class RiddleFoxEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.third_party_roles.append("咒狐")

    def _parse_riddle_fox_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '迷踪'
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
        elif role == "咒狐":
            return self._parse_riddle_fox_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
    
    def _check_death(self, ability, target, round):
        riddle_fox_seat = self.role_map["咒狐"]
        if target == riddle_fox_seat:
            if ability == "查验":
                method = "查验"
                self.night_deaths[round][target] = method
        else:
            if ability in self.deadly_abilities:
                method = f"{self.night_deaths[round].get(target, '')} {ability}".strip()
                self.night_deaths[round][target] = method
    
    def _parse_shot(self, match, round):
        source = int(match.group(1))
        target = int(match.group(2))
        target_role = self.clean_data[target]['role']
        if target_role == "咒狐":
            pass
        else:
            if self.clean_data[source]["death_method"] == "放逐":
                self.clean_data[target]['death_round'] = round
            else:
                previous_round = self._get_previous_round(round)
                self.clean_data[target]['death_round'] = previous_round
            self.clean_data[target]['death_method'] = '枪杀'
        action_dict = self.clean_data[source].get('actions', {})
        action_dict[round] = {'ability': '枪杀', 'target_seat': target,
            'target_role': target_role}
        self.clean_data[source]['actions'] = action_dict 

