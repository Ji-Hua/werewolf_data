import re

from .base_parser_engine import BaseParserEngine


class StudWolfMysticWolfEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "种狼"]
        self.werewolf_group_roles.append("种狼")

    def _format_ability_results(self, ability, target):
        if ability == '变狼':
            ability_dict = {'ability': ability}
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

    def _parse_rogue_action(self, action_text):
        if action_text == "变狼":
            ability = "变身"
            rogue_seat = self.role_map["野孩子"]
            self.clean_data[rogue_seat]['final_camp'] = '狼人'
            self.werewolf_group_seats.append(rogue_seat)
            target = rogue_seat
        else:
            target = self._parse_general_action(action_text)
            ability = '榜样'
            self.model_seat = target
        return (ability, target)
    
    def _format_ability_results(self, ability, target):
        if ability == '变身':
            death_round, _ = self._get_death_info(self.model_seat)
            ability_dict = {'ability': ability, 'round': death_round}
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
        elif role == '守卫':
            return self._parse_guard_action(action_text)
        elif role == "野孩子":
            return self._parse_rogue_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')

    def _check_result(self, target):
        target_role = self.clean_data[target]['role']
        if target_role == "野孩子":
            death_round, _ = self._get_death_info(self.model_seat)
            if death_round and death_round[-1] == "天":
                return "狼人"
            else:
                return "好人"
        else:
            target_role = self.clean_data[target]['role']
            if target_role in self.werewolf_camp:
                return "狼人"
            else:
                return "好人"