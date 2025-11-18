from setuptools import setup, find_packages

setup(
    name="datahero",
    version="0.1.0",
    description="AI-powered data explanation and insights library",
    author="Ganeshamoorthy",
    author_email="ganeshms110@gmail.com",
    url="https://www.linkedin.com/in/ganeshamoorthy-s-8466b7332",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib"
    ],
    python_requires=">=3.8",
)
