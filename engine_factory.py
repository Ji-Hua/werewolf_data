import traceback

from engine_types import EngineTypes


class EngineFactory:

    name_engine_dict = {
        "预女猎白": "Standard",
        "预女猎白混": "Mixblood",
        "梦魇 vs. 预女猎守": "Nightmare",
        "机械狼 vs. 通女猎守": "Wolfbot",
        "魔狼 vs. 预女猎白": "DemonWolf",
        "预女猎妖混": "NineTailsMixblood",
        "黑蝙蝠 vs. 预女猎守": "BlackBat",
        "预女猎孩": "LittleGirl",
    }

    def format_engine_name(self, name):
        """ Translate Chinese name of the template into engine class
        """
        return self.name_engine_dict[name]


    def construct(self, name):
        builder_name = self.format_engine_name(name)
        try:
            target_class = getattr(EngineTypes, builder_name)
            instance = target_class()
            return instance
        except AttributeError:
            print("Builder {} not defined.".format(builder_name))
            traceback.print_stack()
