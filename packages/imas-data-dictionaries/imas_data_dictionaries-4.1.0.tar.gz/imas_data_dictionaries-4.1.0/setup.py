from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import setuptools
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.sdist import sdist


def build_zip_file():
    curdir = Path(__file__).parent.resolve()
    files_to_store = list(curdir.glob("*/*.xml"))

    if not files_to_store:
        # Installation from an sdist which already built the zip file
        return

    with ZipFile(
        curdir / "imas_data_dictionaries/imas_data_dictionaries.zip",
        "w",
        compression=ZIP_DEFLATED,
        # Use best available compression to reduce filesize of distributions
        compresslevel=9,
    ) as zipfile:
        for file in curdir.glob("data-dictionary/*.xml"):
            zipfile.write(file, arcname=Path(*file.parts[-2:]))
        for file in curdir.glob("identifiers/*/*.xml"):
            zipfile.write(file, arcname=Path(*file.parts[-3:]))


class BuildZipFileBeforeSdist(sdist):
    def run(self):
        build_zip_file()
        return super().run()


class BuildZipFileBeforeWheel(bdist_wheel):
    def run(self):
        build_zip_file()
        return super().run()


setuptools.setup(
    cmdclass=dict(
        sdist=BuildZipFileBeforeSdist,
        bdist_wheel=BuildZipFileBeforeWheel,
    )
)
