import re

from .base_parser_engine import BaseParserEngine


class LittleGirlEngine(BaseParserEngine):
    def _parse_little_girl_action(self, action_text):
        match = re.search(r"看\s*(\S+)", action_text)
        ability = '偷看'
        target = None
        if match:
            target = match.group(1)
        return (ability, target)
    
    def _format_ability_results(self, ability, target):
        if ability == '偷看':
            ability_dict = {'ability': ability, 'target': target}
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

    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == '女巫':
            return self._parse_witch_action(action_text)
        elif role == '预言家':
            return self._parse_seer_action(action_text)
        elif role == '猎人':
            return self._parse_hunter_action(action_text)
        elif role == '小女孩':
            return self._parse_little_girl_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')  