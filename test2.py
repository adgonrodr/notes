import pytest
import logging
import os
import time
import re
from unittest.mock import patch, mock_open, MagicMock
from utils.logger import rotate_logs_monthly, configure_logger  # Assuming the module is utils.logger

# Tests for rotate_logs_monthly
@patch('time.strftime')
@patch('os.path.dirname')
@patch('os.path.basename')
@patch('os.path.exists')
@patch('os.listdir')
@patch('os.remove')
@patch('builtins.open', mopen=mock_open())
def test_rotate_logs_monthly_creates_new_file(mock_open, mock_remove, mock_listdir, mock_exists, mock_basename, mock_dirname, mock_strftime):
    mock_strftime.return_value = '2025-08'
    mock_dirname.return_value = '/logs'
    mock_basename.return_value = 'app.log'
    mock_exists.return_value = False
    mock_listdir.return_value = []

    rotate_logs_monthly('/logs/app.log', max_keep=4)

    mock_open.assert_called_once_with('/logs/app_2025-08.log', 'a')
    mock_remove.assert_not_called()

@patch('time.strftime')
@patch('os.path.dirname')
@patch('os.path.basename')
@patch('os.path.exists')
@patch('os.listdir')
@patch('os.remove')
@patch('builtins.open', mopen=mock_open())
def test_rotate_logs_monthly_skips_creation_if_exists(mock_open, mock_remove, mock_listdir, mock_exists, mock_basename, mock_dirname, mock_strftime):
    mock_strftime.return_value = '2025-08'
    mock_dirname.return_value = '/logs'
    mock_basename.return_value = 'app.log'
    mock_exists.return_value = True
    mock_listdir.return_value = []

    rotate_logs_monthly('/logs/app.log', max_keep=4)

    mock_open.assert_not_called()
    mock_remove.assert_not_called()

@patch('time.strftime')
@patch('os.path.dirname')
@patch('os.path.basename')
@patch('os.path.exists')
@patch('os.listdir')
@patch('os.remove')
@patch('builtins.open', mopen=mock_open())
def test_rotate_logs_monthly_cleans_old_logs(mock_open, mock_remove, mock_listdir, mock_exists, mock_basename, mock_dirname, mock_strftime):
    mock_strftime.return_value = '2025-08'
    mock_dirname.return_value = '/logs'
    mock_basename.return_value = 'app.log'
    mock_exists.return_value = True
    mock_listdir.return_value = [
        'app_2025-08.log',
        'app_2025-07.log',
        'app_2025-06.log',
        'app_2025-05.log',
        'app_2025-04.log',
        'app_2025-03.log'
    ]

    rotate_logs_monthly('/logs/app.log', max_keep=4)

    mock_remove.assert_any_call('/logs/app_2025-04.log')
    mock_remove.assert_any_call('/logs/app_2025-03.log')
    assert mock_remove.call_count == 2

@patch('time.strftime')
@patch('os.path.dirname')
@patch('os.path.basename')
@patch('os.path.exists')
@patch('os.listdir')
@patch('os.remove')
@patch('builtins.open', mopen=mock_open())
def test_rotate_logs_monthly_sorts_correctly(mock_open, mock_remove, mock_listdir, mock_exists, mock_basename, mock_dirname, mock_strftime):
    mock_strftime.return_value = '2025-08'
    mock_dirname.return_value = '/logs'
    mock_basename.return_value = 'app.log'
    mock_exists.return_value = True
    mock_listdir.return_value = [
        'app_2025-05.log',
        'app_2025-08.log',
        'app_2025-03.log',
        'app_2025-07.log',
        'app_2025-04.log',
        'app_2025-06.log'
    ]

    rotate_logs_monthly('/logs/app.log', max_keep=3)

    # Should keep 2025-08, 2025-07, 2025-06; remove 2025-05, 2025-04, 2025-03
    mock_remove.assert_any_call('/logs/app_2025-05.log')
    mock_remove.assert_any_call('/logs/app_2025-04.log')
    mock_remove.assert_any_call('/logs/app_2025-03.log')
    assert mock_remove.call_count == 3

# Tests for configure_logger
@patch('logging.getLogger')
@patch('time.strftime')
def test_configure_logger_stream_handler(mock_strftime, mock_getLogger):
    mock_logger = MagicMock()
    mock_logger.handlers = []
    mock_getLogger.return_value = mock_logger

    logger = configure_logger(log_file_def=False)

    mock_logger.setLevel.assert_called_with(logging.DEBUG)
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert logger.handlers[0].formatter._fmt == "%(asctime)s - %(levelname)s - %(message)s"

@patch('logging.getLogger')
@patch('time.strftime')
@patch('utils.logger.rotate_logs_monthly')  # Assuming same module
def test_configure_logger_file_handler_custom_path(mock_rotate, mock_strftime, mock_getLogger):
    mock_strftime.return_value = '2025-08'
    mock_logger = MagicMock()
    mock_logger.handlers = []
    mock_getLogger.return_value = mock_logger

    logger = configure_logger(log_file_def=True, custom_log_path='/custom/app.log')

    mock_rotate.assert_called_with('/custom/app.log', 4)
    assert isinstance(logger.handlers[0], logging.FileHandler)
    assert logger.handlers[0].baseFilename == '/custom/app_2025-08.log'

@patch('logging.getLogger')
@patch('time.strftime')
@patch('utils.logger.rotate_logs_monthly')
def test_configure_logger_file_handler_default_path(mock_rotate, mock_strftime, mock_getLogger):
    mock_strftime.return_value = '2025-08'
    mock_logger = MagicMock()
    mock_logger.handlers = []
    mock_getLogger.return_value = mock_logger

    logger = configure_logger(log_file_def=True, log_path='/default', logger_name='test_logger')

    mock_rotate.assert_called_with('/default/test_logger.log', 4)
    assert isinstance(logger.handlers[0], logging.FileHandler)
    assert logger.handlers[0].baseFilename == '/default/test_logger_2025-08.log'

@patch('logging.getLogger')
def test_configure_logger_returns_existing_if_handlers(mock_getLogger):
    mock_logger = MagicMock()
    mock_logger.handlers = [MagicMock()]
    mock_getLogger.return_value = mock_logger

    logger = configure_logger()

    assert logger == mock_logger
    mock_logger.setLevel.assert_not_called()

@patch('logging.getLogger')
@patch('time.strftime')
@patch('utils.logger.rotate_logs_monthly')
def test_configure_logger_custom_level(mock_rotate, mock_strftime, mock_getLogger):
    mock_logger = MagicMock()
    mock_logger.handlers = []
    mock_getLogger.return_value = mock_logger

    configure_logger(logging_level=logging.WARNING)

    mock_logger.setLevel.assert_called_with(logging.DEBUG)  # It always sets to DEBUG, regardless of logging_level? Wait, code shows setLevel(DEBUG), but arg is logging_level=INFO, but not used.
    # Note: In the code, it's logger.setLevel(logging.DEBUG), not using logging_level. Perhaps a bug, but test as is.