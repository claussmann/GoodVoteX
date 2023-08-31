import click
from . import auth_cli
from . import service


@auth_cli.cli.command("add-user")
@click.argument("username")
@click.argument("name")
@click.argument("email")
@click.argument("password")
@click.argument("admin")
def add_user(username, name, email, password, admin):
    if service.get_user(username) is None:
        print("Creating user '{}' (email: {}) with login '{} : {}'".format(name, username, email, password))
        if admin:
            usergroup = service.get_group("admin")
            if usergroup is None:
                usergroup = service.register_group("admin", "Administrator")
            service.register_user(username, name, email, password, usergroup)
        else:
            usergroup = service.get_group("user")
            if usergroup is None:
                usergroup = service.register_group("user", "User")
            service.register_user(username, name, email, password, usergroup)
    else:
        print("A user with username '{}' already exists. Consider running 'change-pass' instead?".format(username))


@auth_cli.cli.command("change-pass")
@click.argument("username")
@click.argument("password")
def change_pass(username, password):
    if service.get_user(username) is not None:
        print("Changing password of '{}' to '{}'".format(username, password))
        # service.set_password_force(username, password) # TODO: Implement
    else:
        print("A user with username '{}' doesn't exist. Maybe consider running 'add-user' instead?".format(username))
