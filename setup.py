from datetime import datetime
from subprocess import check_output, CalledProcessError

from setuptools import setup, find_packages
from warnings import warn


def version():
    date_string = datetime.now().strftime("1.%Y%m%d.%H%M%S")
    try:
        git_sha = check_output(["git", "describe", "--always", "--dirty=dirty", "--match=NOTHING"]).strip().decode()
        return "{}+{}".format(date_string, git_sha)
    except (CalledProcessError, OSError) as e:
        warn("Error calling git: {}".format(e))
    return date_string


GENERIC_REQ = [
    "Flask==0.12.2",
    "boto3==1.5.24",
]

CODE_QUALITY_REQ = [
    'prospector',
]

TESTS_REQ = [
    'tox==2.9.1',
    'pytest-html',
    'pytest-cov',
    'pytest-helpers-namespace',
    'pytest >= 3.0',
    "moto==1.2.0",
]

setup(
    name="fiaas-ais",
    url="https://github.com/fiaas/ais",
    author="FIAAS developers",
    author_email="fiaas@googlegroups.com",
    version=version(),
    packages=find_packages(exclude=("tests",)),
    zip_safe=True,
    # Requirements
    install_requires=GENERIC_REQ,
    setup_requires=['pytest-runner', 'wheel', 'setuptools_scm'],
    extras_require={
        "dev": TESTS_REQ + CODE_QUALITY_REQ,
        "ci": ["tox==2.9.1", "tox-travis"],
    },
    tests_require=TESTS_REQ,
    entry_points={"console_scripts": ['ais=ais:main']},
)
