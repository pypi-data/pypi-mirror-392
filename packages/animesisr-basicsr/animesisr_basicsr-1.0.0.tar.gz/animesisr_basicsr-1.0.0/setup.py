#!/usr/bin/env python
import os
import subprocess
import time
from setuptools import setup

version_file = 'basicsr/version.py'

def get_git_hash():
    """Get git hash."""
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH', 'HOME']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        sha = out.strip().decode('ascii')
    except OSError:
        sha = 'unknown'

    return sha

def get_hash():
    """Get git hash or use 'unknown'."""
    if os.path.exists('.git'):
        sha = get_git_hash()[:7]
    else:
        sha = 'unknown'
    return sha

def write_version_py():
    """Dynamically generate the version file."""
    content = """# GENERATED VERSION FILE
# TIME: {}
__version__ = '{}'
__gitsha__ = '{}'
version_info = ({})
"""
    sha = get_hash()
    # VERSION file should exist in the repo root
    with open('VERSION', 'r') as f:
        SHORT_VERSION = f.read().strip()
    VERSION_INFO = ', '.join([x if x.isdigit() else f'"{x}"' for x in SHORT_VERSION.split('.')])

    version_file_str = content.format(time.asctime(), SHORT_VERSION, sha, VERSION_INFO)
    with open(version_file, 'w') as f:
        f.write(version_file_str)

if __name__ == '__main__':
    write_version_py()

    cuda_ext = os.getenv('BASICSR_EXT')
    ext_modules = []
    setup_kwargs = {}
    if cuda_ext == 'True':
        try:
            import torch
            from torch.utils.cpp_extension import BuildExtension, CppExtension, CUDAExtension
        except ImportError:
            raise ImportError('Unable to import torch - torch is needed to build cuda extensions')

        def make_cuda_ext(name, module, sources, sources_cuda=None):
            if sources_cuda is None:
                sources_cuda = []
            define_macros = []
            extra_compile_args = {'cxx': []}

            if torch.cuda.is_available() or os.getenv('FORCE_CUDA', '0') == '1':
                define_macros += [('WITH_CUDA', None)]
                extension = CUDAExtension
                extra_compile_args['nvcc'] = [
                    '-D__CUDA_NO_HALF_OPERATORS__',
                    '-D__CUDA_NO_HALF_CONVERSIONS__',
                    '-D__CUDA_NO_HALF2_OPERATORS__',
                ]
                sources += sources_cuda
            else:
                print(f'Compiling {name} without CUDA')
                extension = CppExtension

            return extension(
                name=f'{module}.{name}',
                sources=[os.path.join(*module.split('.'), p) for p in sources],
                define_macros=define_macros,
                extra_compile_args=extra_compile_args)

        ext_modules = [
            make_cuda_ext(
                name='deform_conv_ext',
                module='basicsr.ops.dcn',
                sources=['src/deform_conv_ext.cpp'],
                sources_cuda=['src/deform_conv_cuda.cpp', 'src/deform_conv_cuda_kernel.cu']),
            make_cuda_ext(
                name='fused_act_ext',
                module='basicsr.ops.fused_act',
                sources=['src/fused_bias_act.cpp'],
                sources_cuda=['src/fused_bias_act_kernel.cu']),
            make_cuda_ext(
                name='upfirdn2d_ext',
                module='basicsr.ops.upfirdn2d',
                sources=['src/upfirdn2d.cpp'],
                sources_cuda=['src/upfirdn2d_kernel.cu']),
        ]
        setup_kwargs = dict(cmdclass={'build_ext': BuildExtension})

    setup(
        ext_modules=ext_modules,
        **setup_kwargs
    )
