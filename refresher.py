import json
import subprocess
import cPickle as pickle
from datetime import datetime
from collections import defaultdict

from elements.info import Info
from elements.tree_factory import TreeFactory
from elements.area_knowledge_factory import AreaKnowledgeFactory
import connection_info as conn_info

bitbucket_prefix = "curl --silent -u {name}:{password} {path}/rest/api/1.0/".format(
    name=conn_info.user_name,
    password=conn_info.password,
    path=conn_info.bitbucket_path
)
bitbucket_suffix = "?limit=100&start="


# for pickle only
def for_pickle_only():
    return defaultdict(set)


class Refresher(object):
    ignore_component = set()

    def __init__(self):
        self._project_names = list()
        self._project_to_repos = defaultdict(list)

        self._bad_pull_request = set()
        self._good_pull_request = set()
        self._id_to_area = defaultdict(for_pickle_only)
        self._area_to_id = defaultdict(set)
        self._area_to_people = defaultdict(set)

        self._full_ticket_info = defaultdict(list)
        self._ticket_ids = defaultdict(set)

        self._authors = defaultdict(Info)
        self._id_to_authors_people = defaultdict(for_pickle_only)

        self._approvers = defaultdict(Info)
        self._un_approvers = defaultdict(Info)
        self._total_pull_requests = defaultdict(Info)
        self._id_to_people = defaultdict(for_pickle_only)
        self._ordered_approveres = list()
        self._ordered_authors = list()

        self._tree = None
        self._area_knowledge_map = AreaKnowledgeFactory.create_empty()

        self._persons = set()
        self._persons_name = set()
        self._init_all()

    def _init_all(self):
        start_time = datetime.now()
        print "Warming Cache"
        print "In update_project"
        self._update_project()
        print "In _init_tickets_cache"
        self._init_tickets_cache()
        print "In _extract_all_ticket_ids"
        self._extract_all_ticket_ids()
        print "In _extract_all_info_on_authors"
        self._extract_all_info_on_authors()
        print "In _extract_all_info_on_reviewers"
        self._extract_all_info_on_reviewers()
        print "In _order_approveres_init"
        self._order_approveres_init()
        print "In _order_authors_init"
        self._order_authors_init()
        print "In _create_knowledge_mapping_product"
        self._create_knowledge_mapping_product()
        print "In _update_personal_info"
        self._update_personal_info()
        print "In update photo"
        self._update_photo()
        self._dump_to_file()

        print('Time elpased (hh:mm:ss.ms) {}'.format(datetime.now() - start_time))

    def _init_tickets_cache(self):
        for project_name, slugs in self._project_to_repos.iteritems():
            for slug in slugs:
                result = list()
                print "In: " + project_name + ", repo: " + slug
                bitbucket_query = bitbucket_prefix + "projects/" + project_name + "/repos/" + slug + "/pull-requests?state=ALL&order=NEWEST&limit=100&start={}"
                self._bitbucket_caller(bitbucket_query, self._ticket_update, result, True)
                self._full_ticket_info[(project_name, slug)] = result

    def _extract_all_ticket_ids(self):
        for (project_name, slug), result_list in self._full_ticket_info.iteritems():
            for res in result_list:
                for y in res['values']:
                    self._ticket_ids[(project_name, slug)].add(y['id'])

    def _extract_all_info_on_authors(self):
        for (project_name, slug), result_list in self._full_ticket_info.iteritems():
            for res in result_list:
                for y in res['values']:
                    name = y['author']['user']['displayName']
                    if name == "Builder":
                        continue
                    self._authors[name].name = name
                    self._authors[name].counter += 1
                    self._authors[name].tickets_id[(project_name, slug)].add(y['id'])
                    self._id_to_authors_people[(project_name, slug)][y['id']].add(name)
                    self._persons_name.add(name)

    def _extract_all_info_on_reviewers(self):
        for (project_name, slug), result_list in self._full_ticket_info.iteritems():
            for res in result_list:
                for y in res['values']:
                    author = y['author']['user']['displayName']
                    if(author == "Builder"):
                        continue
                    for z in y['reviewers']:
                        name = z['user']['displayName']
                        if(not z['approved']):
                            self._un_approvers[z['user']['displayName']].name = name
                            self._un_approvers[z['user']['displayName']].counter += 1
                            self._un_approvers[z['user']['displayName']].tickets_id[(project_name, slug)].add(y['id'])
                        if(z['approved']):
                            self._approvers[z['user']['displayName']].name = name
                            self._approvers[z['user']['displayName']].counter += 1
                            self._approvers[z['user']['displayName']].tickets_id[(project_name, slug)].add(y['id'])
                        self._id_to_people[(project_name, slug)][y['id']].add(name)
                        self._total_pull_requests[z['user']['displayName']].name = name
                        self._total_pull_requests[z['user']['displayName']].counter += 1
                        self._total_pull_requests[z['user']['displayName']].tickets_id[(project_name, slug)].add(y['id'])
                        self._persons_name.add(name)

    def _order_approveres_init(self):
        for index, (key, value) in enumerate(sorted(self._total_pull_requests.items(), key=lambda x: x[1].counter, reverse=True), 1):
            self._ordered_approveres.append(key)

    def _order_authors_init(self):
        for index, (key, value) in enumerate(sorted(self._authors.items(), key=lambda x: x[1].counter, reverse=True), 1):
            self._ordered_authors.append(key)

    def _create_knowledge_mapping_product(self):
        project_trees = list()
        for project_name, slugs in self._project_to_repos.iteritems():
            slugs_trees = list()
            for slug in slugs:
                trees = list()
                bitbucket_query = bitbucket_prefix + "projects/" + project_name + "/repos/" + slug + "/pull-requests/{}/diff"
                path_prefix_list = ["Root", project_name, slug]
                print "project_slugs_path:", (project_name, slug)
                project_slugs_ticket_ids = self._ticket_ids[(project_name, slug)]
                self._create_knowledge_mapping_assist(project_name, slug, project_slugs_ticket_ids, bitbucket_query, trees, path_prefix_list)
                slugs_trees.append(TreeFactory.set_root(slug, trees))
            project_trees.append(TreeFactory.set_root(project_name, slugs_trees))
        self._tree = TreeFactory.set_root("Root", project_trees)

    def _create_knowledge_mapping_assist(self, project_path, slug_path, ticket_ids, bitbucket_query_format, trees, path_prefix_list):
        tree = None
        print "Amount of ticket_ids: " + str(len(ticket_ids))
        for index, pull_id in enumerate(ticket_ids):
            if(project_path, slug_path, pull_id) in self._bad_pull_request:
                continue
            if(project_path, slug_path, pull_id) in self._good_pull_request:
                continue
            if index and index % 50 == 0:
                print(index)
            bitbucket_query = bitbucket_query_format.format(pull_id)
            curr_res, error = subprocess.Popen(bitbucket_query.split(), stdout=subprocess.PIPE).communicate()
            try:
                x = json.loads(curr_res)
                x['diffs']
            except:
                print("could not work on pull request id:", str(pull_id))
                self._bad_pull_request.add((project_path, slug_path, pull_id))
                continue

            flag_good_pull_request = False
            for d in x['diffs']:
                source = None
                if(d['destination']):
                    source = d['destination']
                elif(d['source']):
                    source = d['source']
                else:
                    print(d)
                    print("skipped")
                    continue

                hi_level_component_name = source['components'][0]
                if hi_level_component_name in self.ignore_component:
                    continue

                flag_good_pull_request = True

                result = self.manipulate_code_display(source['components'])

                tree = TreeFactory.connect_tree(tree, TreeFactory.get_tree(result))

                AreaKnowledgeFactory.update_or_add(self._area_knowledge_map, path_prefix_list + result, self._id_to_people[(project_path, slug_path)][pull_id])
                self._id_to_area[(project_path, slug_path)][pull_id].add(project_path + "." + slug_path + "." + hi_level_component_name)

                self._area_to_id[hi_level_component_name].add(pull_id)
                self._area_to_people[hi_level_component_name].update(self._id_to_people[(project_path, slug_path)][pull_id])
            if not flag_good_pull_request:
                self._bad_pull_request.add((project_path, slug_path, pull_id))
                print("bad_pull_request:", len(self._bad_pull_request))
            else:
                self._good_pull_request.add((project_path, slug_path, pull_id))

        if tree:
            print "Got " + str(len(tree))+ " Trees"
            trees.extend(tree)
        else:
            print "Tree is EMPTY"

    def _update_personal_info(self):
        # id_to_area: pull_id -> hi level component name -> set of more low level
        # area_to_id: hi level component name -> set of pull_id
        # id_to_people: pull_id -> set of names
        # area_to_people: component name -> set of names
        for (project_path, slug_path), ticket_id_names in self._id_to_people.items():
            for ticket_id, names in ticket_id_names.items():
                for name in names:
                    areas = list(self._id_to_area[(project_path, slug_path)][ticket_id])
                    if self._approvers.get(name):
                        self._approvers[name].areas.update(areas)
                    if self._un_approvers.get(name):
                        self._un_approvers[name].areas.update(areas)
                    if self._total_pull_requests.get(name):
                        self._total_pull_requests[name].areas.update(areas)
                    if self._authors.get(name):
                        self._authors[name].areas.update(areas)

    def _update_photo(self):
        self._persons = self.supply_persons_for_update_photo();
        AreaKnowledgeFactory.update_photo(self._area_knowledge_map, self._persons)
        self._area_knowledge_map = dict(self._area_knowledge_map)

    def _bitbucket_caller(self, url, result_updater, result, check_here=False):
        index = 0
        total_size=0
        next_page_start=0
        is_last_page=False

        while not is_last_page:
            bitbucket_query = url.format(next_page_start)
            curr_res, error = subprocess.Popen(bitbucket_query.split(), stdout=subprocess.PIPE).communicate()

            try:
                res_json = json.loads(curr_res)
            except:
                print "Problem with " + curr_res

            # used to take only the ticket up to a specific date
            ###################
            if check_here:
                values = res_json.get('values', None)
                new_values = []
                if values:
                    for v in values:
                        created_date = v.get('createdDate', None)
                        if created_date and created_date < 1508619600000:
                            pass
                        else:
                            new_values.append(v)
                    res_json['values'] = new_values
            ###################

            result_updater(result, res_json)

            is_last_page = res_json.get('isLastPage', False)
            next_page_start = res_json.get('nextPageStart', 0)
            my_size = res_json.get('size', 0)
            index += 1
            total_size += my_size
            print(index, is_last_page, next_page_start, total_size)

    def _project_update(self, project_names, res_json):
        project_names_curr = [project['key'] for project in res_json['values']]
        project_names.extend(project_names_curr)

    def _slug_update(self, repos, res_json):
        slug_names = [slug['slug'] for slug in res_json['values']]
        repos.extend(slug_names)

    def _update_project(self):
        url = "projects"
        url = bitbucket_prefix + url + bitbucket_suffix + "{}"
        self._bitbucket_caller(url, self._project_update, self._project_names)

        for project_name in self._project_names:
            url = "projects/" + project_name + "/repos"
            url = bitbucket_prefix + url + bitbucket_suffix + "{}"
            repos = list()
            self._bitbucket_caller(url, self._slug_update, repos)
            self._project_to_repos[project_name] = repos

    def _ticket_update(self, full_ticket_info_list, res_json):
        full_ticket_info_list.append(res_json)

    def manipulate_code_display(self, source):
        return source

    def supply_persons_for_update_photo(self):
        return list()

    def _dump_to_file(self):
        pickle.dump(self._bad_pull_request, open("./pickles/bad_pull_request.pkl", "wb"))
        pickle.dump(self._good_pull_request, open("./pickles/good_pull_request.pkl", "wb"))
        pickle.dump(self._id_to_area, open("./pickles/id_to_area.pkl", "wb"))
        pickle.dump(self._area_to_id, open("./pickles/area_to_id.pkl", "wb"))
        pickle.dump(self._area_to_people, open("./pickles/area_to_people.pkl", "wb"))

        pickle.dump(self._full_ticket_info, open("./pickles/full_ticket_info.pkl", "wb"))
        pickle.dump(self._ticket_ids, open("./pickles/ticket_ids.pkl", "wb"))

        pickle.dump(self._authors, open("./pickles/authors.pkl", "wb"))
        pickle.dump(self._id_to_authors_people, open("./pickles/id_to_authors_people.pkl", "wb"))

        pickle.dump(self._approvers, open("./pickles/approvers.pkl", "wb"))
        pickle.dump(self._un_approvers, open("./pickles/un_approvers.pkl", "wb"))
        pickle.dump(self._total_pull_requests, open("./pickles/total_pull_requests.pkl", "wb"))
        pickle.dump(self._id_to_people, open("./pickles/id_to_people.pkl", "wb"))
        pickle.dump(self._ordered_approveres, open("./pickles/ordered_approveres.pkl", "wb"))
        pickle.dump(self._ordered_authors, open("./pickles/ordered_authors.pkl", "wb"))
        pickle.dump(self._tree, open("./pickles/tree.pkl", "wb"))
        pickle.dump(self._persons, open('./pickles/persons.pkl', 'wb'))
        pickle.dump(self._area_knowledge_map, open("./pickles/area_knowledge_map.pkl", "wb"))


if __name__ == "__main__":
    r = Refresher()
