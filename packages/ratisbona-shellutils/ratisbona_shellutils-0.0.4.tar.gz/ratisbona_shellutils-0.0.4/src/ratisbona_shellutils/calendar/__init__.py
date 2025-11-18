"""
    A package that contains ratisbona_gcalendar, a command line interface that can sync git logs to google calendar,
    list calendars, list events, enter events, sync all commit dates of a gitlog into a google-calendar
    or sync the date of files the names of which are to start out by an iso-date to a google-calendar.
"""

from ._gitlogging import find_git_root, get_git_log

from ._google_calendar import try_parse_datetimes

