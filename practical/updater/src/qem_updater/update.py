import pathlib
rootdir = pathlib.Path(__file__).parent.parent.parent.parent.parent
import subprocess


def update():
    print(f"Updating from {rootdir}")
    output = subprocess.check_output(
        ['git', 'pull', "--ff-only"],
        cwd=rootdir,
        shell=True,
    )
    print(output.decode('utf-8'))

    output = subprocess.check_output(
        ['uv', 'pip', "install", "-e", "."],
        cwd=rootdir / "practical",
        shell=True,
    )
    print(output.decode('utf-8'))
