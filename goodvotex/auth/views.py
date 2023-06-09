from flask import render_template, redirect, url_for, flash, request
from flask_login import logout_user, current_user, login_required, login_user
from werkzeug.security import generate_password_hash

from . import auth, service


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if not auth.config["AUTH_ENABLE_REGISTRATION"]:
        return render_template('info.html', message="Registration is disabled.")

    if current_user.is_authenticated:
        return redirect(url_for('voting.start_page'))

    if request.method == 'POST':
        try:
            service.register_user(
                request.form.get('username'),
                request.form.get('name'),
                request.form.get('email'),
                request.form.get('passwd')
            )
            flash("Registration successful.", "info")
        except:
            return render_template('register.html')

    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("Already logged in.", "info")
        return redirect(url_for('voting.start_page'))

    if request.method == 'POST':
        user = service.get_user(request.form.get('username'))
        if user and user.check_password(request.form.get('passwd')):
            login_user(user)
            flash("Login successful.", "info")
            return redirect(url_for('voting.start_page'))
        else:
            flash("Invalid user or password.", "warning")

    return render_template('login.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('voting.start_page'))


@auth.route('/changepasswd')
@login_required
def change_password():
    password = request.form.get('passwd')
    new_password = request.form.get('new_passwd')
    confirm_password = request.form.get('confirm_passwd')

    service.change_password(current_user, password, new_password, confirm_password)
    flash("Password changed successfully!", "info")

    return redirect(url_for('voting.start_page'))
