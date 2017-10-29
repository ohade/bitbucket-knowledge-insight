from collections import defaultdict
from loader import Loader


class Engine:
    def __init__(self):
        self._loader = Loader()
        self._tree_dict = self._loader.tree.tree_to_dict()
        self._area_knowledge_list = list()
        self._init_area_knowledge_map()

    def check_person_exist(self, name):
        return self.get_persons_info_by_name(name) != None

    def get_persons_info_by_name(self, name):
        for p in self._loader.persons:
            if p.display_name == name:
                return p
        return None

    def get_persons_for_top_ten_authors(self):
        person_top_ten = list()

        index = 1
        for author_name in self._loader.ordered_authors:
            found = False
            for p in self._loader.persons:
                if p.display_name == author_name:
                    found = True
                    p.place = index
                    p.counter = self._loader.authors[author_name].counter
                    index += 1
                    break
            if found:
                person_top_ten.append(p)
        return person_top_ten

    def get_persons_for_top_ten_approvers(self):
        person_top_ten = list()

        index = 1
        for approver_name in self._loader.ordered_approveres:
            found = False
            for p in self._loader.persons:
                if p.display_name == approver_name:
                    found = True
                    p.place = index
                    p.counter = self._loader.total_pull_requests[approver_name].counter
                    index += 1
                    break
            if found:
                person_top_ten.append(p)
                # if len(person_top_ten) == 10:
                #     break
        return person_top_ten

    def get_by_name_on_a_approvers(self, name):
        return self._loader.approvers.get(name)

    def get_total_number_of_requests(self, name):
        return self._loader.total_pull_requests.get(name)

    def search_by_name_on_a_authors(self, name):
        return self._loader.authors.get(name)

    def get_personal_author_rank(self, name):
        for index, key in enumerate(self._loader.ordered_authors, 1):
            if name and key == name:
                return index

    def get_personal_approver_rank(self, name):
        for index, key in enumerate(self._loader.ordered_approveres, 1):
            if name and key == name:
                return index

    def get_pull_request_responsiveness(self, name):
        person_approved = self.get_by_name_on_a_approvers(name)
        person_total = self.get_total_number_of_requests(name)

        person_approved_ticket_id_len = 0
        person_total_ticket_id_len = 0
        if person_approved and person_approved.tickets_id:
            person_approved_ticket_id_len = sum([len(v) for v in person_approved.tickets_id.values()])
        if person_total and person_total.tickets_id:
            person_total_ticket_id_len = sum([len(v) for v in person_total.tickets_id.values()])

        if person_total_ticket_id_len == 0:
            return 0
        else:
            return int((float(person_approved_ticket_id_len) / person_total_ticket_id_len) * 100)

    def get_personal_map_area_to_counter(self, name):
        res = list()
        res_authored = self.get_personal_map_authored_area_to_counter(name)
        res_approved = self.get_personal_map_approved_area_to_counter(name)
        for key in set(res_authored.keys() + res_approved.keys()):
            res.append(dict(
                area=key,
                author_counter=res_authored[key],
                approve_counter=res_approved[key]))
        return res

    def get_personal_map_authored_area_to_counter(self, name):
        res = defaultdict(int)
        person = self.search_by_name_on_a_authors(name)
        if not person:
            return res
        for (project_name, slug), ticket_ids in person.tickets_id.iteritems():
            for ticket_id in ticket_ids:
                areas = self._loader.id_to_area[(project_name, slug)][ticket_id]
                for area in areas:
                    res[str(area)] += 1
        return res

    def get_personal_map_approved_area_to_counter(self, name):
        res = defaultdict(int)
        person = self.get_by_name_on_a_approvers(name)
        if not person:
            return res

        for (project_name, slug), ticket_ids in person.tickets_id.iteritems():
            for ticket_id in ticket_ids:
                areas = self._loader.id_to_area[(project_name, slug)][ticket_id]
                for area in areas:
                    res[str(area)] += 1
        return res

    def get_tree(self):
        return self._tree_dict

    def _init_area_knowledge_map(self):
        for knowledge_key in self._loader.area_knowledge_map:
            self._area_knowledge_list.append(self._loader.area_knowledge_map[knowledge_key].get_mapping())

    def get_area_knowledge_map(self):
        return self._area_knowledge_list

    def refresh_cache(self):
        self._loader.reload()
