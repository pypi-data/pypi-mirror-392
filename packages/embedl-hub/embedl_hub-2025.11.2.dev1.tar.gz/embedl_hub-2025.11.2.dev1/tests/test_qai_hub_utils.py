# Copyright (C) 2025 Embedl AB

"""
Utils for Qualcomm AI Hub integration.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from embedl_hub.core.utils.qai_hub_utils import save_qai_hub_model


@patch('embedl_hub.core.utils.qai_hub_utils.onnx.load')
@patch('embedl_hub.core.utils.qai_hub_utils.onnx.save_model')
@patch('embedl_hub.core.utils.qai_hub_utils.unzip_if_zipped')
def test_save_qai_hub_model_default_output_file(
    mock_unzip, mock_save, mock_load
):
    """Test saving model with default output file name."""
    # Setup
    mock_model = Mock()
    mock_model.name = "test_model"
    mock_model.download.return_value = "/tmp/model.zip"

    mock_onnx_model = Mock()
    mock_load.return_value = mock_onnx_model
    mock_unzip.return_value = Path("/tmp/model.onnx")

    with (
        patch('pathlib.Path.cwd') as mock_cwd,
        patch('pathlib.Path.mkdir'),
    ):
        mock_cwd.return_value = Path("/current/dir")

        # Execute
        result = save_qai_hub_model(mock_model)

        # Assert
        expected_output = Path("/current/dir") / "test_model"
        assert result == expected_output
        mock_save.assert_called_once_with(mock_onnx_model, expected_output)


@patch('embedl_hub.core.utils.qai_hub_utils.onnx.load')
@patch('embedl_hub.core.utils.qai_hub_utils.onnx.save_model')
@patch('embedl_hub.core.utils.qai_hub_utils.unzip_if_zipped')
def test_save_qai_hub_model_custom_output_file(
    mock_unzip, mock_save, mock_load
):
    """Test saving model with custom output file path."""
    # Setup
    mock_model = Mock()
    mock_model.name = "test_model"
    mock_model.download.return_value = "/tmp/model.zip"

    mock_onnx_model = Mock()
    mock_load.return_value = mock_onnx_model
    mock_unzip.return_value = Path("/tmp/model.onnx")

    output_file = Path("/custom/path/model.onnx")

    with patch('pathlib.Path.mkdir'):
        # Execute
        result = save_qai_hub_model(mock_model, output_file)

        # Assert
        assert result == output_file
        mock_save.assert_called_once_with(mock_onnx_model, output_file)


@patch('embedl_hub.core.utils.qai_hub_utils.onnx.load')
@patch('embedl_hub.core.utils.qai_hub_utils.onnx.save_model')
@patch('embedl_hub.core.utils.qai_hub_utils.unzip_if_zipped')
def test_save_qai_hub_model_string_output_path(
    mock_unzip, mock_save, mock_load
):
    """Test saving model with string output path."""
    # Setup
    mock_model = Mock()
    mock_model.name = "test_model"
    mock_model.download.return_value = "/tmp/model.zip"

    mock_onnx_model = Mock()
    mock_load.return_value = mock_onnx_model
    mock_unzip.return_value = Path("/tmp/model.onnx")

    output_file_str = "/custom/path/model.onnx"

    with patch('pathlib.Path.mkdir'):
        # Execute
        result = save_qai_hub_model(mock_model, output_file_str)

        # Assert
        expected_path = Path(output_file_str)
        assert result == expected_path
        mock_save.assert_called_once_with(mock_onnx_model, expected_path)


@patch('embedl_hub.core.utils.qai_hub_utils.onnx.load')
@patch('embedl_hub.core.utils.qai_hub_utils.onnx.save_model')
@patch('embedl_hub.core.utils.qai_hub_utils.unzip_if_zipped')
def test_save_qai_hub_model_large_model_fallback(
    mock_unzip, mock_save, mock_load
):
    """Test saving large model that requires folder save."""
    # Setup
    mock_model = Mock()
    mock_model.name = "large_model"
    mock_model.download.return_value = "/tmp/model.zip"

    mock_onnx_model = Mock()
    mock_load.return_value = mock_onnx_model
    mock_unzip.return_value = Path("/tmp/model.onnx")

    # Make first save_model call raise exception, second succeed
    mock_save.side_effect = [Exception("Model too large"), None]
    output_file = Path("/test/large_model.onnx")

    with patch('pathlib.Path.mkdir') as mock_mkdir:
        # Execute
        result = save_qai_hub_model(mock_model, output_file)

        # Assert
        expected_folder = Path("/test/large_model")
        assert result == expected_folder
        # mkdir is called twice: once for output_file.parent, once for expected_folder
        assert mock_mkdir.call_count == 2
        mock_mkdir.assert_any_call(parents=True, exist_ok=True)

        # Verify both save calls
        assert mock_save.call_count == 2
        mock_save.assert_any_call(mock_onnx_model, output_file)


@patch('embedl_hub.core.utils.qai_hub_utils.onnx.load')
@patch('embedl_hub.core.utils.qai_hub_utils.unzip_if_zipped')
def test_save_qai_hub_model_calls_dependencies_correctly(
    mock_unzip, mock_load
):
    """Test that model download and processing dependencies are called correctly."""
    # Setup
    mock_model = Mock()
    mock_model.name = "test_model"
    mock_model.download.return_value = "/tmp/downloaded_model.zip"

    mock_onnx_model = Mock()
    mock_load.return_value = mock_onnx_model
    mock_unzip.return_value = Path("/tmp/extracted_model.onnx")

    with (
        patch('embedl_hub.core.utils.qai_hub_utils.onnx.save_model'),
        patch('pathlib.Path.mkdir'),
    ):
        # Execute
        save_qai_hub_model(mock_model, "/output/model.onnx")

        # Assert download was called with temp file path
        mock_model.download.assert_called_once()
        download_path = mock_model.download.call_args[0][0]
        assert download_path.endswith("/model")

        # Assert unzip was called with downloaded file
        mock_unzip.assert_called_once()
        assert str(mock_unzip.call_args[0][0]) == "/tmp/downloaded_model.zip"

        # Assert onnx.load was called with extracted file
        mock_load.assert_called_once_with(Path("/tmp/extracted_model.onnx"))
        mock_unzip.assert_called_once()
        assert str(mock_unzip.call_args[0][0]) == "/tmp/downloaded_model.zip"

        # Assert onnx.load was called with extracted file
        mock_load.assert_called_once_with(Path("/tmp/extracted_model.onnx"))


if __name__ == "__main__":
    pytest.main([__file__])
