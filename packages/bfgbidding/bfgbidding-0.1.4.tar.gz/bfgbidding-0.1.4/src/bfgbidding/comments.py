"""
    Comment and Strategy cross references.
"""

import sysconfig
from pathlib import Path
import json

from bridgeobjects import SUITS
from bfgbidding.constants import APP_NAME
from bfgbidding.logger import app_logger

logger = app_logger()

comment_data_dir = 'comment_data'

DATA_PATH = Path(Path(__file__).parent, comment_data_dir)

venv_dir = sysconfig.get_path('purelib')
venv_data_path = Path(venv_dir, APP_NAME, comment_data_dir)
# Use if testing a venv version
# DATA_PATH = venv_data_path

COMMENT_XREF_FILE = 'comment_xref.json'
STRATEGY_XREF_FILE = 'strategy_xref.json'
COMMENTS_FILE_NAME = 'comments.json'
STRATEGIES_FILE_NAME = 'strategies.json'

SUIT_FONT_SIZE = '2.2vh'
suit_colour = {
    'S': 'black',
    'H': 'red',
    'D': 'red',
    'C': 'black',
}
suit_codes = {
    'S': '&spades;',
    'H': '&hearts;',
    'D': '&diams;',
    'C': '&clubs;',
}
SUIT_CONVERSIONS = {}
suit_template = (f'<span style="font-size: {SUIT_FONT_SIZE}; '
                 f'color: suit_colour;">suit_code</span>')
for suit in SUITS:
    suit_text = suit_template.replace('suit_colour', suit_colour[suit])
    SUIT_CONVERSIONS[suit] = suit_text.replace('suit_code', suit_codes[suit])


def _read_json(path):
    try:
        with open(path, 'r') as f_json:
            return json.load(f_json)
    except FileNotFoundError:
        logger.error(f'Missing json file: {path}')


comment_xrefs = _read_json(Path(DATA_PATH, COMMENT_XREF_FILE))
strategy_xrefs = _read_json(Path(DATA_PATH, STRATEGY_XREF_FILE))
comments = _read_json(Path(DATA_PATH, COMMENTS_FILE_NAME))
strategies = _read_json(Path(DATA_PATH, STRATEGIES_FILE_NAME))


def comment_id(call_id: str) -> str:
    """Return the comment_id associated with the call_id."""
    return comment_xrefs[call_id]


def comment_html(call_id: str) -> str:
    """Return the comment associated with the call_id."""
    comment_id = comment_xrefs[call_id]
    return convert_text_to_html(comments[comment_id])


def strategy_html(call_id: str) -> str:
    """Return the strategy associated with the call_id."""
    comment_id = comment_xrefs[call_id]
    if comment_id not in strategy_xrefs:
        logger.warning(f'---> no strategy_xref record for {comment_id}!')
        return '0000'
    strategy_id = strategy_xrefs[comment_id]
    return convert_text_to_html(strategies[strategy_id])


def _tag(colour: str, end_tag: bool = False) -> str:
    """Return a html tag of the colour."""
    slash = '/' if end_tag else ''
    return f'<{slash}{colour}>'


def convert_text_to_html(text: str) -> str:
    """Convert proprietary text to html."""
    html = text
    for colour in ['red', 'blue', 'green', 'yellow']:
        if _tag(colour) in text:
            html = html.replace(
                _tag(colour),
                f'<span style="color:{colour}">')
        if _tag(colour, True) in text:
            html = html.replace(_tag(colour, True), '</span>')
    for suit in SUITS:
        html = html.replace(f'!{suit}', SUIT_CONVERSIONS[suit])
        html = html.replace(f'!{suit.lower()}', SUIT_CONVERSIONS[suit])
    return html
