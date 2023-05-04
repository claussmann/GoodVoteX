from flask import *
import Service
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

@app.before_first_request
def initialization_code():
    Service.load_all()

@app.route('/')
def start_page():
    return render_template('start.html')

@app.route('/done')
def voted_successfully_page():
    return render_template('done.html')

@app.route('/createnew', methods=['POST'])
def create_new_election():
    candidates = set()
    for i in range(1,13):
        c = request.form.get('candidate%d'%i)
        if c != None and c != "" and not c.isspace():
            candidates.add(c)
    election = Service.register_election(
        request.form.get('name'), 
        request.form.get('description'),
        candidates,
        int(request.form.get('committeesize'))
    )
    app.logger.info("Election registered: %s, %d candidates, committee size: %d" %(election.name, len(election.candidates), election.K))
    return render_template('details.html', election = election, admin=False, justcreated=True)

@app.route('/searchforelection')
def search_election():
    keyword = request.args.get('keyword')
    matching_elections = Service.search(keyword)
    return render_template('search_results.html', keyword = keyword, elections = matching_elections)

@app.route('/details/<electionID>')
def details_page(electionID):
    return render_template('details.html', election = Service.get_election(electionID), admin =False, justcreated=False)

@app.route('/vote/<electionID>')
def voting_page(electionID):
    return render_template('vote.html', election = Service.get_election(electionID))

@app.route('/vote/<electionID>', methods=['POST'])
def add_vote(electionID):
    content = request.get_json()
    try:
        sets = content["sets"]
        bounds = content["bounds"]
        bounded_sets = list()
        for s in sets:
            items_in_set = set(sets[s])
            if len(items_in_set) == 0:
                continue
            bounded_sets.append(Service.BoundedSet(bounds[s][0],bounds[s][1],bounds[s][2], items_in_set))
        
        votesstring = ("%s  "*len(bounded_sets)) %tuple([str(s) for s in bounded_sets])
        app.logger.debug("New vote received: " + votesstring)
        Service.add_vote(electionID, bounded_sets)
    except Exception as e:
        app.logger.warn(e)
        return "something is wrong with the data", 400
    return "OK"

@app.route('/evaluate/<electionID>', methods=['POST'])
def evaluation_page(electionID):
    token = request.form['token']
    best_committees = Service.evaluate_final_winners(electionID, token)
    election = Service.get_election(electionID)
    if len(best_committees) > 10:
        best_committees = best_committees[:11]
    app.logger.info("Results stopped by creator: %s (%s)" %(election.eid, election.name))
    return render_template('eval.html', election = election, bestcommittees = best_committees)

@app.route('/admin/<electionID>', methods=['POST'])
def admin_details_page(electionID):
    token = request.form['token']
    best_committees = Service.evaluate_current_winners(electionID, token)
    election = Service.get_election(electionID)
    if len(best_committees) > 10:
        best_committees = best_committees[:11]
    return render_template('details.html', election = election, bestcommittees = best_committees, admin = True, justcreated=False)

@app.route('/publish/<electionID>', methods=['POST'])
def publish_successful_page(electionID):
    token = request.form['token']
    winner_id = request.form['winner']
    Service.select_winner(electionID, token, winner_id)
    app.logger.info("Results published by creator: %s (%s)" %(election.eid, election.name))
    return render_template('done.html')

@app.route('/delete/<electionID>', methods=['POST'])
def deletion_successful_page(electionID):
    token = request.form['token']
    Service.delete(electionID, token)
    app.logger.info("Results deleted by creator: %s" %election.eid)
    return render_template('done.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(400)
def page_not_found(e):
    return render_template('errors/400.html'), 400

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    return render_template("errors/500.html", exception=e), 500