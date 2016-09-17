from os import remove
from os.path import isfile
from distutils.core import setup
from distutils.extension import Extension

from Cython.Build import cythonize
# from Cython.Distutils import build_ext
import sys

platform = sys.platform
if platform == 'win32':
    cstdarg = '-std=gnu99'
else:
    cstdarg = '-std=c99'


velocity_modules = {
    'app.tilesystem': ['app/tilesystem.pyx', ],
    }

check_for_removal = ['velocity_module/velocity.c', ]


def build_ext(ext_name, files, include_dirs=[]):
    return Extension(ext_name, files, include_dirs,
                     extra_compile_args=[cstdarg, '-ffast-math'])


def build_extensions_for_modules(modules):
    ext_list = []
    for module_name in modules:
        ext = build_ext(module_name, modules[module_name])
        ext_list.append(ext)
    return cythonize(ext_list)


for file_name in check_for_removal:
    if isfile(file_name):
        remove(file_name)

velocity_extensions = build_extensions_for_modules(velocity_modules)


setup(
    name='KivEnt Velocity Module',
    description='''A game engine for the Kivy Framework.
        https://github.com/Kovak/KivEnt for more info.''',
    author='Jacob Kovac',
    author_email='kovac1066@gmail.com',
    ext_modules=velocity_extensions,
    cmdclass={},
    packages=[
        'velocity_module',
        ],
    package_dir={'velocity_module': 'velocity_module'})
