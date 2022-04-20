import os
import time
from datetime import datetime
from typing import List, Union

from dotenv import load_dotenv
from plexapi.library import MovieSection, ShowSection
from plexapi.server import PlexServer
from plexapi.video import Movie, Show

load_dotenv()


CONFIG = {
    "PLEX_URL": os.getenv("PLEX_URL"),
    "PLEX_TOKEN": os.getenv("PLEX_TOKEN"),
    "MOVIES_LIB": os.getenv("MOVIES_LIB"),
    "SHOWS_LIB": os.getenv("SHOWS_LIB"),
    "LABEL_4K": os.getenv("LABEL_4K"),
    "INTERVAL": os.getenv("INTERVAL"),  # minutes
}


def label_item(item: Union[Movie, Show]):
    """
    Add the 4K label to a movie or show
    """
    if CONFIG["LABEL_4K"] in [label.tag for label in item.labels]:
        print(f"{item.title} -- Already tagged with '{CONFIG['LABEL_4K']}'")
    else:
        print(f"{item.title} -- Adding new tag '{CONFIG['LABEL_4K']}'")
        item.addLabel(CONFIG["LABEL_4K"])


def label_movies(movies: MovieSection):
    """
    Add the 4K label to all 4K movies
    """
    results: List[Movie] = movies.search(resolution="4k", sort="titleSort")
    for movie in results:
        resolutions = [m.videoResolution for m in movie.media]
        if "4k" in resolutions:
            label_item(movie)


def label_shows(shows: ShowSection):
    """
    Add the 4K label to all shows that have at least one 4K episode
    """
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
            label_item(show)


def run():
    """
    Run the 4K labeler
    """

    print("Running Library Scan:")
    print(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
    plex = PlexServer(CONFIG["PLEX_URL"], CONFIG["PLEX_TOKEN"])

    print("\n*****************")
    print("*    Movies     *")
    print("*****************\n")
    label_movies(plex.library.section(CONFIG["MOVIES_LIB"]))

    print("\n*****************")
    print("*   TV Shows   *")
    print("*****************\n")
    label_shows(plex.library.section(CONFIG["SHOWS_LIB"]))

    print("\nFinished Scanning Library\n")


if __name__ == "__main__":

    for item in CONFIG:
        if CONFIG[item] is None:
            raise ValueError(f"Missing value for {item}")

    interval_seconds = float(CONFIG["INTERVAL"]) * 60  # type: ignore

    while True:
        run()
        print(f"Run again in {CONFIG['INTERVAL']} minutes\n")
        time.sleep(interval_seconds)
