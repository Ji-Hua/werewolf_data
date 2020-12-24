import re

from .base_parser_engine import BaseParserEngine


class BigGreyWolfEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "大灰狼"]
        self.werewolf_camp_roles.append("大灰狼")
        self.deadly_abilities.append("突袭")

    def _format_ability_results(self, ability, target):
        if ability == '锁定':
            if target:
                results = {t: self.clean_data[t]["role"] for t in target}
                ability_dict = {'ability': ability, 'targets': results}
            else:
                raise ValueError(f"Invalid target {target} for {ability}")
        else:
            ability_dict = {
                'ability': ability,
                'target_seat': target,
                'target_role': self.clean_data[target]['role']
            }
            if ability == "查验":
                result = self._check_result(target)
                ability_dict["check_result"] = result
        return ability_dict

    def _parse_big_grey_wolf_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '突袭'
        return (ability, target)
  
    
    def _parse_augur_action(self, action_text):
        match = re.search("锁(\d+)\s(\d+)\s(\d+)", action_text)
        ability = "锁定"
        if match:
            target = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        else:
            target = None
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
        elif role == "占卜师":
            return self._parse_augur_action(action_text)
        elif role == "大灰狼":
            return self._parse_big_grey_wolf_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
