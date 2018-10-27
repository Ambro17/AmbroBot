import pytest

from commands.snippets.constants import SAVE_REGEX, GET_REGEX, DELETE_REGEX


@pytest.mark.parametrize('input, match', [
    ('#casobase <algo>', True),
    ('#con_underscore <algo>', True),
    ('#con-guion <algo>', True),
    ('#valepregunta? <algo>', True),
    ('#C0nNum3r0s? <algo>', True),
    ('#signo_apertura_¿ <algo>', False),
    ('#conpunto. <algo>', False),
    ('#concoma, <algo>', False),
    ('#', False),
    ('# ', False),
    ('#     agaegea', False),
])
def test_save_regex(input, match):
    assert bool(SAVE_REGEX.match(input)) is match


@pytest.mark.parametrize('input, match', [
    ('@get casobase', True),
    ('@get caso_base?---', True),
    ('@get 123_caso-base?', True),
    ('@get ¿casobase', False),
    ('@get *', False),
])
def test_get_regex_accepts_all_saved_keys(input, match):
    assert bool(GET_REGEX.match(input)) is match


@pytest.mark.parametrize('input, match', [
    ('@delete casobase', True),
    ('@delete 0123_-_???caso_base?---', True),
    ('@delete *', False),
    ('@delete', False),
])
def test_delete_regex_accepts_all_saved_keys(input, match):
    assert bool(DELETE_REGEX.match(input)) is match
