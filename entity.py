from sprite import *
import configparser


class Entity(Sprite):
    def __init__(self, pos=(0, 0), frames=None, name=None):

        parser = configparser.ConfigParser()
        parser.read("entities/" + name + ".entity")
        print(parser.get("entity", "texture"))

        self.key = {}
        for section in parser.sections():
            if not section == "entity":
                desc = dict(parser.items(section))
                self.key[section] = desc
        print(self.key)
