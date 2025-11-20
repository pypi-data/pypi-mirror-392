# Copyright (C) 2025 Embedl AB

"""
embedl-hub quantize - send an onnx model to Qualcomm AI Hub and retrieve a
quantized onnx model.
"""

from pathlib import Path

import typer

# All other embedl_hub imports should be done inside the function.
from embedl_hub.cli.helper import (
    CONFIG_HELPER,
    OUTPUT_FILE_HELPER,
)

quantize_cli = typer.Typer()


@quantize_cli.command("quantize")
def quantize_command(
    ctx: typer.Context,
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help="Path to the ONNX model file, or to a directory containing the ONNX model "
        "and any associated data files, to be quantized. (required)",
        show_default=False,
    ),
    data_path: Path = typer.Option(
        None,
        "--data",
        "-d",
        help=(
            "Path to the dataset used for calibration. "
            "If not provided, random data will be used for calibration. "
            "If the model is a single-input model, the directory should contain "
            "numpy files (.npy) with the input data. "
            "If the model has multiple inputs, the directory should contain "
            "subdirectories named after the input names, each containing "
            "numpy files (.npy) with the corresponding input data."
        ),
        show_default=False,
    ),
    output_file: Path = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
    num_samples: int = typer.Option(
        None,
        "--num-samples",
        "-n",
        help="Number of data samples to use during quantization calibration.",
        show_default=False,
    ),
    config_path: Path = typer.Option(
        None,
        "--config",
        "-c",
        help=CONFIG_HELPER,
    ),
):
    """
    Quantize an ONNX model using Qualcomm AI Hub.
    Qualcomm AI Hub may return a zip file containing multiple files.

    Required arguments (if not provided through --config):
        --model

    Examples
    --------
    Quantize the ONNX model `compiled_model.onnx` calibrating on data
    from `/path/to/dataset/` using 1000 samples from the dataset:

        $ embedl-hub quantize -m compiled_model.onnx -d /path/to/dataset/ -n 1000

    Quantize the ONNX model using the configuration specified in `my_config.yaml`:

        $ embedl-hub quantize -c ./my_config.yaml

    """

    # pylint: disable=import-outside-toplevel
    from tempfile import TemporaryDirectory

    from embedl_hub.cli.utils import assert_api_config
    from embedl_hub.core.context import (
        require_initialized_ctx,
    )
    from embedl_hub.core.hub_logging import console
    from embedl_hub.core.quantization.quantize import (
        create_quantization_cfg,
        quantize_model,
    )
    from embedl_hub.core.utils.onnx_utils import (
        maybe_package_onnx_folder_to_file,
    )
    # pylint: enable=import-outside-toplevel

    assert_api_config()
    require_initialized_ctx(ctx.obj["config"])

    if not output_file:
        output_file = Path(model).with_suffix(".quantized")
        console.print(
            f"[yellow]No output file specified, using default: {output_file}[/]"
        )
    if data_path is None:
        console.print(
            "[yellow]No data path specified, generating random calibration data.[/]"
        )

    cfg = create_quantization_cfg(
        model, data_path, output_file, num_samples, config_path
    )
    try:
        cfg.validate_config()
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)

    with TemporaryDirectory() as tmpdir:
        cfg.model = maybe_package_onnx_folder_to_file(cfg.model, tmpdir)
        quantized_model_path = quantize_model(
            config=cfg,
            project_name=ctx.obj["config"]["project_name"],
            experiment_name=ctx.obj["config"]["experiment_name"],
        )
    console.print(
        f"[green]✓ Quantized model saved to {quantized_model_path}[/]"
    )
