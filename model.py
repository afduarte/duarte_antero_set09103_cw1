from settings import DATA_DIR
from flask import url_for
import time
import csv
from difflib import SequenceMatcher

ARTISTS = {}
RELEASES = {}
TRACKS = {}
ACOUSTICS = {}

# Indices, for faster lookups

# Index artists to their releases
ARTIST_TO_RELEASES = {}
ARTIST_TO_TRACKS = {}
RELEASE_TO_TRACKS = {}
TEXTINDEX = {}

# List the first character in the bands' names so we can generate a list in the frontend
# The reason why we need this is some bands have decided to call themselves weird stuff
# like numbers or special characters
# seriously... "!!!" is a band name

LETTERS = {}

# Same for releases
RELEASE_LETTERS = {}

with open(DATA_DIR + "/artists.csv") as file:
    reader = csv.reader(file, delimiter=',', quotechar='"')
    # skip headers
    next(reader)
    for row in reader:
        # Add artists to the dict, using their musicbrainz id as the key.
        # csv headers: ["artist","name","country","lifespan"]
        # All data was validated on creation, so there's no need to validate here
        start, end = row[3].split(" ")
        a = dict(
            id=row[0],
            name=row[1],
            country=row[2],
            # Some bands don't have an end date. (still active)
            # Since the data was created with javascript, those fields are undefined
            # So we just switch them for python's none
            lifespan=(start, (end if end != "undefined" else None))
        )
        ARTISTS[a['id']] = a
        TEXTINDEX[a['name']] = {
            "id": a['id'],
            "type": "artists",
            "name": a['name']
        }
        # Add the first letter to the index
        first = a['name'][0].lower()
        LETTERS[first] = (LETTERS[first] + 1) if first in LETTERS else 1

with open(DATA_DIR + "/releases.csv") as file:
    reader = csv.reader(file, delimiter=',', quotechar='"')
    # skip headers
    next(reader)
    for row in reader:
        # Add releases to the dict, using their musicbrainz id as the key.
        # csv headers: ["artist","relgroup","name","reldate","mainrel","frontcover","backcover"]
        # All data was validated on creation, so there's no need to validate here.
        # We store the id of a release's artist, rather than a pointer to it in ARTISTS
        # to simulate a case where looking it up would be expensive (e.g: database)

        # Even though a release on musicbrainz is called a release group and is associated with multiple
        # releases, for this use case, we don't care about that,
        # so we index the release by "mainrel" rather than "relgroup"
        r = dict(
            id=row[4],
            relgroup=row[1],
            artist=row[0],
            name=row[2],
            reldate=row[3],
            cover=(row[5], row[6])
        )
        RELEASES[r["id"]] = r
        # Indices
        # Text index
        TEXTINDEX[r['name']] = {
            "id": r['id'],
            "type": "releases",
            "name": r['name']
        }
        # Index to artist
        if r["artist"] in ARTIST_TO_RELEASES:
            ARTIST_TO_RELEASES[r["artist"]].append(r["id"])
        else:
            ARTIST_TO_RELEASES[r["artist"]] = [r["id"]]

        # Add the first letter to the index
        first = r['name'][0].lower()
        RELEASE_LETTERS[first] = (RELEASE_LETTERS[first] + 1) if first in RELEASE_LETTERS else 1

with open(DATA_DIR + "/tracks.csv") as file:
    reader = csv.reader(file, delimiter=',', quotechar='"')
    # skip headers
    next(reader)
    for row in reader:
        # Add tracks to the dict, using their musicbrainz id as the key.
        # csv headers: ["release","format","track","name","position","duration"]
        # All data was validated on creation, so there's no need to validate here.
        # We store the id of a tracks's release, rather than a pointer to it in RELEASES
        # to simulate a case where looking it up would be expensive (e.g: database)

        # We index using track
        t = dict(
            id=row[2],
            release=row[0],
            format=row[1],
            name=row[3],
            position=int(row[4]) if row[4] != "" else -1,
            duration=int(row[5]) if row[5] != "null" else 0
        )
        t["artist"] = RELEASES[t["release"]]["artist"]
        TRACKS[t["id"]] = t
        # Indices
        # Text index
        TEXTINDEX[t['name']] = {
            "id": t['id'],
            "type": "tracks",
            "name": t['name']
        }
        # Index to artist
        if t["artist"] in ARTIST_TO_TRACKS:
            ARTIST_TO_TRACKS[t["artist"]].append(t["id"])
        else:
            ARTIST_TO_TRACKS[t["artist"]] = [t["id"]]

        # Index to release
        if t["release"] in RELEASE_TO_TRACKS:
            RELEASE_TO_TRACKS[t["release"]].append(t["id"])
        else:
            RELEASE_TO_TRACKS[t["release"]] = [t["id"]]

with open(DATA_DIR + "/acousticbrainz.csv") as file:
    reader = csv.reader(file, delimiter=',', quotechar='"')
    # skip headers
    next(reader)
    for row in reader:
        # Add acoustic data to the dict, using their musicbrainz id as the key.
        # csv headers: ["id","bpm","loudness","chordchange","chordkey","songkey","keystrenght"]
        # All data was validated on creation, so there's no need to validate here.
        # We store the id of a tracks's release, rather than a pointer to it in RELEASES
        # to simulate a case where looking it up would be expensive (e.g: database)

        # We index using track
        ac = dict(
            id=row[0],
            bpm=row[1],
            loudness=row[2],
            chord_change_rate=row[3],
            chord_key=row[4],
            song_key=row[5],
            key_strength=row[6]
        )

        ACOUSTICS[ac["id"]] = ac
        # Indices
        # ACOUSTICS doesn't need indices because it uses the same ID as tracks
        # and it's already an O(1) lookup between them


def get_releases(artist):
    if artist['id'] in ARTIST_TO_RELEASES:
        return ARTIST_TO_RELEASES[artist['id']]
    else:
        return []


def get_tracks(release):
    if release['id'] in RELEASE_TO_TRACKS:
        return RELEASE_TO_TRACKS[release['id']]
    else:
        return []


# Lookup entities in their specific dicts
def artist_fetcher(id):
    return ARTISTS[id]


def release_fetcher(id):
    return RELEASES[id]


def track_fetcher(id):
    return TRACKS[id]


search_result_entity_fetcher = {
    "artists": artist_fetcher,
    "releases": release_fetcher,
    "tracks": track_fetcher,
}


# Generate messages for different entity types
def artist_message(id):
    return "<small>Artist</small>"


def release_message(id):
    artist = RELEASES[id]['artist']
    bandname = ARTISTS[artist]['name']
    return "<small>Release by Artist: " + bandname + "</small>"


def track_message(id):
    release = TRACKS[id]['release']
    artist = RELEASES[release]['artist']
    bandname = ARTISTS[artist]['name']
    return "<small>Track by Artist: " + bandname + ", in " + RELEASES[release]['name'] + "</small>"


search_result_message_builder = {
    "artists": artist_message,
    "releases": release_message,
    "tracks": track_message,
}


# Search in the TEXTINDEX for the best matches
# Output is streamed by using a generator function
def search_results_for(query, stream=False):
    # when stream == True, we yield an <a/> for matches over 0.6
    print("searching: " + query)
    if stream:
        for (k, v) in TEXTINDEX.items():
            match = SequenceMatcher(None, k.lower(), query.lower())
            if match.ratio() > 0.6:
                if v['type'] == 'tracks':
                    t = TRACKS[v['id']]
                    yield '<a data-score="' + str(match.ratio()) + '" href="/releases/' + t[
                        'release'] + '?highlight=' + v['id'] + '"><p>' + \
                          v['name'] + "</p>" + search_result_message_builder[v['type']](v['id']) + "</a>"
                else:
                    yield '<a data-score="' + str(match.ratio()) + '" href="/' + v['type'] + "/" + v[
                        'id'] + '"><p>' + \
                          v['name'] + "</p>" + search_result_message_builder[v['type']](v['id']) + "</a>"
    # If not, we still yield, but we have a cap of 50 results or 3 seconds, whichever comes first
    # Also the results are in a different shape, the one the searc_results.html template expects
    else:
        count = 0
        start_time = time.time()
        for (k, v) in TEXTINDEX.items():
            # Break if we have more than 50 results or 3 seconds have passed
            if count >= 50 or (time.time() - start_time > 3):
                break
            match = SequenceMatcher(None, k, query)
            if match.ratio() > 0.4:
                entity = search_result_entity_fetcher[v['type']](v['id'])
                count += 1
                yield dict(score=match.ratio(), type=v['type'], entity=entity)
