import importlib.resources
import json
import logging
from html import escape

import pandas as pd
from IPython.display import HTML, display

import framedisplay

LOG = logging.getLogger(__name__)

from .__version__ import __version__

JS_FILEPATH = str(importlib.resources.files(framedisplay).joinpath("js", "framedisplay.min.js"))
JS_CDN_URL = f"https://cdn.jsdelivr.net/gh/nsarang/framedisplay@v{__version__}/framedisplay/js/framedisplay.min.js"


def initialize():
    """
    Initialize the FrameDisplay JavaScript in Jupyter Notebook.
    This is optional and is only needed for offline usage.
    """
    with open(JS_FILEPATH, "r", encoding="utf-8") as f:
        js_content = f.read()
    display(HTML(f'<script type="text/javascript">{js_content}</script>'))
    LOG.info("FrameDisplay JavaScript initialized.")


def configure(config: dict = None, reset: bool = False, return_html: bool = False) -> None:
    """
    Configure FrameDisplay settings globally.

    Parameters
    ----------
    config : dict
        Configuration options for FrameDisplay. These will be passed to the JavaScript
        as a global variable `FrameDisplayConfig`. See the documentation for available options.
    reset : bool, optional
        If True, resets the FrameDisplayConfig overrides to empty before applying the new config.
        This is useful if you want to ensure that only the provided config options are used,
        without any previously set options interfering. Defaults to False.
    return_html : bool, optional
        If True, return the HTML string instead of displaying it. Defaults to False.
    """
    if config is None and not reset:
        raise ValueError("Either `config` must be provided or `reset` must be True.")

    config_script = ""
    if reset:
        config_script += """
            <script>
                window.FrameDisplayConfig = {};
            </script>
        """
    config_json = json.dumps(config)
    config_script += f"""
        <script>
            window.FrameDisplayConfig = Object.assign(window.FrameDisplayConfig || {{}}, {config_json});
        </script>
    """
    if return_html:
        return config_script
    display(HTML(config_script))


def get_type(series: pd.Series) -> str:
    """
    Get a simplified type name from a pandas dtype.
    """
    dtype = series.dtype if hasattr(series, "dtype") else series
    if pd.api.types.is_integer_dtype(dtype):
        return "int"
    elif pd.api.types.is_float_dtype(dtype):
        return "float"
    elif pd.api.types.is_string_dtype(dtype):
        return "string"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "datetime"
    elif pd.api.types.is_bool_dtype(dtype):
        return "bool"
    elif isinstance(dtype, pd.CategoricalDtype):
        return "category"
    else:
        return "object"


def dataframe_to_html(df: pd.DataFrame) -> str:
    """
    Minimal HTML generator for displaying a pandas DataFrame.
    """

    # Header columns
    dtypes = df.convert_dtypes().apply(get_type).values
    header_cols = "".join(
        f"<th data-dtype={ctype}>{escape(str(col))}</th>" for col, ctype in zip(df.columns, dtypes)
    )

    # Body rows
    rows = []
    for idx, row in df.iterrows():
        cells = [f"<th>{escape(str(idx))}</th>"]  # Index cell
        for value in row:
            if pd.isna(value):
                cells.append('<td><code class="null-cell">null</code></td>')
            else:
                cells.append(f"<td>{escape(str(value))}</td>")

        rows.append(f"<tr>{''.join(cells)}</tr>")

    return f"""
        <table border="1" class="frame-display-table">
            <thead>
                <tr style="text-align: right;">
                    <th></th> <!-- Index column -->
                    {header_cols}
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
    """


def frame_display(
    df: pd.DataFrame,
    jspath: str = None,
    embed_style: str = None,
    return_html: bool = False,
    config: dict = None,
    reset_config: bool = False,
) -> None:
    """
    Display a DataFrame as HTML in Jupyter Notebook.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to display.
    jspath : str, optional
        The path to the FrameDisplay JavaScript file. Defaults to the CDN URL.
    embed_style : str, optional
        Method for including JavaScript and CSS resources:
        - None: Reference JavaScript from the external source specified by `jspath` (default)
        - 'css_only': Embed only CSS styles inline. This is useful for email clients that don't support external scripts.
        - 'all': Embed both JavaScript and CSS inline
    return_html : bool, optional
        If True, return the HTML string instead of displaying it. Defaults to False.
    config : dict, optional
        Configuration options for FrameDisplay. These will be passed to the JavaScript
        as a global variable `FrameDisplayConfig`. See the documentation for available options.
    reset_config : bool, optional
        If True, resets the FrameDisplayConfig overrides to empty before applying the new config.
        This is useful if you want to ensure that only the provided config options are used,
        without any previously set options interfering. Defaults to False.

    Returns
    -------
    str or None
        If return_html is True, returns the HTML string. Otherwise, displays the content
        and returns None.
    """
    if config is not None or reset_config:
        config_script = configure(config or {}, reset=reset_config, return_html=True)
    else:
        config_script = ""

    if embed_style is not None:
        if embed_style == "css_only":
            script_content = f"""
            <style>
                {(importlib.resources.files(framedisplay) / "js/src/styles.css").read_text()}
            </style>
            """
        elif embed_style == "all":
            script_content = f"""
            <script type="text/javascript">
                {(importlib.resources.files(framedisplay) / "js/framedisplay.min.js").read_text()}
            </script>
            """
        else:
            raise ValueError(
                "Invalid value for `embed_style`. Must be 'all' or 'css_only' or None."
            )
    else:
        jspath = jspath or JS_CDN_URL
        script_content = f"<script src='{escape(jspath)}'></script>"

    html_content = f"""
        <div class="table-container">
            {config_script}
            {script_content}
            {dataframe_to_html(df)}
        </div>
    """
    if return_html:
        return html_content
    display(HTML(html_content))


def _get_dataframe_subset(
    df: pd.DataFrame, max_cells: int = None, max_rows: int = None
) -> pd.DataFrame:
    "Helper function to get a subset of the DataFrame based on max_cells or max_rows."
    assert max_cells is not None or max_rows is not None
    if max_cells is not None:
        nrows, ncols = df.shape
        nrows = max(1, max_cells // ncols)
        if max_rows is not None:
            nrows = min(nrows, max_rows)
        return df.head(nrows)
    return df.head(max_rows)


def integrate_with_pandas(max_cells: int = 10000, max_rows: int = None, **kwargs) -> None:
    """
    This function patches the pandas DataFrame class to use FrameDisplay for HTML
    rendering in Jupyter notebooks and other environments that support rich display.
    After calling this function, all DataFrames will automatically use FrameDisplay
    when displayed in notebook cells.

    Parameters
    ----------
    max_cells : int, optional
        Maximum number of cells to display in the DataFrame. If the DataFrame exceeds
        this size, it will be truncated. Defaults to 10000.
    **kwargs : dict
        Additional keyword arguments to pass to `frame_display`.

    Notes
    -----
    This modifies the global pandas DataFrame._repr_html_ method.
    """
    if not hasattr(pd.DataFrame, "_repr_html_original"):
        pd.DataFrame._repr_html_original = pd.DataFrame._repr_html_
    pd.DataFrame._repr_html_ = lambda df: frame_display(
        _get_dataframe_subset(df, max_cells=max_cells, max_rows=max_rows),
        return_html=True,
        **kwargs,
    )
