from flask import Flask, request, redirect, jsonify
import requests, os

app = Flask(__name__)

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
TENANT_ID = os.environ.get("TENANT_ID")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

access_token = None

@app.route("/")
def login():
    auth_url = (
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?"
        f"client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&"
        f"response_mode=query&scope=https%3A%2F%2Fgraph.microsoft.com%2FFiles.Read%20offline_access"
    )
    return redirect(auth_url)

@app.route("/oauth-callback")
def callback():
    global access_token
    code = request.args.get("code")
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "scope": "https://graph.microsoft.com/Files.Read offline_access"
    }
    r = requests.post(token_url, data=data)
    token_data = r.json()
    access_token = token_data.get("access_token")
    return "✅ Authorized! Access token stored in memory."

@app.route("/list-files")
def list_files():
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get("https://graph.microsoft.com/v1.0/me/drive/root/children", headers=headers)
    return jsonify(r.json())

# ✅ THIS IS THE KEY TO FIX YOUR DEPLOY
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
