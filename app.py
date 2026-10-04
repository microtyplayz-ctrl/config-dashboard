import os
import secrets
import requests

from flask import Flask, request, jsonify, render_template_string, session, redirect

app = Flask(__name__)

app.secret_key = os.environ["SESSION_SECRET"]

VPS_API_URL = os.environ["VPS_API_URL"].rstrip("/")
VPS_API_KEY = os.environ["VPS_API_KEY"]
DASHBOARD_KEY = os.environ["DASHBOARD_KEY"]


HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>Config Dashboard</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background:
        radial-gradient(circle at top left,#5b21b6,transparent 35%),
        radial-gradient(circle at bottom right,#2563eb,transparent 35%),
        #080812;
    color: white;
    min-height: 100vh;
}

.container {
    width: min(1100px,94%);
    margin: 40px auto;
}

.card {
    background: rgba(20,20,35,.82);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,.35);
    backdrop-filter: blur(15px);
}

h1 {
    margin-top: 0;
}

h2 {
    font-size: 18px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(280px,1fr));
    gap: 15px;
}

label {
    display: block;
    margin-bottom: 7px;
    color: #c9c9d9;
}

input, textarea, select {
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #38384d;
    background: #11111d;
    color: white;
    outline: none;
}

textarea {
    min-height: 120px;
    resize: vertical;
}

button {
    border: 0;
    border-radius: 10px;
    padding: 12px 18px;
    background: linear-gradient(135deg,#8b5cf6,#6366f1);
    color: white;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    opacity: .88;
}

.danger {
    background: #dc2626;
}

.save {
    width: 100%;
    margin-top: 10px;
    font-size: 16px;
}

#status {
    margin-top: 15px;
    padding: 12px;
    border-radius: 10px;
    display: none;
}

.login {
    max-width: 420px;
    margin: 15vh auto;
    text-align: center;
}

.list {
    margin-top: 10px;
}

.item {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
}

.item input {
    flex: 1;
}

.logout {
    float: right;
    background: #27273a;
}
</style>
</head>

<body>

<div class="container">

{% if not authenticated %}

<div class="card login">

    <h1>🔐 Dashboard</h1>
    <p>Enter your dashboard key.</p>

    <form method="POST" action="/key">
        <input
            type="password"
            name="key"
            placeholder="Dashboard Key"
            required
        >

        <br><br>

        <button style="width:100%">
            ACCESS DASHBOARD
        </button>
    </form>

    {% if error %}
        <p style="color:#f87171">{{ error }}</p>
    {% endif %}

</div>

{% else %}

<button class="logout" onclick="location.href='/logout'">
    Logout
</button>

<h1>⚡ Configuration Dashboard</h1>
<p>Edit the VPS <code>config_live.json</code> remotely.</p>

<div class="card">

<h2>Discord Tokens</h2>

<textarea id="TOKENS"></textarea>

</div>

<div class="card">

<h2>Target Channel IDs</h2>

<textarea id="TARGET_CHANNEL_IDS"></textarea>

</div>

<div class="card">

<h2>Spam Channel IDs</h2>

<textarea id="SPAM_CHANNEL_IDS"></textarea>

</div>

<div class="card">

<h2>Allowed Users</h2>

<textarea id="ALLOWED_USERS"></textarea>

</div>

<div class="card">

<h2>Bot Configuration</h2>

<div class="grid">

<div>
<label>Pokétwo Bot ID</label>
<input id="POKETWO_BOT_ID">
</div>

<div>
<label>Resolver API</label>
<input id="RESOLVER_API">
</div>

<div>
<label>RPC Status</label>
<select id="RPC_STATUS">
<option value="online">Online</option>
<option value="idle">Idle</option>
<option value="dnd">Do Not Disturb</option>
<option value="offline">Offline</option>
</select>
</div>

<div>
<label>RPC Type</label>
<select id="RPC_TYPE">
<option value="playing">Playing</option>
<option value="streaming">Streaming</option>
<option value="listening">Listening</option>
<option value="watching">Watching</option>
</select>
</div>

<div>
<label>RPC Text</label>
<input id="RPC_TEXT">
</div>

<div>
<label>RPC Emoji</label>
<input id="RPC_EMOJI">
</div>

<div>
<label>Large Image</label>
<input id="RPC_IMAGE_LARGE">
</div>

<div>
<label>Small Image</label>
<input id="RPC_IMAGE_SMALL">
</div>

<div>
<label>Stream URL</label>
<input id="RPC_STREAM_URL">
</div>

</div>

</div>

<div class="card">

<button class="save" onclick="saveConfig()">
💾 SAVE CONFIGURATION
</button>

<div id="status"></div>

</div>

{% endif %}

</div>

{% if authenticated %}

<script>

async function loadConfig() {

    const response = await fetch("/api/config");

    if (!response.ok) {
        alert("Unable to load configuration.");
        return;
    }

    const config = await response.json();

    document.getElementById("TOKENS").value =
        (config.TOKENS || []).join("\\n");

    document.getElementById("TARGET_CHANNEL_IDS").value =
        (config.TARGET_CHANNEL_IDS || []).join("\\n");

    document.getElementById("SPAM_CHANNEL_IDS").value =
        (config.SPAM_CHANNEL_IDS || []).join("\\n");

    document.getElementById("ALLOWED_USERS").value =
        (config.ALLOWED_USERS || []).join("\\n");

    document.getElementById("POKETWO_BOT_ID").value =
        config.POKETWO_BOT_ID ?? "";

    document.getElementById("RESOLVER_API").value =
        config.RESOLVER_API ?? "";

    document.getElementById("RPC_STATUS").value =
        config.RPC_STATUS ?? "online";

    document.getElementById("RPC_TYPE").value =
        config.RPC_TYPE ?? "playing";

    document.getElementById("RPC_TEXT").value =
        config.RPC_TEXT ?? "";

    document.getElementById("RPC_EMOJI").value =
        config.RPC_EMOJI ?? "";

    document.getElementById("RPC_IMAGE_LARGE").value =
        config.RPC_IMAGE_LARGE ?? "";

    document.getElementById("RPC_IMAGE_SMALL").value =
        config.RPC_IMAGE_SMALL ?? "";

    document.getElementById("RPC_STREAM_URL").value =
        config.RPC_STREAM_URL ?? "";
}


function lines(id) {

    return document
        .getElementById(id)
        .value
        .split("\\n")
        .map(x => x.trim())
        .filter(Boolean);
}


async function saveConfig() {

    const config = {

        TOKENS: lines("TOKENS"),

        TARGET_CHANNEL_IDS:
            lines("TARGET_CHANNEL_IDS").map(Number),

        SPAM_CHANNEL_IDS:
            lines("SPAM_CHANNEL_IDS").map(Number),

        ALLOWED_USERS:
            lines("ALLOWED_USERS").map(Number),

        POKETWO_BOT_ID:
            Number(document.getElementById("POKETWO_BOT_ID").value),

        RESOLVER_API:
            document.getElementById("RESOLVER_API").value,

        RPC_STATUS:
            document.getElementById("RPC_STATUS").value,

        RPC_TYPE:
            document.getElementById("RPC_TYPE").value,

        RPC_TEXT:
            document.getElementById("RPC_TEXT").value,

        RPC_EMOJI:
            document.getElementById("RPC_EMOJI").value,

        RPC_IMAGE_LARGE:
            document.getElementById("RPC_IMAGE_LARGE").value,

        RPC_IMAGE_SMALL:
            document.getElementById("RPC_IMAGE_SMALL").value,

        RPC_STREAM_URL:
            document.getElementById("RPC_STREAM_URL").value
    };

    const response = await fetch("/api/config", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(config)
    });

    const result = await response.json();

    const status = document.getElementById("status");

    status.style.display = "block";

    if (response.ok) {
        status.style.background = "#14532d";
        status.textContent = "✓ Configuration saved to VPS.";
    } else {
        status.style.background = "#7f1d1d";
        status.textContent =
            result.error || "Failed to save configuration.";
    }
}


loadConfig();

</script>

{% endif %}

</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():

    if not session.get("authenticated"):
        return render_template_string(
            HTML,
            authenticated=False,
            error=None
        )

    return render_template_string(
        HTML,
        authenticated=True,
        error=None
    )


@app.route("/key", methods=["POST"])
def key():

    supplied = request.form.get("key", "")

    if secrets.compare_digest(supplied, DASHBOARD_KEY):

        session["authenticated"] = True

        return redirect("/")

    return render_template_string(
        HTML,
        authenticated=False,
        error="Invalid dashboard key."
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


@app.route("/api/config", methods=["GET"])
def get_config():

    if not session.get("authenticated"):
        return jsonify({"error": "Unauthorized"}), 401

    response = requests.get(
        VPS_API_URL + "/config",
        headers={
            "X-API-Key": VPS_API_KEY
        },
        timeout=15
    )

    return (
        response.text,
        response.status_code,
        {"Content-Type": "application/json"}
    )


@app.route("/api/config", methods=["POST"])
def update_config():

    if not session.get("authenticated"):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    response = requests.post(
        VPS_API_URL + "/config",
        headers={
            "X-API-Key": VPS_API_KEY,
            "Content-Type": "application/json"
        },
        json=data,
        timeout=15
    )

    return (
        response.text,
        response.status_code,
        {"Content-Type": "application/json"}
    )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )