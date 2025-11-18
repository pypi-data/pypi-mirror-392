# streamlit-music-score

Render MusicXML scores inside Streamlit using the
[OpenSheetMusicDisplay](https://opensheetmusicdisplay.org/) (OSMD) library.

You have three methods:
* `music_score` Feed a musicxml string directly
* `music_score_file` Read a file. It loads it first with music21. Accepts any file format that music21 accepts
* `music_score_stream` Parse a music21 object. Useful if you are doing transformations with music21 and just want to visualize the result.

OSMD play functionality is only available for sponsors at the moment. As soon as it is released to the public this demo will be updated also to include play controls.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd 
streamlit run example_app.py
```

The demo loads the sample score at `examples/twinkle.musicxml` and lets you
upload your own MusicXML.

## Usage

```python
from streamlit_music_score import music_score, music_score_file, music_score_stream

xml = "<score-partwise>...</score-partwise>"  # MusicXML string from music21
music_score(xml, height=540)
```

### API
- `score_xml`: MusicXML string (UTF-8).
- `height`: Pixel height for the component (default `540`).
- `key`: Optional Streamlit widget key.
