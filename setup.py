from setuptools import setup, find_packages
import sys, os

description = "Adds the stream-processing to protobuf messages that you "\
              "usually need to add yourself. "

long_description =\
"Extends protobuf messaging with stream-processing. Serialization will "\
"include length and type. protobufp also includes a receive-buffer to "\
"collect byte chunks, detect when a complete message has been received, and "\
"automatically deserialize to the correct message type."

setup(name='protobufp',
      version='0.2.3',
      description=description,
      long_description=long_description,
      classifiers=[],
      keywords='protobuf translator translation protocol protocols',
      author='Dustin Oprea',
      author_email='myselfasunder@gmail.com',
      url='https://github.com/dsoprea/protobufp',
      license='GPL 2',
      packages=find_packages(exclude=['test']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
      entry_points="",
)

