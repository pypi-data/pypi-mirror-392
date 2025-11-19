from setuptools import setup, find_packages

setup(
  name="policy-uploader-sdk",
  version= '0.1.0',
  description='Library to upload mobile insurance document to s3 bucket',
  long_description=open('README.md').read(),
  author='Gaurv Kumar',
  maintainer='Gaurav Kumar',
  packages=find_packages(),
  install_requires=[
    'boto3',
  ]
)