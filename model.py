from settings import DATA_DIR
from flask import url_for
import csv
from difflib import SequenceMatcher

ARTISTS = {}
RELEASES = {}
TRACKS = {}

# Indices, for faster lookups

# Index artists to their releases
ARTIST_TO_RELEASES = {}
ARTIST_TO_TRACKS = {}
TEXTINDEX = {}

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
        # Indicies
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
            position=row[4],
            duration=row[5]
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


def get_releases(artist):
    # add 1 random release for each artist
    # if the artist has indexed releases
    if artist['id'] in ARTIST_TO_RELEASES:
        return ARTIST_TO_RELEASES[artist['id']]
    else:
        return []


def search_results_for(query):
    for (k, v) in TEXTINDEX.items():
        match = SequenceMatcher(None, k, query)
        print(query, match.ratio(), k)
        if match.ratio() > 0.6:
            yield "<a data-score=\"" + str(match.ratio()) + "\" href=\"/" + v['type'] + "/" + v['id'] + "\">" + v[
                'name'] + "</a>"
