from setuptools import setup, find_packages

setup(
    name='discordclients',
    version='0.1.6',
    description='Usage of DiscordAPI',
    author='Momwhyareyouhere',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.7',
)
