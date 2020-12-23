from .base_parser_engine import BaseParserEngine

class NightmareEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.werewolf_camp = ["狼人", "梦魇"]

    def _parse_nightmare_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '恐惧'
        return (ability, target)
    
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
        elif role == "梦魇":
            return self._parse_nightmare_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')  