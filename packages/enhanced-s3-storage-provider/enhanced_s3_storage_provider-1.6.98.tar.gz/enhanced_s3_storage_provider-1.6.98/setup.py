from setuptools import setup
# v 1.6.0 works in case of rollout without pulling from s3
# v 1.6.6 fixes connection pool exhaustion (threadpool_size and max_pool_connections)
# v 1.6.98: Aggressive fix for OpenStack chunked encoding - monkey-patch to remove Transfer-Encoding header
# v 1.6.97: Fixed OpenStack/OBS chunked encoding issue - disable payload signing for compatibility
# v 1.6.96: Added imghdr-based Content-Type detection for local_content files (reads file magic bytes)
# v 1.6.95: Restored full Content-Type detection with regex pattern matching for thumbnails
__version__ = "1.6.98" 

with open("README.md") as f:
    long_description = f.read()

setup(
    name="enhanced-s3-storage-provider",
    version=__version__,
    zip_safe=False,
    author="matrix.org team and contributors",
    description="A storage provider which can fetch and store media in Amazon S3.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elyesbenamor/synapse-s3-storage-provider.git",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    license="Apache-2.0",
    py_modules=["s3_storage_provider"],
    scripts=["scripts/s3_media_upload"],
    install_requires=[
        "boto3>=1.20.0,<2.0",
        "botocore>=1.23.0,<2.0",
        "humanize>=4.0,<5.0",
        "psycopg2-binary>=2.7.5,<3.0",
        "PyYAML>=5.4,<7.0",
        "tqdm>=4.26.0,<5.0",
        "Twisted",
        "minio",
    ],
)