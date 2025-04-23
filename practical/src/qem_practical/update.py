import pathlib
rootdir = pathlib.Path(__file__).parent.parent.parent.parent
import subprocess


def update():
    output = subprocess.check_output(
        ['git', 'pull', "--ff-only"],
        cwd=rootdir,
        shell=True,
    )
    print(output.decode('utf-8'))
