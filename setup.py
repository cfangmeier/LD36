from os import remove
from os.path import isfile
from distutils.core import setup
from distutils.extension import Extension

from Cython.Build import cythonize
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
    name='Ludum Dare 36 Submission',
    description='''Ludum Dare 36 Submission''',
    author='Caleb Fangmeier',
    author_email='caleb@fangmeier.tech',
    ext_modules=velocity_extensions,
    cmdclass={},
    packages=[
        'velocity_module',
        ],
    package_dir={'velocity_module': 'velocity_module'})
