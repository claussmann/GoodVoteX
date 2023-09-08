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
                service.register_user(
                    request.form.get('username'),
                    request.form.get('name'),
                    request.form.get('email'),
                    request.form.get('passwd')
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


@auth.route('/adminpanel', methods=['GET'])
@login_required
def adminpanel():
    if current_user.is_admin():
        return render_template('admin_page.html', user=current_user, allusers=service.get_all_users())
    flash("you need to login as admin to view the admin page.", "danger")
    return render_template('userinfo.html', user=current_user)


@auth.route('/adminpanel/createuser', methods=['POST'])
def admin_create_user():
    if request.form.get('tnc_accept') != "accept":
        flash("You must inform the users about our Terms and Conditions.", "danger")
    else:
        try:
            service.register_user(
                request.form.get('username'),
                request.form.get('name'),
                request.form.get('email'),
                request.form.get('passwd')
            )
            flash("User %s successfully created." % request.form.get('username'), "success")
        except:
            flash("Something went wrong. Maybe username is already taken?") 
    return redirect(url_for('auth.adminpanel'))

@auth.route('/useredit/<username>', methods=['GET'])
@login_required
def useredit(username):
    if current_user.is_admin():
        return render_template('useredit.html', user=current_user, edituser=service.get_user(username))
    flash("you need to login as admin to edit a user.", "danger")
    return render_template('userinfo.html', user=current_user)

@auth.route('/useredit/permissions/<username>', methods=['POST'])
@login_required
def user_permissions_edit(username):
    if current_user.is_admin():
        if request.form.get('vote') == "true":
            service.update_user_permissions(username, vote=True)
        if request.form.get('vote') == "false":
            service.update_user_permissions(username, vote=False)
        if request.form.get('create') == "true":
            service.update_user_permissions(username, create=True)
        if request.form.get('create') == "false":
            service.update_user_permissions(username, create=False)
        return redirect(url_for('auth.useredit', username=username))
    flash("you need to login as admin to edit a user.", "danger")
    return render_template('userinfo.html', user=current_user)


@auth.route('/useredit/resetpassword/<username>', methods=['POST'])
@login_required
def password_reset(username):
    edituser = service.get_user(username)
    if current_user.username == username:
        flash("Please use the user info form to change your password.", "danger")
    elif edituser.is_admin():
        flash("Admin passwords cannot be changed this way.", "danger")
    elif current_user.is_admin():
        password = request.form.get('passwd_reset')
        service.change_password(edituser, "", password, "", force=True)
        flash("Password reset successfully.", "success")
        return redirect(url_for('auth.useredit', username=username))
    else:
        flash("you need to login as admin to edit a user.", "danger")
    return render_template('userinfo.html', user=current_user)


@auth.route('/useredit/delete/<username>', methods=['POST'])
@login_required
def delete_user(username):
    edituser = service.get_user(username)
    if edituser.is_admin():
        flash("Admins cannot be deleted.", "danger")
    elif current_user.is_admin():
        service.delete_user(username)
        flash("User deleted successfully.", "success")
        return redirect(url_for('auth.adminpanel'))
    else:
        flash("you need to login as admin to edit a user.", "danger")
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