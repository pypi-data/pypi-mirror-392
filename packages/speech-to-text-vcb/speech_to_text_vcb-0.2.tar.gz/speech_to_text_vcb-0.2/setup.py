from setuptools import setup, find_packages

setup(
    name="speech_to_text_vcb",
    version='0.2',
    author="Vishal Chandrabhan Bolke",
    author_email="bolkevishal10@gmail.com",
    description='this is stt file ',
    packages=find_packages(),
    install_requires=[
        "selenium",
        "webdriver_manager"
    ]
)
