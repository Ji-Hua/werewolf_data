from .base_parser_engine import BaseParserEngine

class NineTailsMixbloodEngine(BaseParserEngine):
    def _parse_mixblood_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '榜样'
        return (ability, target)
    
    def _parse_ninetails_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '尾巴'
        return (ability, target)
    
    def _format_ability_results(self, ability, target):
        if ability == '尾巴':
            ability_dict = {'ability': ability, 'number': target}
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
        elif role == '九尾妖狐':
            return self._parse_ninetails_action(action_text)
        elif role == "混血儿":
            return self._parse_mixblood_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
