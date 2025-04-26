import pathlib
import subprocess
rootdir = pathlib.Path(__file__).parent

input_md = rootdir / "slides.md"
with input_md.open() as fp:
    lines = fp.readlines()


stub = '<iframe src="http://localhost:9091'

for idx, line in enumerate(lines):
    if line.startswith(stub):
        fname = line[len(stub):].split('"')[0]
        lines[idx] = f'<img src="figures/panel/tests/{fname}.png" width="auto" height="auto"></img>\n'
    if line.startswith("<!--<!-- _footer:"):
        lines[idx] = line[4:-4]

out_path = input_md.with_stem("index")
try:
    with out_path.open("w") as fp:
        fp.writelines(lines)

    output = subprocess.check_output(
        [
            'npx',
            'marp',
            "--no-config-file",
            "--html",
            "--theme-set",
            "./static/Rose-Pine-For-Marp/css/rose-pine-dawn.css",
            "--output",
            "index.html",
            "--allow-local-files",
            str(out_path),
        ],
        cwd=rootdir,
        shell=True,
    )
    print(output.decode('utf-8'))
finally:
    out_path.unlink(missing_ok=True)
