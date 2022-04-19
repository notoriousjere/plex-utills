from typing import List, Union
from plexapi.server import PlexServer
from plexapi.library import MovieSection, ShowSection
from plexapi.video import Movie, Show



MOVIES_LIB = "Movies"
SHOWS_LIB = "TV Shows"
LABEL_4K = "4K"


plex = PlexServer(PLEX_URL, PLEX_TOKEN)


def tag_item(item: Union[Movie, Show]):
    if "4K" in [label.tag for label in item.labels]:
        print(f"{item.title}: Already tagged with '4K'")
    else:
        print(f"{item.title}: Adding new tag '4K'")
        item.addLabel(LABEL_4K)


def tag_movies(movies: MovieSection):
    results: List[Movie] = movies.search(resolution="4k", sort="titleSort")
    for movie in results:
        resolutions = [m.videoResolution for m in movie.media]
        if "4k" in resolutions:
            tag_item(movie)


def tag_shows(shows: ShowSection):
    results: List[Show] = shows.search(resolution="4k", sort="titleSort")
    for show in results:
        contains_4k = False
        episodes = show.episodes()
        for episode in episodes:
            resolutions = [e.videoResolution for e in episode.media]
            if "4k" in resolutions:
                contains_4k = True
                break
        if contains_4k:
            tag_item(show)


print("*****************")
print("*    Movies     *")
print("*****************\n")
tag_movies(plex.library.section(MOVIES_LIB))

print("\n*****************")
print("*   TV Shows    *")
print("*****************\n")
tag_shows(plex.library.section(SHOWS_LIB))
