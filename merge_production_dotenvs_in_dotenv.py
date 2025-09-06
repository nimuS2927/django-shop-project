import sys
from collections.abc import Sequence
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

env_type = sys.argv[1] if len(sys.argv) > 1 else "prod"

if not env_type:
    env_type = "prod"

ERROR_MESSAGE = "Unknown environment type. Use 'prod' or 'local'."

if env_type == "prod":
    DOTENVS_DIR = BASE_DIR / ".envs" / ".production"
elif env_type == "local":
    DOTENVS_DIR = BASE_DIR / ".envs" / ".local"
else:
    raise ValueError(ERROR_MESSAGE)

DOTENV_FILES = [
    DOTENVS_DIR / ".django",
    DOTENVS_DIR / ".postgres",
]

DOTENV_FILE = BASE_DIR / ".env"


def to_docker_path(win_path: Path) -> str:
    path_str = str(win_path).replace("\\", "/")
    if ":" in path_str:
        drive, rest = path_str.split(":", 1)
        drive = drive.lower()
        path_str = f"/run/desktop/mnt/host/{drive}{rest}"
    return path_str


def merge(
    output_file: Path,
    files_to_merge: Sequence[Path],
    *,
    add_base_dir: bool = True,
) -> None:
    merged_content = ""

    if add_base_dir:
        base_dir: Path = Path(__file__).resolve().parent
        docker_base_dir = to_docker_path(base_dir)
        merged_content += f"BASE_DIR={docker_base_dir}\n"

    for merge_file in files_to_merge:
        merged_content += merge_file.read_text()
        merged_content += "\n"
    output_file.write_text(merged_content)


if __name__ == "__main__":
    merge(DOTENV_FILE, DOTENV_FILES)
