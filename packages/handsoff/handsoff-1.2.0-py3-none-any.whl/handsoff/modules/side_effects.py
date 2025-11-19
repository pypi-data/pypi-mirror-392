from subprocess import run as subpro_run
from os import PathLike

def run_command_(command: str, cwd: PathLike | str | None = None) -> None:
    subpro_run(command, shell=True, cwd=cwd)
    
def read_dotenv_(path: str) -> str:
    return