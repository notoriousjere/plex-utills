from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from app.scripts import (
    posters4k,
    posters3d,
    hide4k,
    tv4kposter,
    migrate,
    restore_posters,
    fresh_hdr_posters,
    setup_logger,
    autocollections,
    remove_unused_backup_files,
    recently_added_posters,
    test_script,
)
import os
from flask_apscheduler import APScheduler
import sqlite3
import logging
import shutil
from plexapi.server import PlexServer
import re
import plexapi
import tzlocal
import time
from apscheduler.triggers.cron import CronTrigger
from croniter import croniter

setup_logger("Application", r"/logs/application_log.log")
log = logging.getLogger("Application")


def setup_helper():
    def continue_setup():
        def add_new_columns():
            log.debug("Adding new Columns")
            conn = sqlite3.connect("/config/app.db")
            c = conn.cursor()
            c.execute("SELECT * FROM plex_utills")
            config = c.fetchall()
            query1 = """ALTER TABLE plex_utills
                    ADD COLUMN autocollections INT
                    """
            query2 = """ALTER TABLE plex_utills        
                    ADD COLUMN default_poster INT
                    """
            query3 = """ALTER TABLE plex_utills        
                    ADD COLUMN tr_r_p_collection INT
                    """
            query4 = """ALTER TABLE plex_utills    
                    ADD COLUMN tautulli_server TEXT
                    """
            query5 = """ALTER TABLE plex_utills    
                    ADD COLUMN tautulli_api TEXT
                    """
            query6 = """ALTER TABLE plex_utills    
                        ADD COLUMN mcu_collection INT
                        """
            query7 = """ALTER TABLE plex_utills    
                        ADD COLUMN audio_posters INT
                        """
            query8 = """ALTER TABLE plex_utills    
                    ADD COLUMN loglevel INT
                    """
            query9 = """ALTER TABLE plex_utills    
                    ADD COLUMN manualplexpath INT
                    """
            query10 = """ALTER TABLE plex_utills    
                    ADD COLUMN manualplexpathfield TEXT
                    """
            try:
                c.execute(query1)
            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                c.execute(query2)
            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                c.execute(query3)
            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                c.execute(query4)

            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                c.execute(query5)
            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                c.execute(query6)
            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                c.execute(query7)
            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                c.execute(query8)

            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                c.execute(query9)

            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                c.execute(query10)
            except sqlite3.OperationalError as e:
                log.debug(repr(e))
            try:
                api = config[0][32]
                loglevel = config[0][36]
                manpp = config[0][37]
                if not api:
                    c.execute(
                        "UPDATE plex_utills SET tautulli_server = 'http://127.0.0.1:8181' where ID = 1"
                    )
                if not loglevel:
                    c.execute("UPDATE plex_utills SET loglevel = '0' WHERE ID = 1")
                if not manpp:
                    c.execute(
                        "UPDATE plex_utills SET manualplexpath = '0' WHERE ID = 1"
                    )
                    c.execute(
                        "UPDATE plex_utills SET manualplexpathfield = 'None' WHERE ID = 1"
                    )
                conn.commit()
            except (sqlite3.OperationalError, IndexError) as e:
                log.debug(e)
            c.close()

        def update_plex_path():
            log.debug("update plex path")
            import requests

            try:
                conn = sqlite3.connect("/config/app.db")
                c = conn.cursor()
                c.execute("SELECT * FROM plex_utills")
                config = c.fetchall()
                plex = PlexServer(config[0][1], config[0][2])
                lib = config[0][3].split(",")
                if len(lib) <= 2:
                    try:
                        films = plex.library.section(lib[0])
                    except IndexError:
                        pass
                else:
                    films = plex.library.section(config[0][3])
                media_location = films.search(limit="1")

                if config[0][37] == 1:
                    log.info("Plexpath Manual override enabled")
                    plexpath = config[0][38]
                    log.debug(plexpath)
                    log.debug("plexpath = " + plexpath)
                    c.execute(
                        "UPDATE plex_utills SET plexpath = '"
                        + plexpath
                        + "' WHERE ID = 1;"
                    )
                    conn.commit()
                    c.close()
                    log.info(
                        "Setup Helper: Your plexpath has been changed from "
                        + plexpath
                        + " to '/films'"
                    )
                elif config[0][37] == 0:
                    filepath = os.path.dirname(
                        os.path.dirname(media_location[0].media[0].parts[0].file)
                    )
                    log.debug("Plex Movie location is: " + filepath)
                    try:
                        plexpath = "/" + filepath.split("/")[2]
                        plexpath = "/" + filepath.split("/")[1]
                        log.debug("plexpath split = " + plexpath)
                        log.debug("Testing to see if plexpath is mounted at root")
                    except IndexError as e:
                        log.debug(e)
                        plexpath = "/"
                    log.debug("plexpath = " + plexpath)
                    c.execute(
                        "UPDATE plex_utills SET plexpath = '"
                        + plexpath
                        + "' WHERE ID = 1;"
                    )
                    conn.commit()
                    c.close()
                    log.info(
                        "Setup Helper: Your plexpath has been changed from "
                        + plexpath
                        + " to '/films'"
                    )
            except requests.exceptions.ConnectionError:
                log.debug("This looks like a first run")

        def update_database():
            log.debug("update database")
            try:
                conn = sqlite3.connect("/config/app.db")
                c = conn.cursor()
                c.execute("SELECT * FROM plex_utills")
                config = c.fetchall()
                plex = PlexServer(config[0][1], config[0][2])
                lib = config[0][3].split(",")
                if len(lib) <= 2:
                    try:
                        films = plex.library.section(lib[0])
                    except IndexError:
                        pass
                else:
                    films = plex.library.section(config[0][3])
                media_location = films.search(limit="1")
                for i in media_location:
                    if config[0][37] == 1:
                        log.debug(i.media[0].parts[0].file)
                        newdir = (
                            os.path.dirname(
                                re.sub(config[0][5], "/films", i.media[0].parts[0].file)
                            )
                            + "/"
                        )
                        log.debug(newdir)
                    elif config[0][37] == 0:
                        if config[0][5] == "/":
                            newdir = "/films" + i.media[0].parts[0].file
                            log.debug(newdir)
                        else:
                            newdir = (
                                os.path.dirname(
                                    re.sub(
                                        config[0][5], "/films", i.media[0].parts[0].file
                                    )
                                )
                                + "/"
                            )
                            log.debug(newdir)
                    testfile = newdir + "test"
                    log.debug("Plex-Utills file path is here: " + newdir)
                    try:
                        open(testfile, "w")
                        log.info("Permissions, look to be correct")
                    except PermissionError as e:
                        log.error(e)
                    if os.path.exists(testfile) == True:
                        os.remove(testfile)
                    break
            except (
                plexapi.exceptions.NotFound,
                OSError,
                ConnectionError,
                NameError,
            ) as e:
                log.error(e)

        add_new_columns()
        update_plex_path()
        update_database()

    def create_table():
        shutil.copy("app/static/default_db/default_app.db", "/config/app.db")
        log.debug("Copying table")
        continue_setup()

    def table_check():
        try:
            conn = sqlite3.connect("/config/app.db")
            c = conn.cursor()
            c.execute("SELECT * FROM plex_utills")
            c.close()
            continue_setup()
        except sqlite3.OperationalError as e:
            log.debug(e)
            create_table()

    log.debug("Running setup Helper")
    table_check()


def update_scheduler():

    log.debug("Running Updater")
    scheduler.remove_all_jobs()
    conn = sqlite3.connect("/config/app.db")
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()

    def check_schedule_format(input):
        try:
            time.strptime(input, "%H:%M")
            return "time trigger"
        except ValueError:
            if croniter.is_valid(input) == True:
                return "cron"
            else:
                return log.error("Schedule for t1 is incorrect")

    t1 = config[0][7]
    t2 = config[0][8]
    # t3 = config[0][9]
    t4 = config[0][10]
    t5 = config[0][11]
    if config[0][13] == 1:
        if check_schedule_format(t1) == "time trigger":
            scheduler.add_job(
                "posters4k",
                func=posters4k,
                trigger="cron",
                hour=t1.split(":")[0],
                minute=t1.split(":")[1],
            )
        elif check_schedule_format(t1) == "cron":
            scheduler.add_job(
                "posters4k", func=posters4k, trigger=CronTrigger.from_crontab(t1)
            )
        log.info("4K/HDR Posters schedule created for " + t1)
    if config[0][16] == 1:
        if check_schedule_format(t5) == "time trigger":
            scheduler.add_job(
                "posters3d",
                func=posters3d,
                trigger="cron",
                hour=t5.split(":")[0],
                minute=t5.split(":")[1],
            )
        elif check_schedule_format(t5) == "cron":
            scheduler.add_job(
                "posters3d", func=posters3d, trigger=CronTrigger.from_crontab(t5)
            )
        log.info("3D Posters schedule created for " + t5)
    if config[0][20] == 1:
        if check_schedule_format(t4) == "time trigger":
            scheduler.add_job(
                "hide4k",
                func=hide4k,
                trigger="cron",
                hour=t4.split(":")[0],
                minute=t4.split(":")[1],
            )
        elif check_schedule_format(t4) == "cron":
            scheduler.add_job(
                "hide4k", func=hide4k, trigger=CronTrigger.from_crontab(t4)
            )
        log.info("Hide 4k schedule created for " + t4)
    if config[0][18] == 1:
        if check_schedule_format(t2) == "time trigger":
            scheduler.add_job(
                "autocollections",
                func=autocollections,
                trigger="cron",
                hour=t2.split(":")[0],
                minute=t2.split(":")[1],
            )
        elif check_schedule_format(t2) == "cron":
            scheduler.add_job(
                "autocollections",
                func=autocollections,
                trigger=CronTrigger.from_crontab(t2),
            )
        log.info("Auto Collections schedule created for " + t2)
    for j in scheduler.get_jobs():
        log.info(j)

    def update_plex_path():
        conn = sqlite3.connect("/config/app.db")
        c = conn.cursor()
        c.execute("SELECT * FROM plex_utills")
        plex = PlexServer(config[0][1], config[0][2])
        lib = config[0][3].split(",")
        if len(lib) <= 2:
            try:
                films = plex.library.section(lib[0])
            except IndexError:
                pass
        else:
            films = plex.library.section(config[0][3])
        media_location = films.search(limit="1")
        log.debug("Updating plex path")
        if config[0][37] == 1:
            log.info("Plexpath Manual override enabled")
            plexpath = config[0][38]
        elif config[0][37] == 0:
            filepath = os.path.dirname(
                os.path.dirname(media_location[0].media[0].parts[0].file)
            )
            log.debug("Plex Movie location is: " + filepath)
            try:
                plexpath = "/" + filepath.split("/")[2]
                plexpath = "/" + filepath.split("/")[1]
                log.debug("plexpath split = " + plexpath)
                log.debug("Testing to see if plexpath is mounted at root")
            except IndexError as e:
                log.debug(e)
                plexpath = "/"
        log.debug("plexpath = " + plexpath)
        c.execute("UPDATE plex_utills SET plexpath = '" + plexpath + "' WHERE ID = 1;")
        conn.commit()
        c.close()
        log.info(
            "Setup Helper: Your plexpath has been changed from "
            + plexpath
            + " to '/films'"
        )

    try:
        update_plex_path()
    except (plexapi.exceptions.NotFound, OSError) as e:
        log.error(e)


class Plex_utills(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv("WERKZEUG_RUN_MAIN") == "true":
            with self.app_context():
                setup_helper()
        super(Plex_utills, self).run(host=host, port=port, debug=debug, **options)


timezone = str(tzlocal.get_localzone())


class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = timezone


app = Plex_utills(__name__)
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
setup_helper()
update_scheduler()
if __name__ == "__main__":
    app.run()


app.secret_key = "_3:WBH)qdY2WDe-_/h9r6)BD(Mp$SX"  # os.urandom(42)


Bootstrap(app)
db_name = "/config/app.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_name
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

from app import routes
