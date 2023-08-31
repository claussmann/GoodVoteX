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
        if request.form.get('tnc_accept') != "accept":
            flash("You must accept our Terms and Conditions.", "danger")
        elif request.form.get('passwd') != request.form.get('passwd_confirm'):
            flash("Passwords do not match.", "danger")
        else:
            try:
                usergroup = service.get_group("user")
                if usergroup is None:
                    usergroup = service.register_group("user", "User")
                service.register_user(
                    request.form.get('username'),
                    request.form.get('name'),
                    request.form.get('email'),
                    request.form.get('passwd'),
                    usergroup
                )
                flash("Registration successful.", "info")
            except:
                flash("Something went wrong. Maybe username is already taken?") 
            return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/userinfo', methods=['GET'])
@login_required
def userinfo():
    return render_template('userinfo.html', user=current_user)


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


@auth.route('/changepasswd', methods=['POST'])
@login_required
def change_password():
    password = request.form.get('passwd')
    new_password = request.form.get('new_passwd')
    confirm_password = request.form.get('confirm_passwd')

    service.change_password(current_user, password, new_password, confirm_password)
    flash("Password changed successfully!", "info")

    return redirect(url_for('voting.start_page'))


@auth.route('/toggletheme', methods=['POST'])
@login_required
def toggle_theme():
    service.toggle_theme(current_user)
    return redirect(url_for('auth.userinfo'))