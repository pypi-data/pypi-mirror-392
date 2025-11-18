"""Tests for dict utility helpers."""

from smartseeds import SmartOptions
from smartseeds.dict_utils import filtered_dict, make_opts


class TestFilteredDict:
    """Tests for filtered_dict helper."""

    def test_returns_copy_when_no_filter(self):
        source = {"a": 1, "b": 2}
        result = filtered_dict(source)
        assert result == source
        assert result is not source

    def test_filters_none_values(self):
        source = {"a": 1, "b": None, "c": 3}
        result = filtered_dict(source, lambda key, value: value is not None)
        assert result == {"a": 1, "c": 3}

    def test_handles_none_source(self):
        assert filtered_dict(None) == {}


class TestMakeOpts:
    """Tests for make_opts helper."""

    def test_merges_defaults_and_incoming(self):
        opts = make_opts({"timeout": 10}, {"timeout": 5, "retries": 3})
        assert opts.timeout == 10
        assert opts.retries == 3

    def test_respects_filter_function(self):
        opts = make_opts(
            {"timeout": None, "retries": 5},
            {"timeout": 2, "retries": 1},
            filter_fn=lambda _, value: value is not None,
        )
        assert opts.timeout == 2  # None filtered, default preserved
        assert opts.retries == 5

    def test_ignore_none_flag(self):
        opts = make_opts(
            {"timeout": None},
            {"timeout": 15},
            ignore_none=True,
        )
        assert opts.timeout == 15

    def test_ignore_empty_flag(self):
        opts = make_opts(
            {"tag": "", "labels": []},
            {"tag": "default", "labels": ["x"]},
            ignore_empty=True,
        )
        assert opts.tag == "default"
        assert opts.labels == ["x"]

    def test_accepts_missing_mappings(self):
        opts = make_opts(None, None)
        assert vars(opts) == {}


class TestSmartOptions:
    """Tests for SmartOptions helper class."""

    def test_basic_merge(self):
        opts = SmartOptions({"timeout": 5}, {"timeout": 1, "retries": 3})
        assert opts.timeout == 5
        assert opts.retries == 3

    def test_ignore_flags(self):
        opts = SmartOptions(
            {"timeout": None, "tags": []},
            {"timeout": 10, "tags": ["default"]},
            ignore_none=True,
            ignore_empty=True,
        )
        assert opts.timeout == 10
        assert opts.tags == ["default"]

    def test_as_dict_returns_copy(self):
        opts = SmartOptions({"timeout": 2}, {})
        result = opts.as_dict()
        assert result == {"timeout": 2}
        result["timeout"] = 99
        assert opts.timeout == 2  # original not mutated

    def test_attribute_updates_are_tracked(self):
        opts = SmartOptions({"timeout": 2}, {})
        opts.timeout = 7
        assert opts.as_dict()["timeout"] == 7
        opts.new_flag = True
        assert opts.as_dict()["new_flag"] is True
        del opts.timeout
        assert "timeout" not in opts.as_dict()
