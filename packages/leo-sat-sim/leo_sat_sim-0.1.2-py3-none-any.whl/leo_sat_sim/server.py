from flask import Flask, send_from_directory
import os

# Serve out of the current directory (dist/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "public"),
    static_url_path="/public"
)

# ======================
# ROUTES
# ======================

@app.route("/")
def serve_index():
    return send_from_directory(os.path.join(BASE_DIR, "public"), "index.html")


# Serve node_modules assets safely
@app.route("/node_modules/<path:filename>")
def serve_node_modules(filename):
    return send_from_directory(os.path.join(BASE_DIR, "node_modules"), filename)


# Catch-all for any static files referenced in HTML (CSS, JS, images)
@app.route("/<path:path>")
def catch_all(path):
    # serve from public/
    public_path = os.path.join(BASE_DIR, "public", path)
    if os.path.exists(public_path):
        return send_from_directory(os.path.join(BASE_DIR, "public"), path)

    # serve from node_modules/
    node_path = os.path.join(BASE_DIR, "node_modules", path)
    if os.path.exists(node_path):
        return send_from_directory(os.path.join(BASE_DIR, "node_modules"), path)

    # fallback: return index.html for SPA compatibility
    return send_from_directory(os.path.join(BASE_DIR, "public"), "index.html")

# ======================
# PRODUCTION ENTRYPOINT
# ======================

# DO NOT ENABLE debug=True
if __name__ == "__main__":
    # NOT for production use
    app.run(host="0.0.0.0", port=8080)
