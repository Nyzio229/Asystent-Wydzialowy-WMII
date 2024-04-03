import argparse

from config import config

def parse_args():
    parser = argparse.ArgumentParser(description="LLM chat completion/embedding server")

    cmd_line_config = config["command_line"]

    parser.add_argument(
        "--host",
        help="Server IP",
        default=cmd_line_config["host"]
    )

    parser.add_argument(
        "--port",
        help="Server port",
        default=cmd_line_config["port"],
        type=int
    )

    parser.add_argument(
        "-m",
        "--model",
        help="Path to the model file (.gguf)",
        required=True
    )

    parser.add_argument(
        "-f",
        "--chat_format",
        help="Chat format",
        default=cmd_line_config["chat_format"]
    )

    parser.add_argument(
        "--n_ctx",
        help="Context window size",
        default=cmd_line_config["n_ctx"],
        type=int
    )

    parser.add_argument(
        "--n_gpu_layers",
        help="Number of GPU layers",
        default=cmd_line_config["n_gpu_layers"],
        type=int
    )

    args = parser.parse_args()

    return args
