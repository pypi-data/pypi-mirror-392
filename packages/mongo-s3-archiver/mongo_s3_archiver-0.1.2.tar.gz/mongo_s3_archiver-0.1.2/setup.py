import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="mongo-s3-archiver",
    version="v0.1.2",
    description="Backup utility for MongoDB. "
                "Compatible with Azure, Amazon Web Services and Google Cloud Platform.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hadikoub/mongo-s3-archiver",
    author="Vladislav I. Kulbatski ",
    author_email="hi@exesse.org",
    maintainer="Hadi Koubeissy",
    maintainer_email="123.hadikoubeissy@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["mongo_s3_archiver"],
    include_package_data=False,
    project_urls={
        "Source": "https://github.com/hadikoub/mongo-s3-archiver",
        "Upstream Project": "https://github.com/exesse/mongodump-s3",
    },
    install_requires=[
        "requests>=2.26.0",
        "hurry.filesize==0.9",
        "python-dotenv>=0.18.0",
        "azure-storage-blob>=12.8.1",
        "boto3>=1.17.111",
        "google-cloud-storage>=1.41.0",
        "pymongo>=4.0.0"
        ],
    entry_points={
        "console_scripts": [
            "mongo-s3-archiver=mongo_s3_archiver.__main__:main",
            "mongodump-s3=mongo_s3_archiver.__main__:main",
        ]
    },
)
