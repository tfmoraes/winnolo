import sys
import os
import tempfile
import pathlib
from urllib import request
from zipfile import ZipFile

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
    with ZipFile(filepath, 'r') as zip_obj:
       zip_obj.extractall(dest)


def get_python(version, dest, arch="amd64"):
    url = f"https://www.python.org/ftp/python/{version}/python-{version}-embed-{arch}.zip"
    filepath = download(url)
    extract_zip(filepath, dest)


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python winnolo.py python_script.py")
        return

    script_filename = pathlib.Path(sys.argv[1])
    project_folder = script_filename.parent
    dist_folder = project_folder.joinpath("dist")
    python_folder = dist_folder.joinpath("python")

    dist_folder.mkdir(parents=True, exist_ok=True)
    python_folder.mkdir(parents=True, exist_ok=True)

    get_python(version="3.7.7", dest=python_folder)


if __name__ == "__main__":
    main()
