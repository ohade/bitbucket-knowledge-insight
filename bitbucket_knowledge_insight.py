from flask import Flask, render_template, make_response
from flask_session import Session
from flask import request, redirect
from engine import Engine
import json
from refresher import for_pickle_only

counter = 0
app = Flask(__name__)
# app.debug = True

search_engine = Engine()


@app.route('/refreshCache')
def refresh_cache():
    search_engine.refresh_cache()
    return render_template('welcome.html')


@app.route('/getSearchByPerson/<searched_name>')
def search_by_person_res_get(searched_name):
    return search_by_person_res_asssit(searched_name)


@app.route('/getSearchByPerson/', methods=['POST'])
def search_by_person_res():
    searched_name = request.form['searched_name']
    return search_by_person_res_asssit(searched_name)


def search_by_person_res_asssit(searched_name):
    area_to_counter = search_engine.get_personal_map_area_to_counter(searched_name)
    found = True
    if not area_to_counter:
        found = False

    person = search_engine.get_persons_info_by_name(searched_name)
    responsiveness = search_engine.get_pull_request_responsiveness(searched_name)
    photo_id = person.photo_id if person else None

    my_name = request.cookies.get('code_insight_user')
    my_person = search_engine.get_persons_info_by_name(my_name)

    return render_template('searchByPerson.html',
                           my_name=my_name,
                           my_photo_id=my_person.photo_id,
                           searched_name=searched_name,
                           area_to_counter=area_to_counter,
                           found=found,
                           photo_id=photo_id,
                           responsiveness=responsiveness)


@app.route('/getSearchByPerson')
def search_by_person():
    my_name = request.cookies.get('code_insight_user')
    my_person = search_engine.get_persons_info_by_name(my_name)
    return render_template('searchByPerson.html',
                           found=False,
                           my_name=my_name,
                           my_photo_id=my_person.photo_id)


@app.route('/getTopContributors')
def get_top_contributors():
    my_name = request.cookies.get('code_insight_user')
    persons = search_engine.get_persons_for_top_ten_authors()

    person_list = list()
    for p in persons:
        person_list.append(dict(
            place=p.place,
            counter=p.counter,
            display_name=p.display_name,
            photo_id=p.photo_id
        ))

    my_person = search_engine.get_persons_info_by_name(my_name)

    return render_template(
        'topContributors.html',
        my_name=my_name,
        my_photo_id=my_person.photo_id,
        persons=person_list)


@app.route('/getTopPullRequesters')
def get_top_pull_requesters():
    my_name = request.cookies.get('code_insight_user')
    persons = search_engine.get_persons_for_top_ten_approvers()
    my_person = search_engine.get_persons_info_by_name(my_name)

    person_list = list()
    for p in persons:
        person_list.append(dict(
            place=p.place,
            counter=p.counter,
            display_name=p.display_name,
            photo_id=p.photo_id
        ))

    return render_template(
        'topPullRequesters.html',
        my_name=my_name,
        my_photo_id=my_person.photo_id,
        persons=person_list)


@app.route('/getSearchByArea')
def search_by_area():
    my_name = request.cookies.get('code_insight_user')
    my_person = search_engine.get_persons_info_by_name(my_name)
    return render_template('searchByArea.html',
                           tree_view=safe_json_dumps(search_engine.get_tree()),
                           area_knowledge_map=search_engine.get_area_knowledge_map(),
                           my_photo_id=my_person.photo_id,
                           my_name=my_name)


@app.route('/getHeatmap')
def heatmap():
    my_name = request.cookies.get('code_insight_user')
    my_person = search_engine.get_persons_info_by_name(my_name)
    return render_template('heatmap.html',
                           my_photo_id=my_person.photo_id,
                           my_name=my_name)


@app.route('/getFaq')
def faq():
    my_name = request.cookies.get('code_insight_user')
    my_person = search_engine.get_persons_info_by_name(my_name)
    return render_template('faq.html',
                           my_photo_id=my_person.photo_id,
                           my_name=my_name)


@app.route('/')
def index():
    return render_template('welcome.html',
                           show_error="")


@app.route('/error')
def index_error():
    return render_template('welcome.html',
                           show_error="show_error")


@app.route('/getMyPage')
@app.route('/getMyPage/', methods=['POST'])
def my_page():
    my_name = None
    try:
        my_name = request.form['my_name']
    except:
        print "No Form"

    if not my_name:
        my_name = request.cookies.get('code_insight_user')

    if not my_name or (my_name and not search_engine.check_person_exist(my_name)):
        return redirect('/error')

    author_rank = safe_json_dumps(search_engine.get_personal_author_rank(my_name))

    approval_rank = safe_json_dumps(search_engine.get_personal_approver_rank(my_name))

    author_stats = search_engine.search_by_name_on_a_authors(my_name)
    authored = None
    if author_stats:
        authored = safe_json_dumps(author_stats.counter)

    approved_stats = search_engine.get_by_name_on_a_approvers(my_name)
    approved = None
    if approved_stats:
        approved = safe_json_dumps(approved_stats.counter)

    asked_stats = search_engine.get_total_number_of_requests(my_name)
    asked = None
    if asked_stats:
        asked = safe_json_dumps(asked_stats.counter)

    pending = "Comming Soon"

    my_person = search_engine.get_persons_info_by_name(my_name)
    area_to_counter = search_engine.get_personal_map_area_to_counter(my_name)
    found = True
    if not area_to_counter:
        found = False

    response = make_response(render_template('myPage.html',
                                             my_name=my_name,
                                             my_photo_id=my_person.photo_id,
                                             author_rank=author_rank,
                                             approval_rank=approval_rank,
                                             area_to_counter=area_to_counter,
                                             authored=authored,
                                             approved=approved,
                                             asked=asked,
                                             pending=pending,
                                             found=found))

    response.set_cookie('code_insight_user', my_name)

    return response


def safe_json_dumps(value):
    return json.dumps(value) if value else value


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess = Session()
    sess.init_app(app)

    app.run(threaded=True, host="0.0.0.0", port=8090)
