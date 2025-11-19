from setuptools import setup, find_packages

# Читаємо README файл для довгого опису на PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='my-sort-Yura-Maksym',  # Назва на PyPI (pip install my-sort)
    version='0.1.2', # Початкова версія
    author='Yura-Maksym', # Вкажіть ваше ім'я
    author_email='your_email@example.com', # Вкажіть ваш email

    description='Кастомна реалізація утиліти sort на Python.',
    long_description=long_description, # Це ми взяли з README
    long_description_content_type='text/markdown',

    url='https://github.com/Ваш_Акаунт/my-sort', # Посилання на репозиторій

    packages=find_packages(), # Ця функція сама знайде папку 'my_sort'

    # Вказуємо залежності. Тепер pip знатиме, що нам потрібен click
    install_requires=[
        'click',
    ],

    # ВАЖЛИВО: Це створює саму команду 'my-sort'
    entry_points={
        'console_scripts': [
            'my-sort = my_sort.main:my_sort',
            # 'ім'я_команди = шлях.до.файлу:назва_функції'
        ],
    },

    # Додаткова мета-інформація
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7', # Вказуємо мінімальну версію Python
)
