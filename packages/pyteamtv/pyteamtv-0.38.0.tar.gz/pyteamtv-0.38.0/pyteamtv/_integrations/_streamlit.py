from typing import Optional

import streamlit as st

from .app import _get_current_app, App


def get_current_app(
    app_id: Optional[str] = None,
    use_cache: bool = False,
    raise_on_missing_token: bool = True,
) -> App:
    # Use new st.query_params if available (Streamlit >= 1.30.0),
    # otherwise fall back to experimental API
    if hasattr(st, "query_params"):
        # New API: st.query_params returns a dict-like object
        query_params = st.query_params
        token = query_params.get("token", None)
    else:
        # Old API: st.experimental_get_query_params returns dict with list values
        query_params = st.experimental_get_query_params()
        token = query_params.get("token", [None])[0]

    return _get_current_app(
        app_id=app_id,
        session=st.session_state,
        token=token,
        use_cache=use_cache,
        raise_on_missing_token=raise_on_missing_token,
    )
