import datetime
import operator
import random
from settings import APP_SECRET
from flask import Flask, request, render_template, Response, abort, session, redirect
from model import ARTISTS, RELEASES, TRACKS, ACOUSTICS, ARTIST_TO_RELEASES, LETTERS, RELEASE_LETTERS, get_releases, \
    get_tracks, get_top, search_results_for

app = Flask(__name__)
app.template_folder = 'templates'
app.secret_key = APP_SECRET


# Define a filter to be used in templates to convert a song's duration into a readable string
@app.template_filter()
def duration(time=0):
    seconds = time / 1000
    minutes = seconds / 60
    return str(int(minutes % 60)).zfill(2) + ":" + str(int(seconds % 60)).zfill(2)


# Transform a loudness number into a volume icon
@app.template_filter()
def volume_icon(loudness=0):
    base = "icono-volume"
    if loudness <= 0.3:
        return base
    if loudness <= 0.7:
        return base + "Low"
    if loudness <= 0.96:
        return base + "Medium"
    return base + "High"


# Transform a loudness number into an explanation
@app.template_filter()
def volume_text(loudness=0):
    if loudness <= 0.3:
        return "Deafening"
    if loudness <= 0.7:
        return "Not loud enough"
    if loudness <= 0.96:
        return "Pretty loud"
    return "I CAN'T HEAR YOU OVER THE SONG!!"


# Transform a danceability volume into a message
@app.template_filter()
def danceability_msg(dnc=0):
    if dnc <= 0.7:
        return "not danceable"
    if dnc <= 1.1:
        return "danceable"
    if dnc <= 1.5:
        return "highly danceable"
    return "dancefloor smasher!"


@app.template_filter()
def sortedvalues(value, key):
    if not value:
        return []
    return sorted(value.values(), key=operator.itemgetter(key))


@app.template_filter()
def get_acoustics(track):
    if 'id' not in track:
        return None
    return ACOUSTICS.get(track['id'], None)


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
    top_dance = [TRACKS[x['id']] for x in get_top(ACOUSTICS, operator.itemgetter('danceability'), 5, reverse=True)]
    return render_template(
        'index.html',
        hero=spotlight,
        top_dance=top_dance,
        staff_picks=[
            TRACKS['8c229043-1d05-40db-9342-9e084d315a25'],  # The Bellrays - Black lightning
            TRACKS['ab205556-92b9-4c89-adec-0a9dbce7b43f'],  # Arcade Fire - Ready to start
            TRACKS['c61d3fe1-f265-45b9-855e-35a3dfae45c4'],  # Graveyard - Ain't fit to live here
            TRACKS['63d9e22a-6053-491d-bbd7-da9707b8bbe0'],  # Garbage - Queer
            TRACKS['2c6963e1-dd65-4509-b046-51fd808fe6fe'],  # Halestorm - Mayhem
        ],
        classics=[
            TRACKS['cb77deb7-f961-4cb3-9a44-c56adc3d10e8'],  # Janis Joplin - Piece of my heart
            TRACKS['ef71afb6-5e51-41df-999b-9e7c7306063a'],  # AC/DC - Back in black
            TRACKS['b8bcd44d-b698-465f-a3ed-c38ca81418d6'],  # Guns n' Roses - Paradise City
            TRACKS['768217d5-f223-4942-9283-8b3e67e62e94'],  # The Doors - Break on Through
            TRACKS['597eae0b-ccb6-4076-b997-0ce940586076'],  # Pink Floyd - Another brick in the wall
        ]
    )


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
    artist = ARTISTS[release['artist']]
    tracks = [TRACKS[x] for x in get_tracks(release)]
    # Get the highlighted track if this page was reached by clicking a search result
    highlight = request.args.get("highlight", None)
    # Sort by ascending release date
    # No problem with sorting in place since this list was created for this purpose
    tracks.sort(key=operator.itemgetter("position"))
    return render_template("single_release.html", artist=artist, release=release, tracks=tracks, highlight=highlight)


@app.route("/setlist", methods=['GET'])
def setlist():
    return render_template("setlist.html")


# Better semantics can be achieved here with PUT and DELETE
# But HTML does not support PUT or DELETE as methods in form
# So in order to maintain functionality without javascript
# (AJAX supports PUT and DELETE)
# the request as sent from an HTML FORM, is always a POST and
# the '_method' hidden field dictates what action should be taken
# With a default of add.
# The method supports both PUT and DELETE as well for AJAX calls

# PUT here is idempotent, since session['setlist'] is a dictionary.
# Adding a song more than once will always result in the song being in the setlist, but never more than once
# DELETE does not have to be idempotent, since after something is deleted we can throw an error saying there's
# nothing to delete with that ID

# As for the response being a redirect,
# a better way would be to return a 205 Status code, which tells
# the client that it should refresh the view to update the status,
# but no major browser implements this feature, they all treat a 205
# response as a 204 NO CONTENT response and basically do nothing,
# rather than refreshing the current page.
@app.route("/setlist/<string:track>", methods=['POST', 'PUT', 'DELETE'])
def setlist_update(track):
    current_setlist = session.pop("setlist", {})
    action = 'add'
    if request.method == 'POST':
        action = request.form.get('_action', "add")
    elif request.method == 'PUT':
        action = "add"
    elif request.method == "DELETE":
        action = "remove"

    if action == 'remove':
        if track not in current_setlist:
            return "Track not in setlist, not able to delete", 400
        else:
            # Get the weight of the item to delete so we can reorganise the setlist
            curr_weight = current_setlist[track]['weight']
            print(curr_weight)
            del current_setlist[track]
            # reorganise the setlist by decreasing the weight of every element that
            # was added before the one we're deleting
            for t in current_setlist.values():
                if t['weight'] > curr_weight:
                    t['weight'] = t['weight'] - 1
            session['setlist'] = current_setlist
            return redirect(request.referrer, 200)

    elif action == 'add':
        if track in TRACKS:
            current_setlist[track] = {"track": TRACKS[track], "weight": len(current_setlist)}
            session['setlist'] = current_setlist
            return redirect(request.referrer, 200)
        else:
            return "Track not found, not able to add to setlist", 400
    else:
        return "Unknown method '" + method + "'", 400


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
