import re

from .base_parser_engine import BaseParserEngine


# TODO: should add target info as well
class DevilMerchantEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        # to identify death method, since one person could
        # be hunted and poisoned
        self.deadly_abilities = ['毒杀', '猎杀', '毒杀（狼毒）']
        self.checkable_werewolf_roles = ["狼人", "邪恶商人"]
        self.werewolf_group_roles.append("邪恶商人")
        self.werewolf_camp_roles.append("邪恶商人")

    def _parse_devil_merchant_action(self, action_text):
        pattern = re.compile('(\S+)\s*->\s*(\d+)')
        match = re.search(pattern, action_text) 
        if match:
            ability = '交易'
            target = (match.group(1), int(match.group(2)))
        else:
            ability = None
            target = None
        return (ability, target)
    
    def _parse_medium_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '查验'
        return (ability, target)
    
    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == '女巫':
            return self._parse_witch_action(action_text)
        elif role == '预言家':
            return self._parse_medium_action(action_text)
        elif role == '猎人':
            return self._parse_hunter_action(action_text)
        elif role == '守卫':
            return self._parse_guard_action(action_text)
        elif role == "邪恶商人":
            return self._parse_devil_merchant_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')

    def _parse_shot(self, match, round):
        source = int(match.group(1))
        target = int(match.group(2))
        source_role = self.clean_data[source]['role']
        if source_role == '猎人':
            ability = '枪杀'
        elif source_role == '狼人':
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

    def _format_ability_results(self, ability, target):
        if ability == '交易':
            ability_dict = {
                'ability': ability,
                'trade_item': target[0],
                'target_target': target[-1]
            }
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
