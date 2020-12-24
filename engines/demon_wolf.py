from .base_parser_engine import BaseParserEngine

class DemonWolfEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "魔狼"]
        self.werewolf_group_roles.append("魔狼")
        self.werewolf_camp_roles.append("魔狼")

    def _parse_demon_wolf_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '重创'
        return (ability, target)
    
    def _parse_demon_hunter_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '狩猎'
        return (ability, target)
    
    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == '女巫':
            return self._parse_witch_action(action_text)
        elif role == '预言家':
            return self._parse_seer_action(action_text)
        elif role == '猎魔人':
            return self._parse_demon_hunter_action(action_text)
        elif role == '白痴':
            return self._parse_moron_action(action_text)
        elif role == "魔狼":
            return self._parse_demon_wolf_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')