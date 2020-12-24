from abc import ABC
import re


CHINESE_NUMBER_DICT = {
    1: '一',
    2: '二',
    3: '三',
    4: '四',
    5: '五',
    6: '六',
    7: '七',
    8: '八',
    9: '九'
}

NUMBER_CHINESE_DICT = {v: k for k, v in CHINESE_NUMBER_DICT.items()}



class BaseParserEngine(ABC):

    def __init__(self):
        self.clean_data = {}
        self.role_map = {}

        # to identify death method, since one person could
        # be hunted and poisoned
        self.deadly_abilities = ['毒杀', '猎杀']
        self.night_deaths = {}
        self.checkable_werewolf_roles = ['狼人']  # used for seer's check
        self.checkable_werewolf_seats = []
        self.werewolf_group_roles = ['狼人']  # used to determine hunting
        self.werewolf_group_seats = []
        self.werewolf_camp_roles = ['狼人']  # used to determine victory camp
        self.werewolf_camp_seats = []
        self.no_target_ability = []

    def read_data(self, action_df, vote_df):
        self.action_df = action_df
        self.vote_df = vote_df
        # some actions are conducted as a team so we also
        # need the raw roles
        self.raw_roles = [r for r in list(action_df.columns)[1:] if r != '-']

    def _get_previous_round(self, round):
        # NOTE: use negative number in case of missing leading "第"
        if round[-1] == '天':
            previous_round = f"{round[:-1]}夜"
        elif round[-1] == '夜':
            num_char = round[-2]
            previous_char = CHINESE_NUMBER_DICT[NUMBER_CHINESE_DICT[num_char] - 1]
            previous_round = f"{round[:-2]}{previous_char}天"
        else:
            raise ValueError(f"Invalid round {round}")
        return previous_round

    def _parse_general_action(self, action_text):
        match = re.search("\d+", action_text)
        if match:
            target = int(match.group(0))
        else:
            target = None
        return target

    def _parse_werewolf_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '猎杀'
        return (ability, target)
    
    def _parse_seer_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '查验'
        return (ability, target)
    
    def _parse_hunter_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '枪杀'
        return (ability, target)
    
    def _parse_witch_action(self, action_text):
        match = re.search(r"(\D+)(\d+)", action_text)
        if match:
            if '救' in match.group(1):
                ability = "解救"
            elif '毒' in match.group(1):
                ability = "毒杀"
            else:
                raise ValueError(f'{action_text} is not valid for 女巫')
            target = int(match.group(2))
        else:
            ability = "用药"
            target = None
        return (ability, target)

    def _parse_moron_action(self, action_text):
        ability = '神志'
        return (ability, None)
    
    def _parse_guard_action(self, action_text):
        target = self._parse_general_action(action_text)
        ability = '守护'
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
        elif role == '白痴':
            return self._parse_moron_action(action_text)
        else:
            raise ValueError(f'{role} {action_text}')

    def create_role_seat_dict(self):
        roles = self.action_df.loc[0]
        self.role_map = {}
        for i, seats in enumerate(roles):
            if i == 0:
                continue

            role = self.action_df.columns[i]
            # handle special case like ‘狼兄 狼弟’
            if ' ' in role:
                role_names = role.split()
                seat_tokens = seats.split()
                if len(role_names) != len(seat_tokens):
                    raise ValueError('Role size and seat size do not match')
                for r, s in zip(role_names, seat_tokens):
                    self.role_map[r] = int(s)
            elif role == '-':
                continue
            else:
                try:
                    seat = int(seats)
                    cleaned_seat = seat
                except ValueError:
                    tokens = seats.split()
                    cleaned_seat = []
                    for t in tokens:
                        seat = int(t)
                        cleaned_seat.append(seat)
                self.role_map[role] = cleaned_seat

    def parse_name_seat(self):
        names = self.vote_df.loc[0]
        for i, name in enumerate(names):
            if i > 0:
                self.clean_data[i] = {
                    'name': name,
                    'seat': i,
                    'role': '平民',
                    'initial_camp': '好人',
                    'final_camp': '好人'
                } # set default
        
        self.create_role_seat_dict()
        for role, seats in self.role_map.items():
            if not isinstance(seats, list):
                seats = [seats]
            for seat in seats:
                if role in self.werewolf_camp_roles:
                    self.clean_data[seat]['initial_camp'] = '狼人'
                    self.clean_data[seat]['final_camp'] = '狼人'
                if role in self.werewolf_group_roles:
                    self.werewolf_group_seats.append(seat)
                if role in self.checkable_werewolf_roles:
                    self.checkable_werewolf_seats.append(seat)
                self.clean_data[seat]['role'] = role
    
    def parse_vote_results(self):
        previous_round = None
        for i in range(1, self.vote_df.shape[0]):
            row = self.vote_df.loc[i]
            round = row[0]
            if round.lower() == "pk":
                round = f"{previous_round} pk"
            for seat, ballot in enumerate(row):
                if seat == 0:
                    continue
                votes = self.clean_data[seat].get('votes', {})
                votes[round] = ballot
                self.clean_data[seat]['votes'] = votes
            previous_round = round
    
    def _check_result(self, target):
        if target in self.checkable_werewolf_seats:
            return "狼人"
        else:
            return "好人"
    
    def _check_death(self, ability, target, round):
        if ability in self.deadly_abilities:
                method = f"{self.night_deaths[round].get(target, '')} {ability}".strip()
                self.night_deaths[round][target] = method
    
    def _format_ability_results(self, ability, target):
            ability_dict = {
                'ability': ability,
                'target_seat': target,
                'target_role': self.clean_data[target]['role']
            }
            if ability == "查验":
                result = self._check_result(target)
                ability_dict["check_result"] = result
            return ability_dict
    
    def _get_death_info(self, seat):
        data = self.clean_data[seat]
        if "death_round" in data:
            return (data["death_round"], data["death_method"])
        else:
            return (None, None)

    def parse_night_actions(self, round, row):
        self.night_deaths[round] = {}
        for role in self.raw_roles:
            if ' ' in role:
                raise Exception(f'Invalid role: {role}')
            role_seat = self.role_map[role]
            action_text = row[role]
            # find the ability and target of this role
            ability, target = self.format_night_action(action_text, role)
            #NOTE: we don't judge the results here. Simply adding target to night deaths
            self._check_death(ability, target, round)
            if target:
                if not isinstance(role_seat, list):
                    role_seat = [role_seat]
                if role == "狼人":
                    role_seat = self.werewolf_group_seats
                for s in role_seat:
                    death_round, death_method = self._get_death_info(s)
                    if death_round:
                        # self-exploded player could hunt that night
                        if death_method == "自爆":
                            if death_round != self._get_previous_round(round):
                                continue
                        else:
                            continue

                    action_dict = self.clean_data[s].get('actions', {})
                    ability_dict = self._format_ability_results(ability, target)
                    ability_list = action_dict.get(round, [])
                    ability_list.append(ability_dict)
                    action_dict[round] = ability_list
                    self.clean_data[s]['actions'] = action_dict

    def _parse_sheriff(self, match, round):
        player = int(match.group(1))
        self.clean_data[player]['badge'] = round
    
    def _parse_banish(self, match, round):
        target = int(match.group(1))
        self.clean_data[target]['death_round'] = round
        self.clean_data[target]['death_method'] = '放逐'

    def _parse_shot(self, match, round):
        source = int(match.group(1))
        target = int(match.group(2))
        target_role = self.clean_data[target]['role']
        if self.clean_data[source]["death_method"] == "放逐":
            self.clean_data[target]['death_round'] = round
        else:
            previous_round = self._get_previous_round(round)
            self.clean_data[target]['death_round'] = previous_round
        self.clean_data[target]['death_method'] = '枪杀'
        action_dict = self.clean_data[source].get('actions', {})
        action_dict[round] = {'ability': '枪杀', 'target_seat': target,
            'target_role': target_role}
        self.clean_data[source]['actions'] = action_dict

    def _parse_explode(self, match, round):
        player = int(match.group(1))
        self.clean_data[player]['death_round'] = round
        self.clean_data[player]['death_method'] = '自爆'

    def _parse_death(self, match, round):
        text = re.sub('\D+', ' ', match.group(1))
        death_targets = [int(s) for s in text.split()]
        for t in death_targets:
            previous_round = self._get_previous_round(round)
            death_method = self.night_deaths[previous_round][t]
            self.clean_data[t]['death_round'] = previous_round
            self.clean_data[t]['death_method'] = death_method

    def _parse_couple(self, match, round):
        player = int(match.group(1))
        self.clean_data[player]['death_round'] = round
        self.clean_data[player]['death_method'] = '殉情'

    def parse_day_actions(self, row, round):
        # Just use one cell since replica
        regexps = {
            '(\d+)警长': '_parse_sheriff',
            '(\d+)出局': '_parse_banish',
            '(\d+)\w*枪杀(\d+)': '_parse_shot',
            '(\d+)\S*自爆': '_parse_explode',
            '(\S+)[双,三,四,五]?死': '_parse_death',
            '(\d+)\S*殉情': '_parse_couple'
        }
        descs = row[1].split('，')
        for desc in descs:
            for key, value in regexps.items():
                pattern = re.compile(key)
                match = re.search(pattern, desc) 
                if match:
                    func = getattr(self, value)
                    func(match, round)
                    break
            
    def parse(self):
        self.parse_name_seat()
        self.parse_vote_results()

        num_round = self.action_df.shape[0]
        for i in range(1, num_round):
            row = self.action_df.loc[i]
            # NOTE: I know this header is weird, blame pandas
            round = row['角色']
            if '夜' in round:
                self.parse_night_actions(round, row)
            elif '天' in round:
                self.parse_day_actions(row, round)
            else:
                raise ValueError(round)

        return self.clean_data

