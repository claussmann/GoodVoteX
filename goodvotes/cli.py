from goodvotes import *
import click
from .models.election import *
from . import service


@app.cli.command("create-db")
@click.option("--overwrite", is_flag=True, show_default=True, default=False, help="Overwrite the old database.")
def create_db(overwrite):
    if not overwrite:
        try:
            Election.query.all()  # Fails if database (or tables) do not exist.
            print("Database exists. Nothing to do.")
        except:
            db.create_all()
            print("Database doesn't exist. Created database.")
    else:
        db.drop_all()
        db.create_all()
        print("Created empty database.")


@app.cli.command("add-user")
@click.argument("username")
@click.argument("name")
@click.argument("password")
def add_user(username, name, password):
    if service.get_user(username) == None:
        print("Creating user '%s' with login '%s : %s'" % (name, username, password))
        service.register_user(username, name, password)
    else:
        print("A user with username '%s' already exists. Maybe consider running 'change-pass' instead?" % username)


@app.cli.command("change-pass")
@click.argument("username")
@click.argument("password")
def change_pass(username, password):
    if service.get_user(username) != None:
        print("Changing password of '%s' to '%s'" % (username, password))
        # service.set_password_force(username, password) # TODO: Implement
    else:
        print("A user with username '%s' doesn't exist. Maybe consider running 'add-user' instead?" % username)