import re

from .base_parser_engine import BaseParserEngine


class StormWolfEngine(BaseParserEngine):
    def __init__(self):
        super().__init__()
        self.checkable_werewolf_roles = ["狼人", "雪狼"]
        self.werewolf_camp_roles = ["狼人", "雪狼"]
        self.storm = False

    def _parse_storm_wolf_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '猎杀'
        return (ability, target)
    
    def _special_werewolf_action(self, ability, target, round):
        source_seat = self.role_map["雪狼"]
        self.werewolf_group_seats.append(source_seat)

    def _parse_duke_action(self, action_text):
        return ("裁决", None)
    
    def _parse_extra_day_info(self, descs, round):
        # check storm wolf
        pattern = re.compile("(\d+)号?((雪狼)?翻牌|发动技能)")
        match = re.search(pattern, descs)
        if match:
            # check if storm is used
            seat = int(match.group(1))
            if seat == self.role_map["雪狼"]:
                self.storm = True
                actions = self.clean_data[seat].get("actions", {})
                action_list = actions.get(round, [])
                action_list.append({"ability": "风暴"})
                actions[round] = action_list
                self.clean_data[seat]["actions"] = actions
        
        # check duke
        # TODO: consider 警长竞选 and pk
        pattern = re.compile("改(\d+)票\S+(\d+)")
        match = re.search(pattern, descs)
        if match:
            seat = self.role_map["公爵"]
            actions = self.clean_data[seat].get("actions", {})
            action_list = actions.get(round, [])
            action_list.append({
                "ability": "裁决",
                "votes": int(match.group(1)),
                "target": int(match.group(2))
            })
            actions[round] = action_list
            self.clean_data[seat]["actions"] = actions

    
    def format_night_action(self, action_text, role):
        if role == "狼人":
            return self._parse_werewolf_action(action_text)
        elif role == "女巫" and not self.storm:
            return self._parse_witch_action(action_text)
        elif role == "预言家" and not self.storm:
            return self._parse_seer_action(action_text)
        elif role == "猎人" and not self.storm:
            return self._parse_hunter_action(action_text)
        elif role == "公爵" and not self.storm:
            return self._parse_duke_action(action_text)
        elif role == "雪狼" and not self.storm:
            return self._parse_storm_wolf_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')
