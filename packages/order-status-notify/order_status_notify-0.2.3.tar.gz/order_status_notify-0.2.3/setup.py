from setuptools import setup, find_packages

setup(
    name='order_status_notify',
    version='0.2.3',
    packages=find_packages(),
    install_requires=[
        'Django>=3.2,<4.0',
    ],
    author='Hetik',
    author_email='hetikchandaria66@gmail.com',
    description='A lightweight Django utility for sending email notifications on order status updates.',
    long_description=open('README.md').read() if open('README.md', 'r') else '',
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/order-status-notify/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
