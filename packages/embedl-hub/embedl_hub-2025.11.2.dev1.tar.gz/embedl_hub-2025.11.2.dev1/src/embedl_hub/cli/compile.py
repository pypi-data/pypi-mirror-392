# Copyright (C) 2025 Embedl AB

"""
embedl-hub compile - send an model to Qualcomm AI Hub, retrieve a
device-specific binary (.tflite for tflite, .bin for qnn, or .onnx for onnxruntime).
"""

from pathlib import Path

import typer

# All other embedl_hub imports should be done inside the function.
from embedl_hub.cli.helper import (
    DEVICE_HELPER,
    OUTPUT_FILE_HELPER,
    SIZE_HELPER,
)

compile_cli = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=True,
)


@compile_cli.command("compile")
def compile_command(
    ctx: typer.Context,
    model: Path = typer.Option(
        ...,
        "-m",
        "--model",
        help="Path to the TorchScript model file, ONNX model file, or to a directory "
        "containing the ONNX model and any associated data files, to be compiled.",
        show_default=False,
    ),
    device: str = typer.Option(
        ...,
        "-d",
        "--device",
        help=DEVICE_HELPER,
        show_default=False,
    ),
    size: str = typer.Option(
        ...,
        "--size",
        "-s",
        help=SIZE_HELPER,
        show_default=False,
    ),
    runtime: str = typer.Option(
        ...,
        "-r",
        "--runtime",
        help="Runtime backend for compilation: tflite, qnn, or onnx.",
    ),
    quantize_io: bool = typer.Option(
        False,
        "--quantize-io",
        help="Quantize input and output tensors. "
        "Improves performance on platforms that support quantized I/O.",
        show_default=True,
    ),
    output_file: str = typer.Option(
        None,
        "-o",
        "--output-file",
        help=OUTPUT_FILE_HELPER,
        show_default=False,
    ),
):
    """
    Compile a model into a device ready binary using Qualcomm AI Hub.
    Qualcomm AI Hub may return a zip file containing multiple files.

    Required arguments:
        --model
        --size
        --device
        --runtime

    Examples
    --------

    Compile the ONNX model `fp32_model.onnx` with input size 1x3x224x224 for the Samsung Galaxy S24 using the tflite runtime:

        $ embedl-hub compile -m fp32_model.onnx  --size 1,3,224,224 -d "Samsung Galaxy S24" -r tflite

    Compile the TorchScript model `model.pt` with input size 1x3x224x224
    for the Samsung Galaxy S24, and save it to `./my_outputs/model.onnx`:

        $ embedl-hub compile -m model.pt  -r onnx --size 1,3,224,224 --device "Samsung Galaxy S24" -o ./my_outputs/model.onnx

    """

    # pylint: disable=import-outside-toplevel
    from tempfile import TemporaryDirectory

    from embedl_hub.cli.utils import assert_api_config, prepare_compile_kwargs
    from embedl_hub.core.compile import (
        CompileError,
        CompileResult,
        QAIHubCompiler,
    )
    from embedl_hub.core.context import require_initialized_ctx
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    assert_api_config()
    require_initialized_ctx(ctx.obj["config"])

    with TemporaryDirectory() as tmpdir:
        compile_kwargs = prepare_compile_kwargs(
            model, device, runtime, size, tmpdir, quantize_io, output_file
        )
        compiler = QAIHubCompiler(
            device=compile_kwargs["device"],
            runtime=compile_kwargs["runtime"],
            quantize_io=compile_kwargs["quantize_io"],
            output_file=compile_kwargs["output_file"],
            input_size=compile_kwargs["input_size"],
        )
        try:
            res: CompileResult = compiler.compile(
                project_name=ctx.obj["config"]["project_name"],
                experiment_name=ctx.obj["config"]["experiment_name"],
                model_path=model,
            )
            console.print(
                f"[green]✓ Compiled model for {res.device} and save at {res.model_path}[/]"
            )

            # TODO: upload artifacts to web
        except (CompileError, ValueError) as error:
            console.print(f"[red]✗ {error}[/]")
            raise typer.Exit(1)
