import os
import pathlib
import shutil
import sys
import tempfile
from distutils.dir_util import copy_tree
from urllib import request
from zipfile import ZipFile


def run_cmd(cmd, env=None, cwd=None):
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True,
        env=env,
        cwd=cwd,
    ) as p:
        for line in p.stdout:
            print(line, end="")

    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)


def download(url):
    tmp_folder = pathlib.Path(tempfile.mkdtemp())
    filename = url.split("/")[-1]
    filepath = tmp_folder.joinpath(filename)
    with open(filepath, "w+b") as f:
        r = request.urlopen(url)
        for bits in r:
            f.write(bits)
    return filepath


def extract_zip(filepath, dest):
    with ZipFile(filepath, "r") as zip_obj:
        zip_obj.extractall(dest)


def get_python(version, dest, arch="amd64"):
    url = (
        f"https://www.python.org/ftp/python/{version}/python-{version}-embed-{arch}.zip"
    )
    filepath = download(url)
    extract_zip(filepath, dest)


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python winnolo.py python_script.py")
        return

    python_version = sys.version.split()[0]

    script_filename = pathlib.Path(sys.argv[1])
    project_folder = script_filename.parent
    dist_folder = project_folder.parent.joinpath("{}.dist".format(project_folder.name))
    app_folder = dist_folder.joinpath("app")

    print("Generating executable inside {}".format(dist_folder))

    python_folder = dist_folder.joinpath("python")

    dist_folder.mkdir(parents=True, exist_ok=True)
    python_folder.mkdir(parents=True, exist_ok=True)

    # Downloading and extracting python into python_folder
    get_python(version=python_version, dest=python_folder)

    # Copying the project inside dist_folder
    copy_tree(str(project_folder), str(app_folder))

    # Installing python libs from requirements
    run_cmd(
        [
            str(python_folder.joinpath("python.exe")),
            "-m",
            "pip",
            "install",
            "-r",
            str(app_folder.joinpath("requirements.txt")),
        ]
    )


if __name__ == "__main__":
    main()
