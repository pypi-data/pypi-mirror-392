import datetime
import zoneinfo

import dateutil
import pytest
import time_machine

import marge.interval
from marge.interval import IntervalUnion, WeeklyInterval


def date(spec):
    return dateutil.parser.parse(spec)


class TestWeekly:
    def test_on_same_week(self):
        interval = WeeklyInterval(
            "Mon", datetime.time(10, 00), "Fri", datetime.time(18, 00)
        )
        assert interval.covers(date("Tuesday 3pm"))
        assert not interval.covers(date("Sunday 5pm"))

        assert interval.covers(date("Monday 10am"))
        assert not interval.covers(date("Monday 9:59am"))

        assert interval.covers(date("Friday 6pm"))
        assert not interval.covers(date("Friday 6:01pm"))

    def test_span_two_weeks(self):
        interval = WeeklyInterval(
            "Friday", datetime.time(12, 00), "Mon", datetime.time(7, 00)
        )
        assert interval.covers(date("Sunday 10am"))
        assert not interval.covers(date("Wed 10am"))

        assert interval.covers(date("Friday 12:00pm"))
        assert not interval.covers(date("Friday 11:59am"))

        assert interval.covers(date("Monday 7am"))
        assert not interval.covers(date("Monday 7:01am"))

    def test_from_human(self):
        working_hours = WeeklyInterval(
            "Mon", datetime.time(9, 00), "Fri", datetime.time(17, 0)
        )

        assert WeeklyInterval.from_human("Mon@9am - Fri@5pm") == working_hours
        assert WeeklyInterval.from_human("Monday 9:00 - Friday@17:00") == working_hours
        assert WeeklyInterval.from_human("Mon@9:00-Fri@17:00") == working_hours
        assert WeeklyInterval.from_human("Mon@9:00-Tue@17:00") != working_hours

    def test_from_human_with_timezone(self):
        working_hours = WeeklyInterval(
            "Mon", datetime.time(9, 00), "Fri", datetime.time(17, 0)
        )

        # During summer time
        now = datetime.datetime(2019, 8, 30, tzinfo=zoneinfo.ZoneInfo("Europe/London"))
        with time_machine.travel(now):
            assert (
                WeeklyInterval.from_human(
                    "Mon 10:00 Europe/London - Fri 18:00 Europe/London"
                )
                == working_hours
            )

        # Outside summer time
        now = datetime.datetime(2019, 12, 30, tzinfo=zoneinfo.ZoneInfo("Europe/London"))
        with time_machine.travel(now):
            assert (
                WeeklyInterval.from_human(
                    "Mon 09:00 Europe/London - Fri 17:00 Europe/London"
                )
                == working_hours
            )


class TestIntervalUnion:
    def test_empty(self):
        empty_interval = IntervalUnion.empty()
        assert empty_interval == IntervalUnion([])
        assert not empty_interval.covers(date("Monday 5pm"))

    def test_singleton(self):
        weekly = WeeklyInterval(
            "Mon", datetime.time(10, 00), "Fri", datetime.time(18, 00)
        )
        interval = IntervalUnion([weekly])
        assert interval.covers(date("Tuesday 3pm"))
        assert not interval.covers(date("Sunday 5pm"))

    def test_non_overlapping(self):
        weekly_1 = WeeklyInterval(
            "Mon", datetime.time(10, 00), "Fri", datetime.time(18, 00)
        )
        weekly_2 = WeeklyInterval(
            "Sat", datetime.time(12, 00), "Sun", datetime.time(9, 00)
        )
        interval = IntervalUnion([weekly_1, weekly_2])
        assert interval.covers(date("Tuesday 3pm"))
        assert not interval.covers(date("Saturday 9am"))
        assert interval.covers(date("Saturday 6pm"))
        assert not interval.covers(date("Sunday 11am"))

    def test_from_human(self):
        weekly_1 = WeeklyInterval(
            "Mon", datetime.time(10, 00), "Fri", datetime.time(18, 00)
        )
        weekly_2 = WeeklyInterval(
            "Sat", datetime.time(12, 00), "Sun", datetime.time(9, 00)
        )
        interval = IntervalUnion([weekly_1, weekly_2])

        assert interval == IntervalUnion.from_human(
            "Mon@10am - Fri@6pm,Sat@12pm-Sunday 9am"
        )
        assert IntervalUnion([weekly_1]) == IntervalUnion.from_human(
            "Mon@10am - Fri@6pm"
        )

    def test_from_human_with_timezone(self):
        weekly_1 = WeeklyInterval(
            "Mon", datetime.time(10, 00), "Fri", datetime.time(18, 00)
        )
        weekly_2 = WeeklyInterval(
            "Sat", datetime.time(12, 00), "Sun", datetime.time(9, 00)
        )
        interval = IntervalUnion([weekly_1, weekly_2])

        # During summer time
        now = datetime.datetime(2019, 8, 30, tzinfo=zoneinfo.ZoneInfo("Europe/London"))
        with time_machine.travel(now):
            assert (
                IntervalUnion.from_human(
                    "Mon 11:00 Europe/London - Fri 19:00 Europe/London,"
                    "Sat 13:00 Europe/London - Sun 10:00 Europe/London"
                )
                == interval
            )

        # Outside summer time
        now = datetime.datetime(2019, 12, 30, tzinfo=zoneinfo.ZoneInfo("Europe/London"))
        with time_machine.travel(now):
            assert (
                IntervalUnion.from_human(
                    "Mon 10:00 Europe/London - Fri 18:00 Europe/London,"
                    "Sat 12:00 Europe/London - Sun 09:00 Europe/London"
                )
                == interval
            )


class TestParseTime:
    invalid_time_msg = "Could not parse time string"

    def test_empty_string(self):
        with pytest.raises(ValueError, match=self.invalid_time_msg):
            marge.interval.parse_time("", "UTC")

    def test_no_colon(self):
        with pytest.raises(ValueError, match=self.invalid_time_msg):
            marge.interval.parse_time("0000", "UTC")

    def test_fewer_minutes(self):
        with pytest.raises(ValueError, match=self.invalid_time_msg):
            marge.interval.parse_time("00:0", "UTC")

    def test_extra_minutes(self):
        with pytest.raises(ValueError, match=self.invalid_time_msg):
            marge.interval.parse_time("00:000", "UTC")

    def test_surplus_minutes(self):
        with pytest.raises(ValueError, match="minute must be in 0..59"):
            marge.interval.parse_time("00:70", "UTC")

    def test_extra_hours(self):
        with pytest.raises(ValueError, match=self.invalid_time_msg):
            marge.interval.parse_time("000:00", "UTC")

    def test_surplus_hours(self):
        with pytest.raises(ValueError, match="hour must be in 0..23"):
            marge.interval.parse_time("30:00", "UTC")

    def test_12am_converts_to_zero(self):
        time = marge.interval.parse_time("12am", "UTC")
        assert time.hour == 0
        assert time.minute == 0

    def test_mixed_case_am(self):
        time = marge.interval.parse_time("12Am", "UTC")
        assert time.hour == 0
        assert time.minute == 0

    def test_mixed_case_pm(self):
        time = marge.interval.parse_time("12pM", "UTC")
        assert time.hour == 12
        assert time.minute == 0
