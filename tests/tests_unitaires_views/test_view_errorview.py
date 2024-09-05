import io
import sys
import os
from unittest.mock import patch
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


from views.error_view import ErrorView


@patch('views.error_view.error_console')
def test_display_error_exception(mock_console):
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    mock_console.print = lambda msg: sys.stdout.write(msg + '\n')
    ErrorView.display_error_exception('Test exception message')

    output = sys.stdout.getvalue().strip().split('\n')
    sys.stdout = original_stdout

    assert output == ['Une erreur est survenue dans le traitement', 'Test exception message']
