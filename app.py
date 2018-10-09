import datetime
import operator
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
        releases = sorted([RELEASES[x] for x in get_releases(artist)], key=operator.itemgetter('reldate'))
        obj = {
            "artist": artist,
            "release": releases[0] if releases else None
        }
        spotlight.append(obj)
    return render_template('index.html', hero=spotlight)


@app.route("/artists", methods=['GET'])
@app.route("/artists/<string:id>", methods=['GET'])
def artists(id=None):
    # If there is no ID, render the artist browsing page
    if id is None:
        letter = request.args.get("l", "a")
        artists = [a for (k, a) in ARTISTS.items() if a['name'].lower().startswith(letter.lower())]
        artists.sort(key=operator.itemgetter('name'))
        artist_tuples = []
        for a in artists:
            releases = sorted([RELEASES[x] for x in get_releases(a)], key=operator.itemgetter('reldate'))
            artist_tuples.append((a, releases[0] if releases else None))
        return render_template("artists.html", artists=artist_tuples, alphabet=map(chr, range(65, 91)))
    # Otherwise, render the single artist page
    artist = ARTISTS[id]
    releases = [RELEASES[x] for x in get_releases(artist)]
    # Sort by ascending release date
    # No problem with sorting in place since this list was created for this purpose
    releases.sort(key=operator.itemgetter("reldate"))
    return render_template("single_artist.html", artist=artist, releases=releases)


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
    stream = request.args.get("stream", False)
    if stream == "true":
        return Response(search_results_for(query, stream=True), mimetype='text/html')
    else:
        results = [x for x in search_results_for(query, stream=False)]
        return render_template("search_results.html", results=results)


if __name__ == " __main__ ":
    app.run(host='0.0.0.0', debug=True)
