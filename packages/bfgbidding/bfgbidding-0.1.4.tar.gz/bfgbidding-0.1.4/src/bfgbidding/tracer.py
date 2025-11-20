"""Constants for bfgbidding."""
import os
from dotenv import load_dotenv

from bfgbidding.bidding import Bid
from bfgbidding.logger import app_logger

logger = app_logger()

TRACER_CODES = {
    'acol_openers_bid': 2,
    'acol_openers_rebid': 3,
    'acol_openers_third_bid': 5,
    'acol_openers_later_bid': 7,
    'acol_responders_bid': 11,
    'acol_responders_rebid': 13,
    'acol_responders_later_bid': 17,
    'acol_overcallers_bid': 19,
    'acol_overcallers_rebid': 23,
    'acol_overcallers_third_bid': 29,
    'acol_advancers_bid': 31,
    'acol_advancers_rebid': 37,
    'acol_advancers_later_bid': 41,
}


def get_trace(
        hand,
        module: str,
        get_frame: object,
        trace_value: str = '',
        trace_message: str = '') -> list:

    (source_file, display_file) = _get_source_and_display(hand, module)
    (call_id, call_name) = _get_call_id_and_call_name(trace_value)

    function = get_frame.f_code.co_name
    line_number = get_frame.f_lineno
    trace_message = ''.join([', ', trace_message])

    return [
        f'{line_number:03d}',
        f'{call_id=}',
        source_file,
        f'{function:.<40}',
        f'{call_name}{trace_message}'
    ]


def _get_source_and_display(hand, module: str) -> tuple[str, bool]:
    """Return a tuple (source_file, display)"""
    source_file = ''
    display = False
    if hand.trace_module:
        source_file = module.replace('bfg_components.src.', '')
        if hand.trace_module == source_file:
            display = True
    return (source_file, display)


@staticmethod
def _get_call_id_and_call_name(trace_value) -> tuple[str]:
    """Return a tuple (call_id, call_name)"""
    call_id = ''
    call_name = ''
    if isinstance(trace_value, Bid):
        call_id = trace_value.call_id
        call_name = trace_value.name
    return (call_id, call_name)


def trace(tracer_code: int) -> bool:
    return bool(TRACER and TRACER % tracer_code == 0)


def _get_env() -> dict:
    load_dotenv()
    return {
        'tracer': os.getenv('TRACER') or '0',
    }


TRACER = int(_get_env()['tracer'])
# logger.info(f'{bool(TRACER and TRACER % 2 == 0)=}')
