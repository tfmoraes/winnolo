import os
import pathlib
import shutil
import sys
import tempfile
from distutils.dir_util import copy_tree
from urllib import request
from zipfile import ZipFile
import subprocess

IGNORE_PATTERNS = ('.pyc','CVS','.git','tmp','.svn')


def download_and_install_pip(python_exec):
    pip_path = download("https://bootstrap.pypa.io/get-pip.py")
    run_cmd([str(python_exec), str(pip_path)])


def pip_install(python_exec, pip_package):
    print("Installing packages using pip")
    run_cmd([str(python_exec), "-m", "pip", "install", pip_package])


def run_cmd(cmd, env=None, cwd=None):
    print("Running command", " ".join(cmd))
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


def download(url, filepath=None):
    print(f"Downloading {url}")
    if filepath is None:
        tmp_folder = pathlib.Path(tempfile.mkdtemp())
        filename = url.split("/")[-1]
        filepath = tmp_folder.joinpath(filename)
    with open(filepath, "w+b") as f:
        r = request.urlopen(url)
        for bits in r:
            f.write(bits)
    return filepath


def extract_zip(filepath, dest):
    print(f"Extracting {filepath} to {dest}")
    with ZipFile(filepath, "r") as zip_obj:
        zip_obj.extractall(dest)


def get_python(version, dest, arch="amd64"):
    print(f"Getting Python-{version}")
    version_2dig = ".".join(version.split('.')[:2])
    url = (
        f"https://sourceforge.net/projects/portable-python/files/Portable%20Python%20{version_2dig}/Portable%20Python-{version}%20x64.exe/download"
    )
    filepath = download(url, dest.joinpath("ppython.exe"))
    # Extracting python
    run_cmd([str(filepath.resolve()), "-y"], cwd=str(dest))
    # Removing zip python
    filepath.unlink()
    # Removing unneeded files and folder
    ppython_folder = dest.joinpath(f"Portable Python-{version} x64")
    shutil.copytree(str(ppython_folder.joinpath("App/Python")), str(dest), ignore=shutil.ignore_patterns(*IGNORE_PATTERNS), dirs_exist_ok=True)
    shutil.rmtree(ppython_folder, ignore_errors=True)
    shutil.rmtree(dest.joinpath("tcl"), ignore_errors=True)
    shutil.rmtree(dest.joinpath("include"), ignore_errors=True)
    shutil.rmtree(dest.joinpath("Doc"), ignore_errors=True)
    shutil.rmtree(dest.joinpath("Scripts"), ignore_errors=True)
    shutil.rmtree(dest.joinpath("Tools"), ignore_errors=True)


def compress_upx(folder):
    patterns = ("pyd", "dll", "exe")
    for pattern in patterns:
        for fname in folder.glob(f"**/*.{pattern}"):
            try:
                run_cmd(["upx", "-1", str(fname.resolve())])
            except subprocess.CalledProcessError:
                pass


def compile_pyc(python_exec, folder):
    run_cmd([python_exec, "-m", "compileall", str(folder)])
    for fname in folder.glob("**/.py"):
        fname.unlink()


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
    python_exec = str(python_folder.joinpath("python.exe"))

    if dist_folder.exists():
        shutil.rmtree(dist_folder, ignore_errors=True)
    dist_folder.mkdir(parents=True, exist_ok=True)
    python_folder.mkdir(parents=True, exist_ok=True)

    # Downloading and extracting python into python_folder
    get_python(version=python_version, dest=python_folder)

    # Copying the project inside dist_folder
    shutil.copytree(str(project_folder), str(app_folder), ignore=shutil.ignore_patterns(*IGNORE_PATTERNS), dirs_exist_ok=True)
    
    #shutil.rmtree(app_folder.joinpath(".git"))

    # Download and install pip
    # download_and_install_pip(python_exec)

    # Installing python libs from requirements
    run_cmd(
        [
            python_exec,
            "-m",
            "pip",
            "install",
            "-r",
            str(app_folder.joinpath("requirements.txt")),
        ]
    )

    # Copying launcher
    shutil.copyfile(pathlib.Path("launcher/launcher.exe"), dist_folder.joinpath("launcher.exe"))

    #compress_upx(dist_folder)

    #compile_pyc(python_exec, dist_folder)

if __name__ == "__main__":
    main()
