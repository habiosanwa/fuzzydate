from unittest.mock import call, patch

import pytest

from fuzzydate import fuzzydate


class TestFuzzydate:
    @pytest.mark.parametrize(
        "args,exp_year,exp_month,exp_day,exp_fuzzy_month,exp_fuzzy_day",
        [
            ((2020, 6, 27), 2020, 6, 27, False, False),
            ((2020, 6, None), 2020, 6, 1, False, True),
            ((2020, None, None), 2020, 1, 1, True, True),
        ],
    )
    def test_new__ok(self, args, exp_year, exp_month, exp_day, exp_fuzzy_month, exp_fuzzy_day):  # noqa: PLR0913
        fdt = fuzzydate(*args)

        assert fdt.year == exp_year, "year not initialised correctly"
        assert fdt.month == exp_month, "month not initialised correctly"
        assert fdt.day == exp_day, "day not initialised correctly"

        assert fdt._fuzzy_month is exp_fuzzy_month, "fuzzy month not set correctly"
        assert fdt._fuzzy_day is exp_fuzzy_day, "fuzzy day not set correctly"

    def test_new__fails_when_only_fuzzy_month(self):
        with pytest.raises(ValueError, match=r"cannot.+fuzzy month.+defined day"):
            _ = fuzzydate(2020, None, 27)

    def test_from_isoformat__disabled(self):
        with pytest.raises(NotImplementedError, match="not supported.*instead$"):
            _ = fuzzydate.fromisoformat("2020-06-27")

    @pytest.mark.parametrize(
        "date_string,exp_year,exp_month,exp_day",
        [
            ("2020-06-27", 2020, 6, 27),
            ("2020-06-??", 2020, 6, None),
            ("2020-??-??", 2020, None, None),
        ],
    )
    def test_fuzzy_fromisoformat__ok(self, date_string, exp_year, exp_month, exp_day):
        with patch.object(fuzzydate, "__new__", wraps=fuzzydate.__new__) as mocked_new:
            _ = fuzzydate.fuzzy_fromisoformat(date_string)

        assert mocked_new.call_args == call(
            fuzzydate, exp_year, exp_month, exp_day
        ), "constructor was not called with the appropriate parameters"

    def test_fuzzy_fromisoformat__not_string(self):
        with pytest.raises(TypeError, match=r"argument must be str$"):
            _ = fuzzydate.fuzzy_fromisoformat(b"2020-06-27")

    @pytest.mark.parametrize("date_string", ["2020-6-27", "2020-6-27 9:30", ""])
    def test_fuzzy_fromisoformat__invalid_length(self, date_string):
        with pytest.raises(ValueError, match=r"^Invalid fuzzy isoformat string"):
            _ = fuzzydate.fuzzy_fromisoformat(date_string)

    @pytest.mark.parametrize("date_string", ["2020_06_27", "2020-06/27"])
    def test_fuzzy_fromisoformat__invalid_separator(self, date_string):
        with pytest.raises(ValueError, match=r"^Invalid date separator"):
            _ = fuzzydate.fuzzy_fromisoformat(date_string)

    @pytest.mark.parametrize("date_string", ["2020-06-?#", "2020-##-??"])
    def test_fuzzy_fromisoformat__inconsistent_marker(self, date_string):
        with pytest.raises(ValueError, match=r"Inconsistent marker usage"):
            _ = fuzzydate.fuzzy_fromisoformat(date_string)

    def test_fuzzy_fromisoformat__invalid_year(self):
        with pytest.raises(ValueError, match=r"Invalid year"):
            _ = fuzzydate.fuzzy_fromisoformat("????-06-27")

    def test_isoformat__disabled(self):
        with pytest.raises(NotImplementedError, match="not supported.*instead$"):
            _ = fuzzydate(2020, 6, 27).isoformat()

    @pytest.mark.parametrize(
        "year,month,day,exp_date_string",
        [
            (2020, 6, 27, "2020-06-27"),
            (2020, 6, None, "2020-06-??"),
            (2020, None, None, "2020-??-??"),
        ],
    )
    def test_fuzzy_isoformat__ok(self, year, month, day, exp_date_string):
        fstr = fuzzydate(year, month, day).fuzzy_isoformat()

        assert fstr == exp_date_string, "fuzzy isoformat string is incorrect"

    def test_fuzzy_isoformat__custom_marker(self):
        fstr = fuzzydate(2020, 6, None).fuzzy_isoformat(marker="%")

        assert fstr == "2020-06-%%", "fuzzy isoformat string with custom marker is incorrect"

    @pytest.mark.parametrize("marker", ["###", "9"])
    def test_fuzzy_isoformat__invalid_marker(self, marker):
        with pytest.raises(ValueError, match=r"^Invalid fuzzy marker"):
            _ = fuzzydate(2020, 6, None).fuzzy_isoformat(marker=marker)

    def test_str__ok(self):
        assert str(fuzzydate(2020, 6, None)) == "2020-06-??", "incorrect __str__ output"

    def test_repr__ok(self):
        assert repr(fuzzydate(2020, 6, None)) == "fuzzydate(2020, 6, None)", "incorrect __repr__ output"
