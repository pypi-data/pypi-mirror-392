"""
Google Calendar API utilities for Ratisbona Shell Utils.
This module provides functions to authenticate with Google Calendar API,
list calendars, manage events, and format calendar data for UI display.
"""

import pickle
import re
from datetime import datetime, date, timedelta, time
from functools import partial
from typing import Any, Optional, Sequence

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from ratisbona_utils.colors import RGBColor, hex_to_rgb
from ratisbona_utils.datetime import (
    to_datetime,
    ensure_timezone,
    ensure_no_timezone,
    lenient_tokenizer,
    leniently_parse,
)
from ratisbona_utils.datetime._datetime_utils import (
    DateTimeLike,
    maybe_extract_date,
    maybe_extract_time,
)
from ratisbona_utils.functional import Function, Provider
from ratisbona_utils.io import get_config_dir
from ratisbona_utils.monads import Just, Nothing, Maybe
from ratisbona_utils.parsing import Token
from ratisbona_utils.strings import indent, wrap_text
from ratisbona_utils.terminals.vt100 import color_block

from ratisbona_shellutils.dialogator.chatgpt_parsing import debug_print_message

DEBUG = True

# https://console.cloud.google.com/workspace-api/credentials?inv=1&invt=AbnYUA&project=calclient

# Define the scope for Google Calendar API
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_DIR = get_config_dir("ratisbona_calendar")
TOKEN_FILE = TOKEN_DIR / "token.pickle"
CREDENTIALS_FILE = TOKEN_DIR / "credentials.json"  # Place your credentials.json here

# Type aliases
CalendarService = Any
CalendarEvent = dict
CalendarEntry = dict
Calendar = dict
DateSpec = dict
DateTimeSpec = dict
EventId = str


def authenticate() -> CalendarService:
    """
    Authenticates the user with Google OAuth 2.0 and returns a service object to interact with Google Calendar API.
    Tokens are saved in TOKEN_DIR.

    Args:
        None

    Returns:
        CalendarService: An authenticated service object to interact with Google Calendar API.

    Raises:
        FileNotFoundError: If the credentials file does not exist.
        AuthError: If there is an error during the authentication process.

    Side Effects:
        Creates a token file in TOKEN_DIR if authentication is successful.
        Prompts the user to log in via a web browser if no valid token is found.

    """
    creds = None

    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_FILE}")

    # Load existing token if available
    if TOKEN_FILE.exists():
        with TOKEN_FILE.open("rb") as token:
            creds = pickle.load(token)

    # Refresh or generate a new token if necessary
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as error:
                print(f"Cannot refresh token: {error}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES
                )
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the new token
        with TOKEN_FILE.open("wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)


def ui_format_calendar(calendar: Calendar) -> str:
    """
    Formats a calendar for UI display.

    Args:
        calendar (Calendar): The calendar object containing details like summary and id.

    Returns:
        str: A formatted string representing the calendar, might contain ansi color sequences!
    """
    maybe_color = get_color(calendar)
    the_color_block = maybe_color.bind(color_block).default_or_throw(" ")
    return f"{the_color_block} {calendar['summary']} - {calendar['id']}"


def maybe_infer_start_end_datetime(
    start_spec: Maybe[DateTimeLike],
    end_spec: Maybe[DateTimeLike],
    *,
    base_date_for_implicit_dates: Provider[datetime],
) -> tuple[Maybe[datetime | date], Maybe[datetime | date]]:

    if not start_spec:
        return Nothing, Nothing

    start_date = (
        start_spec
        .bind(maybe_extract_date)
        .default_or_throw(
            base_date_for_implicit_dates().date()
        )
    )

    maybe_start_time = start_spec.bind(maybe_extract_time)
    maybe_end_date = end_spec.bind(maybe_extract_date)
    maybe_end_time = end_spec.bind(maybe_extract_time)
    end_date, maybe_end_time = maybe_infer_end_date_and_time(
        maybe_end_date, maybe_end_time, start_date, maybe_start_time
    )

    if maybe_start_time and maybe_end_time:
        return (
            Just(datetime.combine(start_date, maybe_start_time.unwrap_value())),
            Just(datetime.combine(end_date, maybe_end_time.unwrap_value())),
        )

    return Just(start_date), Just(end_date)


def maybe_infer_end_date_and_time(
    maybe_end_date: Maybe[date],
    maybe_end_time: Maybe[time],
    start_date: date,
    maybe_start_time: Maybe[time],
) -> tuple[date, Maybe[time]]:
    """
    Infers the end date and time based on the start date and time.

    If end_date is not provided, it defaults to start_date.

    If end_time is not provided but start_time is, then it defaults to the end of the day if the end_date is after the start_date,
    or to one hour after the start_time if the end_date is the same as the start_date.

    If start_time is not provided, it does not affect the end_time inference.

    Args:
        end_date (Optional[date]): The end date of the event.
        end_time (Optional[time]): The end time of the event.
        start_date (date): The start date of the event.
        start_time (Optional[time]): The start time of the event.

    Returns:
        Tuple[date, time]: A tuple containing the inferred end date and end time.
    """
    end_date = maybe_end_date.default_or_throw(start_date)

    if maybe_start_time and not maybe_end_time:
        if end_date > start_date:
            maybe_end_time = Just(time(23, 59, 59))
        else:
            end_datetime = datetime.combine(
                start_date, maybe_start_time.unwrap_value()
            ) + timedelta(hours=1)
            end_date = end_datetime.date()
            maybe_end_time = Just(end_datetime.time())

    if end_date == start_date and maybe_end_time and maybe_start_time:
        if maybe_end_time.unwrap_value() <= maybe_start_time.unwrap_value():
            end_date = end_date + timedelta(days=1)

    return end_date, maybe_end_time


def list_calendars(service: CalendarService) -> list[Calendar]:
    """
    Lists all available calendars.

    Args:
        service (CalendarService): An authenticated service object to interact with Google Calendar API.
    Returns:
        list[Calendar]: A sorted by summary list of calendars, each represented as a dictionary.
    """

    calendars = list(service.calendarList().list().execute().get("items", []))
    calendars.sort(key=lambda calendar: calendar.get("summary", ""))
    return calendars


def find_calendar_by_name(
    name: str, *, calendar_provider: Provider[list[Calendar]]
) -> Maybe[Calendar]:
    """
    Finds the first calendar calendar matching by its name.

    Args:
        name (str): The name or part of a name of the calendar to search for.
        calendar_provider (Provider[list[Calendar]]): A provider function that returns a list of calendars. If in doubt, use lambda: list_calendars(service)

    Returns:
        Maybe[Calendar]: A Maybe object containing the first found calendar if it exists, or Nothing if not found.
    """
    name = name.lower().strip()
    if len(name) == 0:
        return Nothing

    calendars = calendar_provider()
    for calendar in calendars:
        maybe_summary = Just(calendar)["summary"].bind(str.lower)
        if maybe_summary and name in maybe_summary.unwrap_value():
            return Just(calendar)

    return Nothing


def as_datetime(event: CalendarEvent, key: str) -> Maybe[datetime]:
    """
    Converts a datetime string from an event to a datetime object.
    """
    maybe_field = Just(event)[key]
    # maybe_datetime = maybe_field["dateTime"].bind(datetime.fromisoformat) or (
    #    maybe_field["date"].bind(date.fromisoformat).bind(to_datetime)
    # )
    maybe_datetime = (
        maybe_field["dateTime"].bind(datetime.fromisoformat)
        or maybe_field["date"].bind(date.fromisoformat).bind(to_datetime)
        or maybe_field.bind(datetime.fromisoformat)
        or (maybe_field.bind(date.fromisoformat).bind(to_datetime))
    )

    maybe_datetime = maybe_datetime.bind(ensure_timezone)
    maybe_datetime.maybe_warn("Invalid datetime format!")
    return maybe_datetime


def start_datetime(event: CalendarEvent) -> Maybe[datetime]:
    return as_datetime(event, "start")


def end_datetime(event: CalendarEvent) -> Maybe[datetime]:
    return as_datetime(event, "end")


def list_events(
    service: CalendarService,
    time_min: datetime,
    time_max: datetime,
    calendar_id="primary",
    max_results=100,
) -> list[CalendarEvent]:
    """
    Lists upcoming events from the specified calendar.
    """
    time_min = ensure_timezone(time_min)
    time_max = ensure_timezone(time_max)

    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            maxResults=max_results,
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = Just(events_result)["items"]

    if not events:
        return []

    return sorted(
        events.unwrap_value(),
        key=lambda x: start_datetime(x).default_also_on_error(datetime.min),
    )


def insert_event(service: CalendarService, event: CalendarEvent, calendar_id="primary"):
    """
    Inserts an event into the specified calendar.
    :param service: Google Calendar API service object.
    :param event: Event details as a dictionary.
    :param calendar_id: The calendar ID where the event will be inserted.
    :return: The created event.
    """
    created_event = (
        service.events().insert(calendarId=calendar_id, body=event).execute()
    )
    print(f"Event created: {created_event.get('htmlLink')}")
    return created_event


def get_color(calendar: Calendar) -> Maybe[RGBColor]:
    return Just(calendar)["backgroundColor"].bind(hex_to_rgb)


def search_by_date_and_summary_or_description_part(
    calendar_id: str,
    search_text: str,
    start: datetime,
    *,
    service: CalendarService,
    max_results=1000,
    search_description=True,
    timedelta_hours_plusminus=2,
) -> Maybe[CalendarEvent]:
    min_time = start - timedelta(hours=timedelta_hours_plusminus)
    max_time = start + timedelta(hours=timedelta_hours_plusminus)

    events = list_events(
        service, min_time, max_time, calendar_id, max_results=max_results
    )
    for event in events:
        just_event = Just(event)
        if search_text in just_event["summary"].default_also_on_error(""):
            return just_event
        if search_description and search_text in just_event[
            "description"
        ].default_also_on_error(""):
            return just_event
    return Nothing


def spec_by_date(theDate: date) -> DateSpec:
    return {"date": theDate.isoformat()}


def spec_by_datetime(the_datetime: datetime) -> DateTimeSpec:
    return {
        "dateTime": ensure_no_timezone(the_datetime).isoformat(),
        "timeZone": "Europe/Amsterdam",
    }


def spec_by_date_and_maybe_time(
    the_date: date, maybe_time: Optional[time]
) -> DateSpec | DateTimeSpec:
    if maybe_time:
        return spec_by_datetime(datetime.combine(the_date, maybe_time))
    return spec_by_date(the_date)


def create_entry(
    summary: str,
    start_spec: DateSpec | DateTimeSpec,
    end_spec: DateSpec | DateTimeSpec,
    description: Maybe[str] = Nothing,
) -> CalendarEntry:
    body = {"summary": summary, "start": start_spec, "end": end_spec}
    if description:
        body["description"] = description.unwrap_value()
    return body


def nothing_color_function(_: CalendarEvent) -> Maybe[RGBColor]:
    return Nothing


def format_event(
    event: CalendarEvent,
    *,
    colorprovider: Function[CalendarEvent, Maybe[RGBColor]] = nothing_color_function,
) -> str:
    just_event = Just(event)
    colorblockfield = (
        just_event.bind(colorprovider).bind(color_block).default_or_throw(" ")
    )

    start_datetime_field = (
        start_datetime(event)
        .bind(ensure_no_timezone)
        .bind(datetime.strftime, "%Y-%m-%d %H:%M")
        .default_or_throw("-" * 15)
    )
    end_datetime_field = (
        end_datetime(event)
        .bind(ensure_no_timezone)
        .bind(datetime.strftime, "%Y-%m-%d %H:%M")
        .default_or_throw("-" * 15)
    )
    maybe_description = just_event["description"]
    maybe_summary = just_event["summary"]
    maybe_link = just_event["htmlLink"]

    result_text = f"{colorblockfield}{start_datetime_field} - {end_datetime_field}: {maybe_summary.default_or_throw('')}"

    def indent_properly(text: str) -> str:
        return indent(text, 4)

    def wrap_properly(text: str) -> str:
        return wrap_text(text, 76)

    def prepend_newline(text: str) -> str:
        return f"\n{text}"

    result_text += (
        maybe_description.bind(wrap_properly)
        .bind(indent_properly)
        .bind(prepend_newline)
        .default_or_throw("")
    )
    result_text += (
        maybe_link.bind(indent_properly).bind(prepend_newline).default_or_throw("")
    )
    return result_text


SEPARATOR_PATTERN = re.compile(
    r"[\s-]+"
)  # Matches whitespace and dashes.


def try_parse_for_separator(tokens: list[Token]) -> tuple[Maybe[str], list[Token]]:
    if len(tokens) == 0:
        return Nothing, tokens
    first_token = tokens.pop(0)
    if first_token.token_type_name == "Pure Separators":
        return Just(first_token.token_full_match), tokens
    tokens.insert(0, first_token)
    return Nothing, tokens


def try_parse_entry(
    cmdline: str,
    *,
    base_date_for_relative_dates: Provider[datetime],
    base_date_for_implicit_dates: Provider[datetime]
) -> Maybe[CalendarEntry]:
    tokens = list(lenient_tokenizer(cmdline))
    if DEBUG:
        for token in tokens:
            print("   =>", token)
    maybe_start_datetimelike, maybe_end_datetimelike, tokens = try_parse_datetimes(
        tokens,
        base_date_for_relative_dates=base_date_for_relative_dates,
        base_date_for_implicit_dates=base_date_for_implicit_dates
    )
    maybe_start_point, maybe_end_point = maybe_infer_start_end_datetime(
        maybe_start_datetimelike,
        maybe_end_datetimelike,
        base_date_for_implicit_dates=base_date_for_implicit_dates
    )
    if not maybe_start_point or not maybe_end_point:
        return Nothing
    start_value, end_value = (
        maybe_start_point.unwrap_value(),
        maybe_end_point.unwrap_value(),
    )
    if isinstance(start_value, datetime):
        start_spec = spec_by_datetime(start_value)
        end_spec = spec_by_datetime(end_value)
    else:
        start_spec = spec_by_date(start_value)
        end_spec = spec_by_date(end_value)

    summary = " ".join([token.token_full_match for token in tokens])
    return Just(create_entry(summary, start_spec, end_spec, Just(summary)))


def try_parse_datetimes(
    tokens: list[Token],
    *,
    base_date_for_relative_dates: Provider[datetime],
    base_date_for_implicit_dates: Provider[datetime]
) -> tuple[Maybe[datetime | date | time], Maybe[datetime | date | time], Sequence[Token]]:
    """
        Parses a start and maybe an end from a tokensequence, maybe provided by the lenient_tokenizer function.
        Searches for something datelike, timelike or datetimelike
        followed by a sequence of Pure Separators,
        followed maybe by an end datelike, timelike or datetimelike


        Args:
            tokens: the tokensequence, maybe use lenient_tokenizer function to tokenize a str.
            base_date_for_relative_dates: the base date for relative dates. like "yesterday".
            base_date_for_implicit_dates: the base date for implicit dates. like "18:00" without specifying a date.

        Returns:
            a tuple of maybe start and maybe end dates as well as leftover tokens.

    """
    maybe_start, tokens = leniently_parse(
        tokens,
        base_date_for_relative_dates=base_date_for_relative_dates,
        base_date_for_implicit_dates=base_date_for_implicit_dates
    )
    if not maybe_start:
        debug_print_message("parse_datetimes: no start date found, bailing out.")
        return Nothing, Nothing, tokens
    debug_print_message("parse_datetimes: searching for separator...")
    maybe_dashlike, tokens = try_parse_for_separator(tokens)
    if not maybe_dashlike:
        debug_print_message("parse_datetimes: no separator found, assuming only start given.")
        return maybe_start, Nothing, tokens
    maybe_end, tokens = leniently_parse(
        tokens,
        base_date_for_relative_dates=base_date_for_relative_dates,
        base_date_for_implicit_dates=base_date_for_implicit_dates
    )
    maybe_dashlike, tokens = try_parse_for_separator(tokens)
    if maybe_dashlike:
        debug_print_message("parse_datetimes: ate separator: {maybe_dashlike}")
    else:
        debug_print_message("parse_datetimes: no separator eating necessary.")
    return maybe_start, maybe_end, tokens

def calendar_details_by_name_or_die(calendar_name, service) -> tuple[str, Maybe[RGBColor]]:
    calendar_provider = partial(list_calendars, service=service)
    maybe_calendar = find_calendar_by_name(calendar_name, calendar_provider=calendar_provider)
    maybe_calendar_id = maybe_calendar["id"]
    if not maybe_calendar_id:
        raise ValueError(
            f"Calendar {calendar_name} not found. Maybe use list_calendars to find the correct name."
        )
    calendar_id = maybe_calendar_id.unwrap_value()
    maybe_color = maybe_calendar.bind(get_color)
    return calendar_id, maybe_color

if __name__ == "__main__":
    # Authenticate and build the service
    calendar_service = authenticate()

    # Example usage: List upcoming events
    print("Upcoming events:")
    events = list_events(
        calendar_service, datetime.now(), datetime.now() + timedelta(days=30)
    )
    for event in events:
        print(
            f"{start_datetime(event).bind(str).default_or_throw('-' * 25)}"
            f"_-_{end_datetime(event).bind(str).default_or_throw('-' * 25)}"
            f" - {Just(event)['summary'].default_or_throw('-- no summary --')}"
        )

    # Example usage: Insert a new event
    new_event = {
        "summary": "Sample Event",
        "location": "123 Main St, Anytown, USA",
        "description": "A test event.",
        "start": {
            "dateTime": "2025-01-25T10:00:00-05:00",
            "timeZone": "America/New_York",
        },
        "end": {
            "dateTime": "2025-01-25T11:00:00-05:00",
            "timeZone": "America/New_York",
        },
        "attendees": [
            {"email": "example@example.com"},
        ],
    }

    print("Inserting new event:")
    # insert_event(calendar_service, new_event)
