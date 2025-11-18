import unittest
import datetime

from ratisbona_utils.datetime import lenient_tokenizer
from ratisbona_shellutils.calendar import try_parse_datetimes
from ratisbona_shellutils.calendar._google_calendar import try_parse_entry


def relative_date_provider():
    return datetime.datetime(2020, 1, 1)

def implicit_date_provider():
    return datetime.datetime(2019, 12, 31)

class GoogleCalendarTestCase(unittest.TestCase):

    def test_parse_datetimes_must_be_able_to_yield_start_and_end_dates_for_relative(self):

        given = "heute, 8:30-17:30: Arbeiten"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.datetime(2020, 1, 1, 8, 30))
        self.assertEqual(maybe_end, datetime.time(17, 30))

    def test_parse_datetimes_must_be_able_to_yield_start_and_end_dates_for_implicit(self):

        given = "8:30-17:30: Arbeiten"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.time(8, 30))
        self.assertEqual(maybe_end, datetime.time(17, 30))

    def test_parse_datetimes_must_handle_two_datetimes_with_space_separator(self):
        given="1.1.2001 8:30 31.12.2024 9:14"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.datetime(2001, 1, 1, 8, 30))
        self.assertEqual(maybe_end, datetime.datetime(2024, 12, 31, 9, 14))

    def test_parse_datetimes_must_handle_two_datetimes_with_dash_and_spaceseparator(self):
        given = "1.1.2001 8:30 - 31.12.2024 9:14"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.datetime(2001, 1, 1, 8, 30))
        self.assertEqual(maybe_end, datetime.datetime(2024, 12, 31, 9, 14))


    def test_parse_datetimes_must_handle_two_datetimes_with_dash_only_separator(self):
        given = "1.1.2001 8:30-31.12.2024 9:14"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.datetime(2001, 1, 1, 8, 30))
        self.assertEqual(maybe_end, datetime.datetime(2024, 12, 31, 9, 14))

    def test_parse_datetimes_must_handle_two_datetimes_given_as_isodate(self):
        given = "2001-01-01T08:30:00 2024-12-31T09:14:00"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.datetime(2001, 1, 1, 8, 30))
        self.assertEqual(maybe_end, datetime.datetime(2024, 12, 31, 9, 14))

    def test_parse_datetimes_must_handle_two_dates_given(self):
        given = "2001-01-01-2024-12-31"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(datetime.date(2001, 1, 1), maybe_start)
        self.assertEqual(datetime.date(2024, 12, 31), maybe_end)

    def test_parse_datetimes_allows_datetime_and_date_given(self):
        given = "2001-01-01T08:08:08 2024-12-31"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.datetime(2001, 1, 1, 8, 8, 8))
        self.assertEqual(maybe_end, datetime.date(2024, 12, 31))

    def test_parse_datetimes_allows_date_and_datetime_given(self):
        given = "2001-01-01 2024-12-31T00:31:42"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.date(2001, 1, 1))
        self.assertEqual(maybe_end, datetime.datetime(2024, 12, 31, 0, 31, 42))

    def test_parse_datetimes_must_allow_datetime_followed_by_text(self):
        given = "2001-01-01T08:08:08 Arbeiten"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.datetime(2001, 1, 1, 8, 8, 8))
        self.assertEqual(maybe_end, None)
        self.assertEqual([token.token_full_match for token in tokens], ["Arbeiten"])

    def test_parse_datetimes_must_allow_datetime_immediately_followed_by_text(self):
        given = "2001-01-01T08:08:08=Arbeiten"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, datetime.datetime(2001, 1, 1, 8, 8, 8))
        self.assertEqual(maybe_end, None)
        self.assertEqual([token.token_full_match for token in tokens], ["=Arbeiten"])

    def test_parse_datetimes_must_bail_out_on_no_start_found(self):
        given = "Arbeiten"
        tokens = list(lenient_tokenizer(given))

        maybe_start, maybe_end, tokens = try_parse_datetimes(
            tokens,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual(maybe_start, None)
        self.assertEqual([token.token_full_match for token in tokens], ["Arbeiten"])

    def test_try_parse_entry_must_parse_ordinary_datetime_entry(self):
        given = "2001-01-01T08:12:34 - 2001-01-01T17:56:45 Arbeiten"
        entry = try_parse_entry(
            given,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual("Arbeiten", entry['summary'])
        self.assertEqual(datetime.datetime(2001, 1, 1, 8, 12, 34).isoformat(), entry['start']['dateTime'])
        self.assertEqual(datetime.datetime(2001, 1, 1, 17, 56, 45).isoformat(), entry['end']['dateTime'])

    def test_try_parse_entry_must_bail_out_on_no_start_found(self):
        given = "Arbeiten"
        entry = try_parse_entry(
            given,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertFalse(entry)

    def test_try_parse_entry_must_infer_end_on_only_start_datetime_given(self):
        given = "2001-01-01T08:12:34 Arbeiten"
        entry = try_parse_entry(
            given,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )

        self.assertEqual("Arbeiten", entry['summary'])
        self.assertEqual(datetime.datetime(2001, 1, 1, 8, 12, 34).isoformat(), entry['start']['dateTime'])
        self.assertEqual(datetime.datetime(2001, 1, 1, 9, 12, 34).isoformat(), entry['end']['dateTime'])

    def test_try_parse_entry_must_infer_end_on_only_start_date_given(self):
        given = "2001-01-01 Arbeiten"
        entry = try_parse_entry(
            given,
            base_date_for_implicit_dates=implicit_date_provider,
            base_date_for_relative_dates=relative_date_provider,
        )
        print(entry)
        self.assertEqual("Arbeiten", entry['summary'].unwrap_value())
        self.assertEqual(datetime.date(2001, 1, 1).isoformat(), entry['start']['date'])
        self.assertEqual(datetime.date(2001, 1, 1).isoformat(), entry['end']['date'])


if __name__ == "__main__":
    unittest.main()
