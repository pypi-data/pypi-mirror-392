from __future__ import annotations

import base64
import json
from pathlib import Path

import streamlit as st
from streamlit.components.v1 import html

__all__ = ["music_score", "music_score_file", "music_score_stream"]

# OSMD pulled from CDN; override here if you want to self-host.
DEFAULT_OSMD_SCRIPT = (
    "https://unpkg.com/opensheetmusicdisplay@1.9.0/build/opensheetmusicdisplay.min.js"
)


def music_score(
    score_xml: str,
    *,
    height: int = 540,
    key: str | None = None,
) -> None:
    """
    Render a MusicXML string (e.g., from music21) in Streamlit using OSMD.
    """
    if not isinstance(score_xml, str):
        raise TypeError("score_xml must be a MusicXML string")

    encoded_content = base64.b64encode(score_xml.encode("utf-8")).decode("ascii")
    counter = st.session_state.get("_streamlit_music_score_counter", 0)
    st.session_state["_streamlit_music_score_counter"] = counter + 1
    safe_key = key or "score"
    container_id = f"osmd-container-{safe_key}-{counter}"

    component_html = f"""
    <div id="{container_id}" style="width: 100%; min-height: {height}px; background: #ffffff;"></div>
    <script src="{DEFAULT_OSMD_SCRIPT}"></script>
    <script>
        (function() {{
            const encodedScore = {json.dumps(encoded_content)};
            const target = document.getElementById("{container_id}");

            async function renderOsmd() {{
                try {{
                    const osmdFactory = window.opensheetmusicdisplay || window.OpenSheetMusicDisplay || null;
                    const OSMDClass = osmdFactory?.OpenSheetMusicDisplay || osmdFactory;

                    if (!OSMDClass) {{
                        target.innerHTML = "OpenSheetMusicDisplay failed to load.";
                        return;
                    }}

                    const osmd = new OSMDClass(target, {{ autoResize: true }});
                    const scoreSource = atob(encodedScore);

                    await osmd.load(scoreSource);
                    await osmd.render();
                }} catch (error) {{
                    console.error("OSMD render failed", error);
                    target.innerHTML = "Failed to render score.";
                }}
            }}

            renderOsmd();
        }})();
    </script>
    """

    html(component_html, height=height)


def music_score_file(
    file_path: str | Path,
    *,
    height: int = 540,
    key: str | None = None,
    hide_part_name: bool = False,
) -> None:
    """
    Load a score file with music21 and render it as MusicXML via OSMD.
    """
    try:
        from music21 import converter, musicxml  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "music21 is required for music_score_file(). Install with `pip install music21`."
        ) from exc

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Score file not found: {path}")

    score = converter.parse(path)
    if hide_part_name:
        for part in score.parts:
            part.partName = ""
            part.partAbbreviation = ""
    exported = musicxml.m21ToXml.GeneralObjectExporter(score).parse()
    score_xml = exported.decode("utf-8") if isinstance(exported, (bytes, bytearray)) else str(exported)
    music_score(score_xml, height=height, key=key)


def music_score_stream(
    score: object,
    *,
    height: int = 540,
    key: str | None = None,
    hide_part_name: bool = False,
) -> None:
    """
    Render an in-memory music21 stream by exporting it to MusicXML first.
    """
    try:
        from music21 import musicxml, stream as m21stream  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "music21 is required for music_score_stream(). Install with `pip install music21`."
        ) from exc

    if not isinstance(score, m21stream.Stream):
        raise TypeError("score must be a music21 stream.Stream")

    if hide_part_name:
        for part in score.parts:
            part.partName = " "
            part.partAbbreviation = " "

    exported = musicxml.m21ToXml.GeneralObjectExporter(score).parse()
    score_xml = exported.decode("utf-8") if isinstance(exported, (bytes, bytearray)) else str(exported)
    music_score(score_xml, height=height, key=key)
