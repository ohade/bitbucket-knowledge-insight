import cPickle as pickle


class Loader:
    def __init__(self):
        self.bad_pull_request = None
        self.good_pull_request = None
        self.id_to_area = None
        self.area_to_id = None
        self.area_to_people = None

        self.full_ticket_info = None
        self.ticket_ids = None
        self.authors = None
        self.id_to_authors_people = None

        self.approvers = None
        self.un_approvers = None
        self.total_pull_requests = None
        self.id_to_people = None
        self.ordered_approveres = None
        self.ordered_authors = None

        self.persons = None
        self.tree = None
        self.area_knowledge_map = None

        print "Loading cache"
        self._load()

    def _load(self):
        self.bad_pull_request = pickle.load(open("./pickles/bad_pull_request.pkl", "rb"))
        self.good_pull_request = pickle.load(open("./pickles/good_pull_request.pkl", "rb"))
        self.id_to_area = pickle.load(open("./pickles/id_to_area.pkl", "rb"))
        self.area_to_id = pickle.load(open("./pickles/area_to_id.pkl", "rb"))
        self.area_to_people = pickle.load(open("./pickles/area_to_people.pkl", "rb"))

        self.full_ticket_info = pickle.load(open("./pickles/full_ticket_info.pkl", "rb"))
        self.ticket_ids = pickle.load(open("./pickles/ticket_ids.pkl", "rb"))
        self.authors = pickle.load(open("./pickles/authors.pkl", "rb"))
        self.id_to_authors_people = pickle.load(open("./pickles/id_to_authors_people.pkl", "rb"))

        self.approvers = pickle.load(open("./pickles/approvers.pkl", "rb"))
        self.un_approvers = pickle.load(open("./pickles/un_approvers.pkl", "rb"))
        self.total_pull_requests = pickle.load(open("./pickles/total_pull_requests.pkl", "rb"))
        self.id_to_people = pickle.load(open("./pickles/id_to_people.pkl", "rb"))
        self.ordered_approveres = pickle.load(open("./pickles/ordered_approveres.pkl", "rb"))
        self.ordered_authors = pickle.load(open("./pickles/ordered_authors.pkl", "rb"))
        self.persons = pickle.load(open("./pickles/persons.pkl", "rb"))
        self.tree = pickle.load(open("./pickles/tree.pkl", "rb"))
        self.area_knowledge_map = pickle.load(open("./pickles/area_knowledge_map.pkl", "rb"))

    def reload(self):
        print "Refreshing cache"
        self._load()
