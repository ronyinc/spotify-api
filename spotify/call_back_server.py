
from utils.file_utils import save_json
from flask import Flask, request
import requests
import webbrowser

from auth.spotify_auth import build_authorization_url, get_access_token

app = Flask(__name__)
token_response = None

@app.route("/callback")
def callback():

    global token_response
    code = request.args.get("code")
    if not code:
        return "Authorization code not found"

    token_response = get_access_token(code)
    save_json(token_response, "data/token_file.json")

    print("Access token:", token_response["access_token"])
    print("Refresh token:", token_response["refresh_token"])

    return "Success! Tokens received. You can close this tab and return to the terminal."


if __name__ == "__main__":
    url = build_authorization_url()
    print(f"Open the url in the browser: \n{url}")
    # webbrowser.open(build_authorization_url())
    app.run(host="0.0.0.0", port=8888)



