import datetime
import operator
import random
from flask import Flask, request, render_template, Response, abort
from model import ARTISTS, RELEASES, TRACKS, ARTIST_TO_RELEASES, LETTERS, RELEASE_LETTERS, get_releases, get_tracks, \
    search_results_for

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
        artists = [a for (k, a) in ARTISTS.items() if a['name'].lower().startswith(letter)]
        artists.sort(key=operator.itemgetter('name'))
        artist_tuples = []
        for a in artists:
            releases = sorted([RELEASES[x] for x in get_releases(a)], key=operator.itemgetter('reldate'))
            artist_tuples.append((a, releases[0] if releases else None))
        sorted_alphabet = sorted(LETTERS.items(), key=operator.itemgetter(0))
        return render_template("artists.html", artists=artist_tuples, alphabet=sorted_alphabet)
    if id not in ARTISTS:
        return abort(404)
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
    # If there is no ID, render the release browsing page
    if id is None:
        letter = request.args.get("l", "a")
        releases = [r for (k, r) in RELEASES.items() if r['name'].lower().startswith(letter)]
        releases.sort(key=operator.itemgetter('name'))

        sorted_alphabet = sorted(RELEASE_LETTERS.items(), key=operator.itemgetter(0))
        return render_template("releases.html", releases=releases, alphabet=sorted_alphabet)
    if id not in RELEASES:
        return abort(404)
    # Otherwise, render the single artist page
    release = RELEASES[id]
    tracks = [TRACKS[x] for x in get_tracks(release)]
    # Get the highlighted track if this page was reached by clicking a search result
    highlight = request.args.get("highlight", None)
    # Sort by ascending release date
    # No problem with sorting in place since this list was created for this purpose
    tracks.sort(key=operator.itemgetter("position"))
    return render_template("single_release.html", release=release, tracks=tracks, highlight=highlight)


@app.route("/search")
def search():
    query = request.args.get("query", None)
    stream = request.args.get("stream", False)
    if stream == "true":
        return Response(search_results_for(query, stream=True), mimetype='text/html')
    else:
        results = [x for x in search_results_for(query, stream=False)]
        return render_template("search_results.html", results=results)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == " __main__ ":
    app.run(host='0.0.0.0', debug=True)
