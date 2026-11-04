from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'digit_relay'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='athar',
    maintainer_email='114593329+aaatharazizzz@users.noreply.github.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'relay1 = digit_relay.relay1:main',
            'relay2 = digit_relay.relay2:main',
            'relay3 = digit_relay.relay3:main',
            'relay4 = digit_relay.relay4:main',
        ],
    },
)
