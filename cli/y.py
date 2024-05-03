import click
import requests
import getpass
import os
import json

API_URL = "http://127.0.0.1:5000/api/v1"

credentials = {
    "user_id": None,
    "auth_token": None
}

def validate_login():
    if not "auth_token" in credentials or credentials["auth_token"] is None:
        print("You have NOT logged in!")
        exit()

def api_call(url, data_json, assert_key = None):
    response = requests.post(f"{API_URL}/{url}", json=data_json).json()
    if "error" in response:
        print("ERROR:", response["error"])
        exit()
    if assert_key is not None and not (assert_key in response or response[assert_key]):
        print("ERROR:", response)
        exit()
    else:
        return response

@click.group()
@click.version_option("1.0.0", prog_name="CLI for Flask API")
def cli():
    """CLI support for Flask API project"""

@cli.group()
def auth():
    """Authorization API"""

@auth.command()
def login():
    """Login with username and password"""
    global credentials

    user_id = input("Username: ")
    user_password = getpass.getpass()
    
    response = api_call("auth/login", { "user_id": user_id, "user_password": user_password }, assert_key="logged_in")

    with open("credentials.json", "w") as file:
        credentials = { "user_id": response["user_id"], "auth_token": response["auth_token"] }
        json.dump(credentials, file)
        print(f"User logged in! You can use Flask API now as {user_id}")


@auth.command()
def logout():
    """Logout if logged in"""
    global credentials

    validate_login()

    api_call("auth/logout", credentials, assert_key="logged_out")

    if os.path.exists("credentials.json"):
        os.unlink("credentials.json")

    credentials = { "user_id": None, "auth_token": None }

    print(f"User logged out successfully!")


@auth.command()
def signup():
    """Signup as a new user"""

    user_id = input("Username: ")
    user_mail = input("E-Mail: ")
    user_password = getpass.getpass()
    user_password2 = getpass.getpass("Confirm Password: ")
    
    if user_password != user_password2:
        print("Passwords does NOT match! Try again")
        exit()
    
    print()
    print(f"USERNAME: {user_id}")
    print(f"E_MAIL  : {user_mail}")
    print()
    print("CONFIRM: Are those informations valid? [Y/N]")

    confirm = input().strip().upper()

    if confirm == "Y":
        api_call("auth/signup",{
            "user_id": user_id,
            "user_password": user_password,
            "user_mail": user_mail
        }, assert_key="signed_up")

        print("Signed up successfully. You can login now.")


@cli.group()
def user():
    """User API"""


@user.command()
@click.option("-s", "--set-privacy", default=None, help="Change privacy to private|public")
def privacy(set_privacy):
    """Get user privacy or set if specified"""

    validate_login()

    params = credentials.copy()

    if set_privacy is not None:
        if set_privacy not in ("private", "public"):
            print("Invalid parameter!")
            exit()
        else:
            params["privacy"] = set_privacy

    response = api_call("user/privacy", params, assert_key="privacy")

    print(f"{credentials['user_id']}'s content is {response['privacy']}")


@cli.group()
def clipboard():
    """Clipboard API"""

@clipboard.command()
@click.option("-c", "--clip-data", required=True, help="Clip to add")
def add(clip_data):
    """Add new clip to user's clipboard"""

    validate_login()

    params = credentials.copy()
    params["clip_data"] = clip_data

    response = api_call("clipboard/add", params, assert_key="clip_id")

    print(response)

@clipboard.command()
def list():
    """List user's clipboard"""

    validate_login()

    response = api_call("clipboard/list", credentials)

    if "count" in response:
        print(response)
    else:
        print("ERROR:", response)


@clipboard.command()
@click.option("-i", "--clip-id", required=True, help="Clip to add")
def delete(clip_id):
    """Delete clip by id from user's clipboard"""

    validate_login()

    params = credentials.copy()
    params["clip_id"] = clip_id

    response = api_call("clipboard/delete", params, assert_key="clip_id")

    print(response)


if __name__ == "__main__":
    if os.path.exists("credentials.json"):
        with open("credentials.json", "r") as file:
            credentials = json.load(file)
    cli()


def api_call(url, data_json):
    return requests.post(f"{API_URL}/{url}", json=data_json).json()

@click.group()
@click.version_option("1.0.0", prog_name="CLI for YNSource/Clipboard API")
def cli():
    """CLI support for YNSource/Clipboard API Project"""

@cli.group()
def auth():
    """Authorization API"""

@auth.command()
def login():
    """Login as user"""
    user_id = input("Username: ")
    user_password = getpass.getpass()
    
    response = api_call("auth/login", { "user_id": user_id, "user_password": user_password })

    if "error" in response:
        print("ERROR:", response["error"])
    elif "logged_in" in response and response["logged_in"] == True:
        with open("secret-credentials.txt", "w") as file:
            file.write(str(response))
        print(f"User logged in! You can use Flask API now as {user_id}")
    else:
        print("ERROR:", response)

@auth.command()
def signup():
    """Signup"""
    user_id = input("Username: ")
    user_mail = input("E-Mail: ")
    user_password = getpass.getpass()
    user_password2 = getpass.getpass("Confirm Password: ")
    
    if user_password != user_password2:
        print("Passwords does NOT match! Try again")
        exit()
    
    print()
    print(f"USERNAME: {user_id}")
    print(f"E_MAIL  : {user_mail}")
    print()
    print("CONFIRM: Are those informations valid? [Y/N]")

    confirm = input().strip().upper()

    if confirm == "Y":
        response = api_call("auth/signup",{
            "user_id": user_id,
            "user_password": user_password,
            "user_mail": user_mail
        })

        if "error" in response:
            print("ERROR:", response["error"])
        elif "signed_up" in response and response["signed_up"] == True:
                print("Signed up successfully. You can login now.")
        else:
            print("ERROR:", response)

if __name__ == "__main__":
    cli()
