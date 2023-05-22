from flask import render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.exceptions import HTTPException

from . import service, voting, logger


@voting.route('/', methods=['GET', 'POST'])
def start_page():
    if request.method == 'POST':
        candidates = set(filter(len, request.form.getlist('candidates[]')))
        if len(candidates) != len(list(filter(len, request.form.getlist('candidates[]')))):
            # at least one name was present twice
            flash("Candidate names must be unique. Creation failed.", "error")
        if len(candidates) <= int(request.form.get('committeesize')):
            # candidate set must be larger than committee-size.
            flash("Candidate set must be larger than committee-size.", "error")
        else:
            # we can continue creation with the given candidate set.
            election = service.register_election(
                request.form.get('name'),
                request.form.get('description'),
                candidates,
                int(request.form.get('committeesize')),
                current_user
            )
            logger.info("Election registered: %s, %d candidates, committee size: %d" % (
                election.title, len(election.candidates), election.committeesize))
            flash("Election was successfully created.", "info")
            return redirect(url_for('voting.details_page', electionID=election.id))

    return render_template('start.html', elections=service.get_all_elections())


@voting.route('/done')
def done_page():
    return render_template('done.html', forward="/")


@voting.route('/searchforelection')
def search_election():
    keyword = request.args.get('keyword')
    matching_elections = service.search(keyword)
    return render_template('search_results.html', keyword=keyword, elections=matching_elections,
                           user=current_user)


@voting.route('/details/<electionID>', methods=['GET', 'POST'])
def details_page(electionID):
    election = service.get_election(electionID)
    if current_user and current_user.owns_election(election):
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
    logger.info("Election stopped by creator: %s (%s)" % (electionID, election.title))
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
    logger.error(e)
    return render_template("errors/500.html", exception=e), 500
