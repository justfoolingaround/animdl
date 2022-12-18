import operator
import platform
import re
import sys
from functools import lru_cache

import pkginfo
from packaging import version

python_impl_dict = {
    "CPython": "cp",
    "PyPy": "pp",
    "Jython": "jy",
    "IronPython": "ip",
    "Stackless": "sl",
    "Brython": "br",
}


PYTHON_IMPLEMENTATION = python_impl_dict.get(platform.python_implementation())

if PYTHON_IMPLEMENTATION is None:
    raise ValueError(
        f"Unsupported Python implementation {platform.python_implementation()!r}, will not find wheels."
    )


PACKAGE_NAME = "lxml"
VERSION_EXPR = "~=4.9.1"

PC_ARCH = "win_amd64" if sys.maxsize > 2**32 else "win32"
STRING_REGEX = re.compile(r"&#(\d+);")
ABI_TAG = f"{PYTHON_IMPLEMENTATION}{sys.version_info.major}{sys.version_info.minor}"


def match_version(version_expression: str, version_string: str) -> bool:
    if version_expression is None:
        return True

    def single_matcher(single_expression: str):

        target_version = single_expression.lstrip("=<>~")
        expr = single_expression[: -len(target_version)]

        target = version.parse(target_version)
        current = version.parse(version_string)

        operators = {
            "==": operator.eq,
            ">=": operator.ge,
            "<=": operator.le,
            ">": operator.gt,
            "<": operator.lt,
            "~=": lambda x, y: (x.major == y.major and x.minor == y.minor) or x >= y,
        }

        user_operator = operators.get(expr)

        if user_operator is None:
            raise ValueError(f"Invalid version expression {expr!r}")

        return user_operator(current, target)

    return all(
        single_matcher(single_expression)
        for single_expression in version_expression.split(",")
    )


@lru_cache()
def get_packages_page(session):
    return session.get(
        "https://www.lfd.uci.edu/~gohlke/pythonlibs/", follow_redirects=True
    ).text


def iter_packages(
    session, package_name, version_expression: str = None, pc_arch: str = PC_ARCH
):

    WHEELS_REGEX = re.compile(rf"]'>({package_name}.+?{pc_arch}&#46;whl)<")

    for _ in WHEELS_REGEX.finditer(get_packages_page(session)):
        package = STRING_REGEX.sub(lambda match: chr(int(match.group(1))), _.group(1))

        _, package_version, *abis, _ = package.split("‑")

        if match_version(version_expression, package_version) and ABI_TAG in abis:
            yield "https://download.lfd.uci.edu/pythonlibs/archived/" + package.replace(
                "‑", "-"
            )


def resolve(packages, *, prefix="[animdl/utils/win32-build-inquirer]"):
    import subprocess

    import httpx

    pip_install_args = [sys.executable, "-m", "pip", "install"]

    session = httpx.Client()

    for package, version_expr in packages:

        pkg = pkginfo.get_metadata(package)

        if pkg is not None and match_version(version_expr, pkg.version):
            continue

        pip_pkg_string = package + (version_expr if version_expr else "")

        print(
            prefix, f"{pip_pkg_string!r} is not installed, trying to install from PyPI."
        )

        pip_process = subprocess.Popen(
            pip_install_args + [pip_pkg_string],
        )
        pip_process.wait()

        if pip_process.returncode == 0:
            continue

        print(
            prefix,
            f"Failed to install {pip_pkg_string!r} from PyPI, trying to install from the build inquiry.",
        )

        if sys.platform != "win32":
            raise RuntimeError(
                f"Failed to install {pip_pkg_string!r} with pip. Build inquiry is not supported on {sys.platform!r}."
            )

        urls = list(iter_packages(session, package, version_expr))

        if not urls:
            raise RuntimeError(
                f"Failed to find a wheel for {pip_pkg_string!r} in the build inquiry."
            )

        selection = urls[0]

        print(prefix, f"Installing {pip_pkg_string!r} from {selection!r}.")

        pip_process = subprocess.Popen(
            pip_install_args + [selection],
        )
        pip_process.wait()

        if pip_process.returncode != 0:
            raise RuntimeError(
                f"Failed to install {pip_pkg_string!r} from the build inquiry, please raise an issue if this is persistent"
            )
