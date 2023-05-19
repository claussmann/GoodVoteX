from flask import render_template, request
from flask_login import login_required, current_user
from werkzeug.exceptions import HTTPException

from . import service, voting, logger


@voting.route('/')
def start_page():
    return render_template('start.html')


@voting.route('/done')
def done_page():
    user = False
    return render_template('done.html', forward="/")


@voting.route('/createnew', methods=['POST'])
@login_required
def create_new_election():
    candidates = set()
    for i in range(1, 13):
        c = request.form.get('candidate%d' % i)
        if c != None and c != "" and not c.isspace():
            candidates.add(c)
    election = service.register_election(
        request.form.get('name'),
        request.form.get('description'),
        candidates,
        int(request.form.get('committeesize')),
        current_user
    )
    logger.info("Election registered: %s, %d candidates, committee size: %d" % (
        election.title, len(election.candidates), election.committeesize))
    return render_template('done.html', forward="/details/" + str(election.id))


@voting.route('/searchforelection')
def search_election():
    keyword = request.args.get('keyword')
    matching_elections = service.search(keyword)
    return render_template('search_results.html', keyword=keyword, elections=matching_elections,
                           user=current_user)


@voting.route('/details/<electionID>')
def details_page(electionID):
    election = service.get_election(electionID)
    if current_user and current_user.owns_election(electionID):
        service.evaluate(electionID, current_user)
        return render_template('details.html', election=election, admin=True)
    return render_template('details.html', election=election, admin=False)


@voting.route('/vote/<electionID>')
def voting_page(electionID):
    return render_template('vote.html', election=service.get_election(electionID))


@voting.route('/vote/<electionID>', methods=['POST'])
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
            bounded_sets.append(service.BoundedSet(bounds[s][0], bounds[s][1], bounds[s][2], items_in_set))

        votesstring = ("%s  " * len(bounded_sets)) % tuple([str(s) for s in bounded_sets])
        logger.debug("New vote received: " + votesstring)
        ballot = service.BoundedApprovalBallot()
        ballot.encode(bounded_sets)
        service.add_vote(electionID, ballot)
    except Exception as e:
        logger.warn(e)
        return "something is wrong with the data", 400
    return "OK"


@voting.route('/evaluate/<electionID>', methods=['POST'])
@login_required
def evaluate(electionID):
    election = service.get_election(electionID)
    best_committee = service.evaluate(electionID, current_user)
    service.stop_election(electionID, current_user)
    logger.info("Election stopped by creator: %s (%s)" % (election.eid, election.name))
    return render_template('done.html', forward="/details/" + electionID)


@voting.route('/delete/<electionID>', methods=['POST'])
@login_required
def deletion_successful_page(electionID):
    service.delete_election(electionID, current_user)
    logger.info("Results deleted by creator: %s" % str(electionID))
    return render_template('done.html', forward="/")


@voting.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@voting.errorhandler(400)
def page_not_found(e):
    return render_template('errors/400.html'), 400


@voting.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    print(e)
    return render_template("errors/500.html", exception=e), 500
