# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs
import os

# Configuration pour éviter les avertissements NumPy array_api
os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'

block_cipher = None

# Collect essential modules
torch_hidden_imports = collect_submodules('torch', filter=lambda name: not any(x in name for x in [
    'testing', 'distributed', 'cuda', 'hip', 'cpp', 'autograd._functions', 'utils.tensorboard',
    'utils.bottleneck', 'utils.cpp_extension', 'onnx', 'caffe2'
]))

torchvision_hidden_imports = collect_submodules('torchvision', filter=lambda name: not any(x in name for x in [
    'testing', 'datasets', 'models', 'cuda', 'cpp', 'io._video_opt'
]))

numpy_hidden_imports = collect_submodules('numpy', filter=lambda name: not any(x in name for x in [
    'testing', 'distutils', 'f2py', 'array_api', 'core.tests', 'lib.tests'
]))

# Liste des DLLs essentielles
essential_dlls = {
    'torch': ['torch_cpu.dll', 'c10.dll'],
    'numpy': ['libopenblas64_.dll'],
    'PyQt6': ['Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll'],
}

# Collect only essential DLLs
def collect_essential_dlls():
    dlls = []
    for package, dll_list in essential_dlls.items():
        package_dlls = collect_dynamic_libs(package)
        dlls.extend([dll for dll in package_dlls if any(essential in dll[0] for essential in dll_list)])
    return dlls

a = Analysis(
    ['C:\\DEV\\RAG_Doc-analyzer\\src\\main.py'],
    pathex=[],
    binaries=collect_essential_dlls(),
    datas=[
        ('C:\\DEV\\RAG_Doc-analyzer\\build\\resources', 'resources'),
        ('C:\\DEV\\RAG_Doc-analyzer\\build\\version.json', 'version.json'),
        *collect_data_files('numpy', include_py_files=False, subdir='core'),
    ],
    hiddenimports=[
        *torch_hidden_imports,
        *torchvision_hidden_imports,
        *numpy_hidden_imports,
        'numpy.core._methods',
        'numpy.lib.format',
        'numpy._typing',
        'numpy.random',
        'sentence_transformers',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'spacy',
        'scikit-learn',
        'structlog',
        'pydantic',
        'requests',
        'packaging'
    ],
    hookspath=[],
    hooksconfig={
        'torch': {
            'lib_package': True,
            'include_cuda': False
        },
        'numpy': {
            'include_np_core': True,
            'include_tests': False,
            'include_experimental': False
        }
    },
    runtime_hooks=[],
    excludes=[
        # Modules de test
        'pytest', 'unittest', 'sphinx', 'numpy.testing', 'torch.testing',
        
        # Outils de build et compilation
        'numpy.distutils', 'numpy.f2py', 'torch.utils.cpp_extension',
        
        # Fonctionnalités expérimentales et dépréciées
        'numpy.array_api', 'torch.distributed',
        
        # Modules non utilisés de torch
        'torch.cuda', 'torch.hip', 'torch.utils.bottleneck',
        'torch.utils.tensorboard', 'torch.onnx', 'torch.caffe2',
        
        # Modules non utilisés de torchvision
        'torchvision.datasets', 'torchvision.models',
        'torchvision.io._video_opt',
        
        # Autres modules non essentiels
        'tkinter', 'matplotlib', 'IPython', 'notebook', 'PIL.ImageQt',
        'PySide2', 'PySide6', 'PyQt4', 'PyQt5',
        'email', 'html', 'http', 'multiprocessing', 'xml',
        'xmlrpc', 'socket', 'distutils'
    ],
    noarchive=False,
    optimize=2,
)

# Fonction pour filtrer les binaires
def filter_binaries(binaries):
    return [(binary, name) for binary, name in binaries if not any(x in binary.lower() for x in [
        'cudnn', 'cublas', 'cufft', 'curand', 'cusolver', 'cusparse',  # CUDA
        'nvrtc', 'nvToolsExt', 'opencv',  # NVIDIA et OpenCV
        'mkl_', 'libiomp',  # MKL
        'test', 'example', 'demo',  # Tests et exemples
        'qt5', 'pyside',  # Qt5 et PySide
    ])]

# Filtrer les binaires
a.binaries = filter_binaries(a.binaries)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RAG_Analyzer_1.0.0_windows_amd64',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'python*.dll',
        'Qt6Core.dll',
        'Qt6Gui.dll',
        'Qt6Widgets.dll',
        'libopenblas64_.dll'
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\DEV\\RAG_Doc-analyzer\\resources\\assets\\icon.ico'],
)
