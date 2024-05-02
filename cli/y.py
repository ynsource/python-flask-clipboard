import click
import requests
import getpass

API_URL = "http://127.0.0.1:5000/api/v1"

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
