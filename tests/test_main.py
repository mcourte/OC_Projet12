from unittest.mock import patch
import pytest
from click.testing import CliRunner
from main import sentry_activate, main


@patch('sentry_sdk.init')
def test_sentry_activate(mock_sentry_init):
    sentry_activate()
    mock_sentry_init.assert_called_once_with(
        dsn="https://f005574ea1d1b9036d974ac1ef6eacd1@o4507899769389056.ingest.de.sentry.io/4507899813757008",
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )


@pytest.fixture
def runner():
    return CliRunner()


def test_epic_cli_start(runner):
    result = runner.invoke(main, ['start'])
    assert result.exit_code == 1
    # Vérifiez la sortie attendue ou tout autre comportement spécifique
    assert "\x1b[1;32mInitialisation de EpicBase\x1b[0m\x1b[1;33m...\x1b[0m\n\x1b[32mConnexion à la " in result.output
