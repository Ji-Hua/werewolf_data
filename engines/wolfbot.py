import re

from .base_parser_engine import BaseParserEngine

class WolfbotEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        # to identify death method, since one person could
        # be hunted and poisoned
        self.deadly_abilities = ['毒杀', '猎杀', '毒杀（狼毒）', '猎杀 (双刃）']
        self.checkable_werewolf_roles = ["狼人"]
        self.werewolf_camp_roles.append("机械狼")


    def _parse_wolfbot_action(self, action_text):
        regexps = {
            '学\s*(\d+)': '模仿',
            '毒\s*(\d+)': '毒杀（狼毒）',
            '守\s*(\d+)': '守护（狼盾）',
            '验\s*(\d+)': '查验（狼预）',
            '刀\s*(\d+)': '猎杀'
        }
        for key, value in regexps.items():
            pattern = re.compile(key)
            match = re.search(pattern, action_text) 
            if match:
                ability = value
                target = int(match.group(1))
            else:
                ability = None
                target = None
            return (ability, target)
    
    def _parse_medium_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '查验'
        return (ability, target)
    
    def _check_result(self, target):
        target_role = self.clean_data[target]['role']
        if target_role == "机械狼":
            mock_role = "机械狼"
            for action in self.clean_data[target]["actions"].values():
                for ability in action:
                    if "模仿" in ability.values():
                        # NOTE: we always check this after "模仿"
                        mock_role = ability["target_role"]
            return mock_role
        else:
            return target_role
    
    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == "女巫":
            return self._parse_witch_action(action_text)
        elif role == "通灵师":
            return self._parse_medium_action(action_text)
        elif role == "猎人":
            return self._parse_hunter_action(action_text)
        elif role == "守卫":
            return self._parse_guard_action(action_text)
        elif role == "机械狼":
            return self._parse_wolfbot_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')

    def _parse_shot(self, match, round):
        source = int(match.group(1))
        target = int(match.group(2))
        source_role = self.clean_data[source]['role']
        if source_role == '猎人':
            ability = '枪杀'
        elif source_role == '机械狼':
            ability = '枪杀（狼枪）'
        else:
            raise ValueError(f"Invalid role {source_role} to shoot")

        target_role = self.clean_data[target]['role']
        self.clean_data[target]['death_round'] = round
        self.clean_data[target]['death_method'] = ability
        action_dict = self.clean_data[source].get('actions', {})
        action_dict[round] = {'ability': ability, 'target_seat': target,
            'target_role': target_role}
        self.clean_data[source]['actions'] = action_dict
