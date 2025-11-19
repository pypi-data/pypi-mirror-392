import os

from setuptools import setup, find_packages


def get_version():
    return os.getenv("PYRASP_VERSION")


setup(
    name="python-rasp-core",
    version=get_version(),
    description="Python RASP Core Package",
    long_description="Python RASP Core Package",
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
    install_requires=["python-rasp-setup=={}".format(get_version())],
    zip_safe=False,
)
