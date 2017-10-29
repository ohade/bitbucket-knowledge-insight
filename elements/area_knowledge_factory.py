from collections import defaultdict
from elements.area_knowledge import AreaKnowledge


class AreaKnowledgeFactory:
    def __init__(self):
        pass

    @staticmethod
    def update_or_add(area_knowledge_map, result, people_names):
        path = ""
        for r in result:
            path += "," + r
            path = path.strip(',')
            area_knowledge_map[path].set_text(path)
            area_knowledge_map[path].add_people_names(people_names)

    @staticmethod
    def update_photo(area_knowledge_map, persons):
        for area_knowledge in area_knowledge_map.values():
            area_knowledge.update_people_photos(persons)

    @staticmethod
    def create_empty():
        return defaultdict(lambda: AreaKnowledge())
