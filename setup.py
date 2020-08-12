import setuptools

with open("README.md","r",encoding="utf-8") as fh:
    long_description=fh.read()

setuptools.setup(
        name="baike",
        license="Apache 2.0",
        version="1.4.1",
        author="Lightyears",
        author_email="1MLightyears@gmail.com",
        description="BaiduBaike search bot",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/1MLightyears/baike',
        classifiers=[
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Operating System :: OS Independent",
            "Development Status :: 2 - Pre-Alpha",
            "License :: OSI Approved :: Apache Software License",
            "Natural Language :: Chinese (Simplified)"
        ],
        install_requires=[
            "requests",
            "lxml"
        ],
        python_requires='>=3.6',
        packages=setuptools.find_packages(),
)

