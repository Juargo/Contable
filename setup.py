from setuptools import setup, find_packages

setup(
    name="contable",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.7",
        "gspread>=5.0.0",
        "oauth2client>=4.1.3",
        "prettytable>=2.0.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Sistema de procesamiento de extractos bancarios y actualización a Google Sheets",
    keywords="excel, bank, sheets, finance",
    python_requires=">=3.6",
)
