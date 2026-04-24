from flask import Flask, jsonify, request
from flask_cors import CORS
from scraper import _bootstrap_session, get_posts_with_comments, SESSION_ID

app = Flask(__name__)
CORS(app)

@app.route("/api/scrape", methods=["GET"])
def scrape():
      username = request.args.get("username", "").strip()
      post_limit = min(int(request.args.get("posts", 10)), 20)

      if not username:
          return jsonify({"error": "username requerido"}), 400

      session = _bootstrap_session(SESSION_ID)
      result = get_posts_with_comments(username, session, post_limit, comment_limit=3)

      if result["success"]:
          return jsonify(result)
      return jsonify({"error": result.get("error", "Error desconocido")}), 500

if __name__ == "__main__":
      app.run(debug=True, port=5000)