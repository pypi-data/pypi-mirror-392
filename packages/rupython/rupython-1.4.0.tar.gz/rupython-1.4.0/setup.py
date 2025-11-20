from setuptools import setup as Установить
from pathlib import Path as Путь

Установить(
    name = 'rupython',
    version = '1.4.0',
    description = "Исполнитель кода Русского Питона",
    packages = [ 'rupython', 'rupython.Модули' ],
    long_description = (Путь(__file__).parent / 'README.md').read_text('UTF-8'),
    long_description_content_type = 'text/markdown',
    python_requires = '>=3.8',

    classifiers = [
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Natural Language :: Russian'
    ],

    author='Сообщество русских программистов',
    license='ОДРН',
    keywords='Россия, русский язык',
    url = 'https://gitflic.ru/project/russky/rupython'
)
