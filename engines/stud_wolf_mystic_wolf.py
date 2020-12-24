import re

from .base_parser_engine import BaseParserEngine


class StudWolfMysticWolfEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "种狼"]
        self.werewolf_group_roles.append("种狼")
        self.werewolf_camp_roles = ["狼人", "种狼", "隐狼"]

    def _format_ability_results(self, ability, target):
        if ability == '感染':
            if target:
                ability_dict = {'ability': ability, 'result': target}
                actions = list(self.clean_data[self.role_map["种狼"]]["actions"].values())
                target_seat = actions[-1][0]["target_seat"]
                ability_dict["target"] = target_seat
                if target == '成功':
                    self.clean_data[target_seat]["final_camp"] = "狼人"
                    self.werewolf_camp_seats.append(target_seat)
                    self.werewolf_group_seats.append(target_seat)
                    self.checkable_werewolf_seats.append(target_seat)
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

    def _parse_stud_wolf_action(self, action_text):
        action_text = action_text.strip()
        if action_text == "感染成功":
            ability = "感染"
            target = "成功"  # need to be non-None value
        elif action_text == "感染失败":
            ability = "感染"
            target = "失败"  # need to be non-None value
        else:
            ability = "感染"
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
        elif role == "守卫":
            return self._parse_guard_action(action_text)
        elif role == "种狼":
            return self._parse_stud_wolf_action(action_text)
        elif role == "隐狼":
            return (None, None)
        else:
            raise ValueError(f'{role} {action_text}')
