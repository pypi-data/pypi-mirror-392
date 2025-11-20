"""Tests for utility functions."""

from django_api_orm.utils import build_query_params, chunk_list, merge_dicts


class TestBuildQueryParams:
    """Test query parameter building."""

    def test_basic_params(self) -> None:
        """Test building basic query parameters."""
        params = build_query_params(status="active", limit=10)
        assert params == {"status": "active", "limit": "10"}

    def test_none_values_excluded(self) -> None:
        """Test that None values are excluded."""
        params = build_query_params(status="active", limit=None, offset=0)
        assert params == {"status": "active", "offset": "0"}

    def test_empty_params(self) -> None:
        """Test with no parameters."""
        params = build_query_params()
        assert params == {}

    def test_boolean_values(self) -> None:
        """Test that boolean values are converted to strings."""
        params = build_query_params(active=True, deleted=False)
        assert params == {"active": "True", "deleted": "False"}

    def test_numeric_values(self) -> None:
        """Test that numeric values are converted to strings."""
        params = build_query_params(id=123, price=99.99)
        assert params == {"id": "123", "price": "99.99"}


class TestMergeDicts:
    """Test dictionary merging."""

    def test_merge_two_dicts(self) -> None:
        """Test merging two dictionaries."""
        result = merge_dicts({"a": 1, "b": 2}, {"c": 3})
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_merge_with_override(self) -> None:
        """Test that later dicts override earlier ones."""
        result = merge_dicts({"a": 1, "b": 2}, {"b": 3, "c": 4})
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_with_none(self) -> None:
        """Test that None dicts are skipped."""
        result = merge_dicts({"a": 1}, None, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_merge_all_none(self) -> None:
        """Test merging only None dicts."""
        result = merge_dicts(None, None)
        assert result == {}

    def test_merge_empty_dicts(self) -> None:
        """Test merging empty dictionaries."""
        result = merge_dicts({}, {}, {})
        assert result == {}

    def test_merge_single_dict(self) -> None:
        """Test merging a single dictionary."""
        result = merge_dicts({"a": 1, "b": 2})
        assert result == {"a": 1, "b": 2}


class TestChunkList:
    """Test list chunking."""

    def test_basic_chunking(self) -> None:
        """Test basic list chunking."""
        items = [1, 2, 3, 4, 5, 6]
        chunks = chunk_list(items, 2)
        assert chunks == [[1, 2], [3, 4], [5, 6]]

    def test_uneven_chunks(self) -> None:
        """Test chunking with remainder."""
        items = [1, 2, 3, 4, 5]
        chunks = chunk_list(items, 2)
        assert chunks == [[1, 2], [3, 4], [5]]

    def test_chunk_size_equals_list_size(self) -> None:
        """Test when chunk size equals list size."""
        items = [1, 2, 3]
        chunks = chunk_list(items, 3)
        assert chunks == [[1, 2, 3]]

    def test_chunk_size_larger_than_list(self) -> None:
        """Test when chunk size is larger than list."""
        items = [1, 2]
        chunks = chunk_list(items, 5)
        assert chunks == [[1, 2]]

    def test_empty_list(self) -> None:
        """Test chunking an empty list."""
        items = []
        chunks = chunk_list(items, 2)
        assert chunks == []

    def test_single_item(self) -> None:
        """Test chunking a single item."""
        items = [1]
        chunks = chunk_list(items, 1)
        assert chunks == [[1]]
