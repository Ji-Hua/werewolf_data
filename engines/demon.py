from .base_parser_engine import BaseParserEngine

class DemonEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "恶魔"]
        self.werewolf_group_roles.append("恶魔")
        self.werewolf_camp_roles.append("恶魔")

    def _parse_demon_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '审判'
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
        elif role == "恶魔":
            return self._parse_demon_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
    
    def _check_judge_result(self, target):
            target_role = self.clean_data[target]['role']
            if target_role in self.checkable_werewolf_roles:
                return "非神"
            elif target_role == "平民":
                return "非神"
            else:
                return "神"

    def _format_ability_results(self, ability, target):
        ability_dict = {
            'ability': ability,
            'target_seat': target,
            'target_role': self.clean_data[target]['role']
        }
        if ability == "查验":
            result = self._check_result(target)
            ability_dict["check_result"] = result

        if ability == '审判':
            result = self._check_judge_result(target)
            ability_dict["check_result"] = result

        return ability_dict
