from .base_parser_engine import BaseParserEngine


class MixbloodEngine(BaseParserEngine):
    def _parse_mixblood_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '榜样'
        if target:
            target_role = self.clean_data[target]['role']
            if target_role in self.werewolf_camp_roles:
                seat = self.role_map["混血儿"]
                self.clean_data[seat]['final_camp'] = "狼人"
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
        elif role == "白痴":
            return self._parse_moron_action(action_text)
        elif role == "混血儿":
            return self._parse_mixblood_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
