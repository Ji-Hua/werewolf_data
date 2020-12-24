from .base_parser_engine import BaseParserEngine


class WolfBeautyMonkEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "狼美人"]
        self.werewolf_group_roles.append("狼美人")
        self.werewolf_camp_roles.append("狼美人")
        self.deadly_abilities.append("魅惑")

    def _parse_monk_action(self, action_text):
        ability = '负伤'
        return (ability, None)
    
    def _parse_wolf_beauty_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '魅惑'
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
        elif role == "武僧":
            return self._parse_monk_action(action_text)
        elif role == "狼美人":
            return self._parse_wolf_beauty_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
