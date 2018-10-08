import random
from flask import Flask, request, render_template, Response
from model import ARTISTS, RELEASES, ARTIST_TO_RELEASES, get_releases, search_results_for

app = Flask(__name__)
app.template_folder = 'templates'


@app.route("/", methods=['GET'])
def index():
    # Get 5 random artists
    spotlight = []
    for a in random.sample(list(ARTISTS), 5):
        artist = ARTISTS[a]
        releases = get_releases(artist)
        obj = {
            "artist": artist,
            "release": RELEASES[releases.pop()] if releases else None
        }
        spotlight.append(obj)
    return render_template('index.html', hero=spotlight)


@app.route("/artists", methods=['GET'])
@app.route("/artists/<string:id>", methods=['GET'])
def artists(id=None):
    return "Artist id is: " + str(id)


@app.route("/releases", methods=['GET'])
@app.route("/releases/<string:id>", methods=['GET'])
def releases(id=None):
    return "Release id is: " + str(id)


@app.route("/tracks", methods=['GET'])
@app.route("/tracks/<string:id>", methods=['GET'])
def tracks(id=None):
    return "Track id is: " + str(id)


@app.route("/search")
def search():
    query = request.args.get("query", None)
    stream = request.args.get("stream", True)
    if stream != "false":
        print("streaming")
        return Response(search_results_for(query), mimetype='text/html')
    else:
        print("not streaming")
        results = [x for x in search_results_for(query, stream=False)]
        print(results)
        return render_template("search_results.html", results=results)


if __name__ == " __main__ ":
    app.run(host='0.0.0.0', debug=True)
