#!/usr/bin/env python

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

import importlib.util
from pathlib import Path

root_dir = Path(__file__).parent

package_name = "makora"
description = ""
author = ""
author_email = ""
url = f""
download_url = f""
data_files = {}

version_file = Path(__file__).parent.joinpath(package_name, "version.py")
spec = importlib.util.spec_from_file_location(
    "{}.version".format(package_name), version_file
)
package_version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_version)

long_desc = None
long_desc_type = None
readme_md = Path(__file__).parent.joinpath("README.md")
if readme_md.exists():
    data_files.setdefault("", []).append(readme_md.name)
    with readme_md.open("r") as f:
        long_desc = f.read()
        long_desc_type = "text/markdown"

license = Path(__file__).parent.joinpath("LICENSE")
if license.exists():
    data_files.setdefault("", []).append(license.name)

data_files[package_name] = ["py.typed"]


class dist_info_mixin:
    def run(self):
        _dist_file = version_file.parent.joinpath("_dist_info.py")
        _dist_file.write_text(
            "\n".join(
                map(
                    lambda attr_name: attr_name
                    + " = "
                    + repr(getattr(package_version, attr_name)),
                    package_version.__all__,
                )
            )
            + "\n"
        )
        try:
            ret = super().run()
        finally:
            _dist_file.unlink()
        return ret


class custom_sdist(dist_info_mixin, sdist):
    pass


class custom_wheel(dist_info_mixin, build_py):
    pass


setup(
    name=package_name,
    version=package_version.version,
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    download_url=download_url,
    long_description=long_desc or "",
    long_description_content_type=long_desc_type or "",
    python_requires=">=3.10.0",
    install_requires=[
    ],
    extras_require={
    },
    packages=find_packages(where=".", include=[package_name, package_name + ".*"]),
    package_dir={"": "."},
    package_data=data_files,
    cmdclass={"sdist": custom_sdist, "build_py": custom_wheel},
)
