from setuptools import setup

setup(
    name = "j21-tool",
    packages = ["j21tool"],
    version = "0.0.1",
    author = "Lance Liang",
    author_email = "lanceliang2005@gmail.com.com",
    url = "http://github.com/lancesoft23/j21-tool",
    description = "A simple Python script to enable/disable Java21 features",
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
        ],
    long_description = """\
========
boot-tool
========

boot-tool is a pure Python library for working with Spring-boot and Java source
code generation. 
""",
    zip_safe = False,
    install_requires = ['javalang', 'six',],
    tests_require = ["nose",],
    test_suite = "nose.collector",
)
