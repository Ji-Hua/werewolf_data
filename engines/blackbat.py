import re

from .base_parser_engine import BaseParserEngine


class BlackBatEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.werewolf_camp = ["狼人", "黑蝙蝠"]
        self.protection = True

    def _parse_blackbat_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '庇护'
        return (ability, target)
    
    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == '女巫':
            return self._parse_witch_action(action_text)
        elif role == '预言家':
            return self._parse_seer_action(action_text)
        elif role == '猎人':
            return self._parse_hunter_action(action_text)
        elif role == '守卫':
            return self._parse_guard_action(action_text)
        elif role == "黑蝙蝠":
            return self._parse_blackbat_action(action_text)
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
    
    def _check_deadth(self, ability, target, round):
        if ability in self.deadly_abilities:
                method = f"{self.night_deaths[round].get(target, '')} {ability}".strip()
                self.night_deaths[round][target] = method
        if ability in ["毒杀", "守护"] and self.protection:
            bat_seat = self.role_map["黑蝙蝠"]
            bat_target = self.clean_data[bat_seat]["actions"][round]["target_seat"]
            if target == bat_target:
                method = "反噬（庇护）"
                method = f"{self.night_deaths[round].get(target, '')} {method}".strip()
                if ability == "守护": 
                    self.night_deaths[round][self.role_map["守卫"]] = method
                    self.protection = False
                elif ability == "毒杀":
                    self.night_deaths[round][self.role_map["女巫"]] = method
                    self.protection = False
