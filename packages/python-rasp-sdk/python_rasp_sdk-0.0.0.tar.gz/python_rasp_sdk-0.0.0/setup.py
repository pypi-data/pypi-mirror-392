import os

from setuptools import setup, find_packages


def get_version():
    return os.getenv("PYRASP_VERSION")


setup(
    name="python-rasp-sdk",
    version=get_version(),
    description="Python RASP Packages",
    long_description="Python RASP Packages",
    long_description_content_type="text/markdown",
    author="Alibaba Cloud",
    author_email="security@alibaba-inc.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "aliyunrasp": ["data/*"],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    install_requires=[
        "python-rasp-core=={}".format(get_version()),
        "python-rasp-update=={}".format(get_version()),
    ],
    extras_require={
        "all": [
            "requests>=2.20.0",
            "PyYAML>=5.1",
            "watchdog>=2.0.0",
            "wrapt>=1.10.0",
        ]
    },
    zip_safe=False,
)
