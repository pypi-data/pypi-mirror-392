from setuptools import setup, find_packages

setup(
    name="wxw",
    version="1.0.5.dev", 
    keywords=["pip", "wxw"],
    description="A library for wxw",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="weixianwei",
    author_email="weixianwei0129@gmail.com",
    url="https://github.com/weixianwei0129/wxwLibrary",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    platforms="any",
    install_requires=[],
    extras_require={"dev": []},
    entry_points={
        "console_scripts": [
            "wxw-cameras = wxw.scripts.cameras:main",
            "wxw-fixvscode = wxw.scripts.fix_vscode_jump:main",
        ]
    },
)
