import re

from .base_parser_engine import BaseParserEngine


class GargoyleGraveyardKeeperEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "石像鬼"]
        self.werewolf_camp_roles = ["狼人", "石像鬼"]

    def _parse_gargoyle_action(self, action_text):
        match = re.search(r'验(\d+)', action_text)
        ability = '魔眼'
        if match:
            target = int(match.group(1))
        else:
            target = None
        return (ability, target)
    
    def _special_werewolf_action(self, ability, target, round):
        source_seat = self.role_map["石像鬼"]
        self.werewolf_group_seats.append(source_seat)

    def _parse_graveyard_keeper_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '盖棺'
        return (ability, target)
    
    def _check_gargoyle_result(self, target):
        target_role = self.clean_data[target]['role']
        return target_role

    def _format_ability_results(self, ability, target):
        ability_dict = {
            'ability': ability,
            'target_seat': target,
            'target_role': self.clean_data[target]['role']
        }
        if ability == "查验":
            result = self._check_result(target)
            ability_dict["check_result"] = result

        if ability == '魔眼':
            result = self._check_gargoyle_result(target)
            ability_dict["check_result"] = result

        return ability_dict
    
    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == "女巫":
            return self._parse_witch_action(action_text)
        elif role == "预言家":
            return self._parse_seer_action(action_text)
        elif role == "猎人":
            return self._parse_hunter_action(action_text)
        elif role == "守墓人":
            return self._parse_graveyard_keeper_action(action_text)
        elif role == "石像鬼":
            return self._parse_gargoyle_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
