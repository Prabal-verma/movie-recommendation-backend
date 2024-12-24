import json
import pickle
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)  # This allows all origins by default

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Load the pickle files
movies = pickle.load(open("./../../model/movie_list.pkl", "rb"))
similarity = pickle.load(open("./../../model/similarity.pkl", "rb"))

@app.route("/movies", methods=["GET"])
def get_movies():
    movie_list = movies["title"].tolist()
    return jsonify(movie_list)

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.json
        movie_name = data.get("movie")

        if not movie_name:
            return jsonify({"error": "No movie provided"}), 400

        if movie_name not in movies["title"].values:
            return jsonify({"error": "Movie not found"}), 404

        # Calculate recommendations
        index = movies[movies["title"] == movie_name].index[0]
        distances = sorted(
            list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
        )

        recommendations = []
        for i in distances[1:6]:
            movie_id = int(movies.iloc[i[0]].movie_id)  # Convert int64 to Python int
            recommendations.append({
                "title": str(movies.iloc[i[0]].title),  # Ensure string type
                "movie_id": movie_id
            })

        return jsonify(recommendations)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
