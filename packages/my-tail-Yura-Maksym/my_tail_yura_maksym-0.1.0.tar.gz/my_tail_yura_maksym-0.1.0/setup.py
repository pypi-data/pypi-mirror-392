from setuptools import setup, find_packages

# Читаємо README файл
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='my-tail-Yura-Maksym',  # Унікальна назва, щоб не було конфлікту
    version='0.1.0', # Починаємо знову з 0.1.0
    author='Yura Maksym', # Вкажіть ваше ім'я
    author_email='your_email@example.com', # Вкажіть ваш email

    description='A custom implementation of the tail utility in Python. Supports -n and -f.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/Yura-Maksym/my-tail', # Посилання на репозиторій my-tail

    packages=find_packages(), # Знаходить папку my_tail
    install_requires=[
        'click',
    ],

    # Створюємо команду 'my-tail'
    entry_points={
        'console_scripts': [
            # 'ім'я_команди = шлях.до.файлу:назва_функції'
            'my-tail = my_tail.main:my_tail',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)