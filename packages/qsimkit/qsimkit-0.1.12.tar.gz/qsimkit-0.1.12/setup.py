import setuptools
import subprocess
import os

# Try to get version from git, fall back to VERSION file if not in a git repo
package_version = None

# First, try to read from existing VERSION file (used when building from sdist)
if os.path.isfile("qsimkit/VERSION"):
    with open("qsimkit/VERSION", "r", encoding="utf-8") as fh:
        package_version = fh.read().strip()

# If not available, try to get from git (used when building from git repo)
if not package_version:
    try:
        result = subprocess.run(
            ["git", "describe", "--tags"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        package_version = result.stdout.decode("utf-8").strip()

        if "-" in package_version:
            # when not on tag, git describe outputs: "1.3.3-22-gdf81228"
            # pip has gotten strict with version numbers
            # so change it to: "1.3.3+22.git.gdf81228"
            # See: https://peps.python.org/pep-0440/#local-version-segments
            v,i,s = package_version.split("-")
            # package_version = v + "+" + i + ".git." + s
            package_version = v

        # Write version to file for sdist
        assert os.path.isfile("qsimkit/version.py")
        with open("qsimkit/VERSION", "w", encoding="utf-8") as fh:
            fh.write("%s\n" % package_version)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git not available or not a git repo
        pass

# Final fallback: use a default version
if not package_version:
    package_version = "0.0.0"

assert "-" not in package_version
assert "." in package_version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qsimkit",
    version=package_version,
    author="Jue XU",
    author_email="xujue@connect.hku.hk",
    description="Quantum Simulation Toolkit - Error bounds and Trotterization tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jue-Xu/Qsimkit",
    packages=setuptools.find_packages(),
    package_data={"qsimkit": ["VERSION"]},
    include_package_data=True,
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.10",
    entry_points={"console_scripts": ["qsimkit = qsimkit.main:main"]},
    install_requires=[
        "qiskit >= 1.0.2",
        "qiskit-aer>=0.17.2",
        "jaxlib >= 0.6.2",
        "jax >= 0.6.2",
        "openfermion >= 1.5.1",
        "openfermionpyscf >= 0.5",
        "matplotlib >= 3.8.2",
        "numpy >= 1.23.5",
        "pandas >= 2.2.2",
        "scipy >= 1.12.0",
        "colorspace>=1.0.0",
        "multiprocess>=0.70.16",
    ],
)