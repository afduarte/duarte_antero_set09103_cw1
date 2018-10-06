from settings import DATA_DIR
import csv

ARTISTS = {}
RELEASES = {}
with open(DATA_DIR + "/artists.csv") as file:
    reader = csv.reader(file, delimiter=',', quotechar='"')
    # skip headers
    next(reader)
    for row in reader:
        # Add artists to the dict, using their musicbrainz id as the key.
        # csv headers: ["artist","name","country","lifespan"]
        # All data was validated on creation, so there's no need to validate here
        start, end = row[3].split(" ")
        ARTISTS[row[0]] = dict(
            id=row[0],
            name=row[1],
            country=row[2],
            # Some bands don't have an end date. (still active)
            # Since the data was created with javascript, those fields are undefined
            # So we just switch them for python's none
            lifespan=(start, end if end != "untitled" else None)
        )

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
        RELEASES[row[4]] = dict(
            id=row[2],
            relgroup=row[1],
            artist=row[0],
            name=row[2],
            reldate=row[3],
            cover=(row[5], row[6])
        )
