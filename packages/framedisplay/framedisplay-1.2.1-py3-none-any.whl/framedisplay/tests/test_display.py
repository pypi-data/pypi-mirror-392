# Requires pytest-mock: pip install pytest-mock
# This provides the 'mocker' fixture as a pytest-compatible alternative to unittest.mock

import numpy as np
import pandas as pd
import pytest
from bs4 import BeautifulSoup
from hypothesis import given
from hypothesis import strategies as st

from framedisplay.display import (
    dataframe_to_html,
    frame_display,
    get_type,
    initialize,
    integrate_with_pandas,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {"int_col": [1, 2, 3], "str_col": ["a", "b", "c"], "float_col": [1.1, 2.2, np.nan]}
    )


class TestCoreHTMLGeneration:
    """Core functionality and HTML generation."""

    def test_basic_dataframe_structure(self, sample_df):
        html = dataframe_to_html(sample_df)
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", class_="frame-display-table")
        assert table is not None

        headers = soup.find("thead").find_all("th")
        assert len(headers) == 4  # Index + 3 columns
        assert headers[1].text == "int_col"
        assert headers[2].text == "str_col"
        assert headers[3].text == "float_col"

        rows = soup.find("tbody").find_all("tr")
        assert len(rows) == 3

    def test_null_values_handling(self):
        df = pd.DataFrame({"mixed_nulls": [1, None, 3, np.nan, 5]})

        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        null_cells = soup.find_all("code", class_="null-cell")
        assert len(null_cells) == 2  # None and np.nan
        for cell in null_cells:
            assert cell.text == "null"

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        assert soup.find("table", class_="frame-display-table") is not None
        assert soup.find("thead") is not None
        assert soup.find("tbody") is not None


class TestSecurityAndEscaping:
    """XSS prevention and input sanitization."""

    def test_xss_prevention_in_data(self):
        df = pd.DataFrame(
            {"malicious": ['<script>alert("xss")</script>', "<img src=x onerror=alert(1)>"]}
        )

        html = dataframe_to_html(df)
        assert "<script>" not in html
        assert "<img" not in html
        assert "&lt;script&gt;" in html
        assert "&lt;img" in html

    def test_xss_prevention_in_column_names(self):
        df = pd.DataFrame({'<script>alert("xss")</script>': [1, 2, 3]})

        html = dataframe_to_html(df)
        assert "<script>alert(" not in html
        assert "&lt;script&gt;" in html

    def test_malicious_js_path_escaping(self):
        df = pd.DataFrame({"A": [1]})
        malicious_path = '"><script>alert(1)</script>'

        html = frame_display(df, jspath=malicious_path, return_html=True)
        assert "<script>alert(1)" not in html
        assert "&quot;&gt;&lt;script&gt;" in html


class TestDataTypeHandling:
    """Data type detection and handling."""

    @pytest.mark.parametrize(
        "dtype,expected",
        [
            (np.dtype("int64"), "int"),
            (np.dtype("float64"), "float"),
            (pd.StringDtype(), "string"),
            (np.dtype("bool"), "bool"),
            (np.dtype("datetime64[ns]"), "datetime"),
            (pd.CategoricalDtype(["A", "B"]), "category"),
            (np.dtype("object"), "string"),  # pandas considers object as string
            (np.dtype("complex128"), "object"),
        ],
    )
    def test_get_type_function(self, dtype, expected):
        assert get_type(dtype) == expected

    def test_datetime_columns_get_correct_dtype(self):
        df = pd.DataFrame({"dates": pd.date_range("2023-01-01", periods=3)})

        html = frame_display(df, return_html=True)
        assert "data-dtype=datetime" in html

    def test_mixed_data_types_in_output(self):
        df = pd.DataFrame(
            {
                "integers": [1, 2, 3],
                "floats": [1.1, 2.2, np.inf],
                "strings": ["a", "b", "c"],
                "booleans": [True, False, True],
            }
        )

        html = frame_display(df, return_html=True)
        assert "data-dtype=int" in html
        assert "data-dtype=float" in html
        assert "data-dtype=string" in html
        assert "data-dtype=bool" in html


class TestFrameDisplayFunction:
    """Main user-facing function behavior."""

    def test_return_vs_display_modes(self, sample_df, mocker):
        mock_display = mocker.patch("framedisplay.display.display")

        # Default behavior: display in Jupyter
        result = frame_display(sample_df)
        assert result is None
        mock_display.assert_called_once()

        # Return HTML mode
        html = frame_display(sample_df, return_html=True)
        assert isinstance(html, str)
        assert "table-container" in html

    def test_custom_js_path(self, sample_df):
        custom_path = "https://example.com/custom.js"
        html = frame_display(sample_df, jspath=custom_path, return_html=True)
        assert custom_path in html

    @pytest.mark.parametrize("embed_style", ["css_only", "all"])
    def test_embed_styles(self, sample_df, embed_style, mocker):
        mock_files = mocker.patch("importlib.resources.files")
        mock_file = mocker.MagicMock()
        mock_file.read_text.return_value = "/* mock content */"
        mock_files.return_value.__truediv__.return_value = mock_file

        html = frame_display(sample_df, embed_style=embed_style, return_html=True)
        assert "/* mock content */" in html

    def test_invalid_embed_style_raises_error(self, sample_df):
        with pytest.raises(ValueError, match="Invalid value for `embed_style`"):
            frame_display(sample_df, embed_style="invalid")


class TestPandasIntegration:
    """Pandas DataFrame._repr_html_ integration."""

    def test_integration_modifies_dataframe_repr(self, sample_df):
        original = getattr(pd.DataFrame, "_repr_html_", None)

        try:
            integrate_with_pandas()
            assert hasattr(pd.DataFrame, "_repr_html_")

            html = sample_df._repr_html_()
            assert isinstance(html, str)
            assert "frame-display-table" in html

        finally:
            if original is not None:
                pd.DataFrame._repr_html_ = original
            else:
                delattr(pd.DataFrame, "_repr_html_")

    def test_integration_passes_kwargs(self, sample_df, mocker):
        original = getattr(pd.DataFrame, "_repr_html_", None)

        try:
            mock_frame_display = mocker.patch("framedisplay.display.frame_display")
            mock_frame_display.return_value = "<html>test</html>"

            integrate_with_pandas(embed_style="css_only")
            sample_df._repr_html_()

            args, kwargs = mock_frame_display.call_args
            assert kwargs["embed_style"] == "css_only"
            assert kwargs["return_html"] is True

        finally:
            if original is not None:
                pd.DataFrame._repr_html_ = original
            else:
                delattr(pd.DataFrame, "_repr_html_")


class TestEdgeCases:
    """Edge cases and stress testing."""

    def test_multiindex_dataframe(self):
        arrays = [["A", "A", "B", "B"], [1, 2, 1, 2]]
        index = pd.MultiIndex.from_arrays(arrays)
        df = pd.DataFrame({"values": [10, 20, 30, 40]}, index=index)

        html = frame_display(df, return_html=True)
        assert "frame-display-table" in html  # Should not crash

    def test_extreme_numeric_values(self):
        df = pd.DataFrame({"extreme": [float("inf"), float("-inf"), 1e308, -1e-308, np.nan]})
        html = dataframe_to_html(df)
        assert "inf" in html.lower()
        assert "null-cell" in html  # for np.nan

    def test_large_dataframe_performance(self):
        df = pd.DataFrame(
            {"col1": range(1000), "col2": ["text"] * 1000, "col3": np.random.random(1000)}
        )

        html = frame_display(df, return_html=True)
        assert "frame-display-table" in html
        assert len(html) > 1000

    def test_wide_dataframe(self):
        data = {f"col_{i}": [1, 2, 3] for i in range(50)}
        df = pd.DataFrame(data)

        html = frame_display(df, return_html=True)
        soup = BeautifulSoup(html, "html.parser")
        headers = soup.find("thead").find_all("th")
        assert len(headers) == 51  # 50 columns + index

    def test_single_row_dataframe(self):
        df = pd.DataFrame({"A": [1], "B": ["test"]})
        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.find("tbody").find_all("tr")
        assert len(rows) == 1
        cells = rows[0].find_all(["th", "td"])
        assert len(cells) == 3  # Index + 2 data columns

    def test_index_handling(self):
        df = pd.DataFrame({"A": [1, 2]}, index=["row1", "row2"])
        html = dataframe_to_html(df)
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.find("tbody").find_all("tr")
        index_cells = [row.find("th") for row in rows]
        assert index_cells[0].text == "row1"
        assert index_cells[1].text == "row2"

    def test_very_long_strings(self):
        long_string = "x" * 10000
        df = pd.DataFrame({"long": [long_string]})
        html = frame_display(df, return_html=True)
        assert "frame-display-table" in html
        assert long_string in html

    def test_categorical_dtype_detection(self):
        df = pd.DataFrame({"cat": pd.Categorical(["A", "B", "C"])})
        # Only test if dtype preserved as categorical
        if isinstance(df["cat"].dtype, pd.CategoricalDtype):
            html = frame_display(df, return_html=True)
            assert "data-dtype=category" in html

    def test_time_series_dataframe(self):
        dates = pd.date_range("2023-01-01", periods=5)
        df = pd.DataFrame(
            {
                "date": dates,
                "value": [1.1, 2.2, 3.3, 4.4, 5.5],
                "category": ["A", "B", "A", "B", "C"],
            }
        )

        html = frame_display(df, return_html=True)
        assert "data-dtype=datetime" in html
        assert "data-dtype=float" in html
        assert "data-dtype=string" in html

    def test_unicode_data(self):
        df = pd.DataFrame({"unicode": ["🚀", "测试", "🇺🇸", "∑∆∫", "café"]})

        html = frame_display(df, return_html=True)
        assert "🚀" in html
        assert "测试" in html
        assert "café" in html


class TestResourceHandling:
    """Resource loading and error handling."""

    def test_missing_js_file_fails_gracefully(self, sample_df, mocker):
        mocker.patch("importlib.resources.files", side_effect=FileNotFoundError())

        with pytest.raises(FileNotFoundError):
            frame_display(sample_df, embed_style="all")

    def test_cdn_url_format_is_valid(self):
        from framedisplay.display import JS_CDN_URL

        assert JS_CDN_URL.startswith("https://cdn.jsdelivr.net/")
        assert ".min.js" in JS_CDN_URL


class TestInitialization:
    """JavaScript initialization functionality."""

    def test_initialize_loads_and_displays_js(self, mocker):
        mock_display = mocker.patch("framedisplay.display.display")
        mock_open = mocker.patch("builtins.open")
        mock_open.return_value.__enter__.return_value.read.return_value = "test_js_content"

        initialize()

        mock_display.assert_called_once()
        html_obj = mock_display.call_args[0][0]
        assert "test_js_content" in html_obj.data
        assert '<script type="text/javascript">' in html_obj.data


class TestPropertyBased:
    """Property-based testing with hypothesis."""

    @given(st.lists(st.text(), min_size=1, max_size=10))
    def test_arbitrary_text_data_safety(self, strings):
        df = pd.DataFrame({"col": strings})
        html = dataframe_to_html(df)

        # Should never contain unescaped script tags
        assert "<script" not in html.lower()
        assert "javascript:" not in html.lower()
        assert "frame-display-table" in html

    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=10).filter(lambda x: x.strip()),
            values=st.lists(
                st.one_of(st.integers(), st.floats(allow_nan=True), st.text(), st.none()),
                min_size=1,
                max_size=20,
            ),
            min_size=1,
            max_size=5,
        )
    )
    def test_arbitrary_dataframes_dont_crash(self, df_data):
        try:
            df = pd.DataFrame(df_data)
            html = dataframe_to_html(df)
            assert isinstance(html, str)
            assert len(html) > 10
            # Should be valid HTML
            soup = BeautifulSoup(html, "html.parser")
            assert soup.find("table") is not None
        except (ValueError, TypeError):
            # Some combinations might create invalid DataFrames
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
