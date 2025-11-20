#!/usr/bin/env python

"""
setup.py file for ctypes-ified wndchrm
"""

from setuptools import setup, Extension
import os, sys, shutil

__version__ = None
def Fix_tiff_h ():
	# from https://stackoverflow.com/a/65776297/2104010
	# 	copy the tiff.h library header from /usr/include/x86_64-linux-gnu/tiff.h to venv/include/
	try:
		import libtiff
	except ValueError:
		root_path = os.path.join (sys.base_prefix, 'include')
		src_tiff_h = None
		for root, dirs, files in os.walk(root_path):
			for file in files:
				if file == 'tiff.h':
					src_tiff_h = os.path.join (root,file)
					break
		dst_tiff_h = os.path.join (sys.prefix, 'include', 'tiff.h')
		if src_tiff_h:
			shutil.copyfile(src_tiff_h, dst_tiff_h)

def GetVersions ():
	print ('Getting version info')
	pkg_base = os.path.dirname( os.path.realpath(__file__))
	libcharm_base = os.path.join(pkg_base, 'src', 'libcharm' )
	pkg_dir = os.path.join(pkg_base, 'src', 'CharmFeatures' )
	PY3 = sys.version_info.major == 3
	PY2 = sys.version_info.major == 2
	# this sets the __version__ variable initially to the library version
	# In the library's code distribution the version string is in the file src/VERSION
	print ('working from: ',libcharm_base)
	with open(os.path.join (libcharm_base, 'src', 'VERSION')) as f:
		__lib_version__ = f.read().strip()
		with open( os.path.join( libcharm_base, '_lib_version.py' ), 'w+' ) as f:
			f.write( "__lib_version__ = '{0}'\n".format( __lib_version__) )
		print ('wrote {} to {}: '.format(__lib_version__, os.path.join( libcharm_base, '_lib_version.py' )))

	__version__ = __lib_version__
	if PY3:
		exec(open(os.path.join (pkg_dir,'_version.py')).read())
	else:
		execfile(os.path.join (pkg_dir,'_version.py'))

	try:
		from subprocess import check_output
		with open(os.devnull, 'w') as DEVNULL:
			os.chdir (pkg_base)
			git_hash = check_output(['git', 'rev-parse', '--short', 'HEAD'], stderr=DEVNULL ).decode("utf-8").strip()
			# Check for local modifications
			localmod = check_output(['git', 'diff-index', '--name-only', 'HEAD'], stderr=DEVNULL ).decode("utf-8").strip()
			if len(localmod) > 0:
				# print ('localmod\n', localmod, "\n")
				git_hash += '.localmod'
			print ("Building WND-CHARM {} at git repo commit {}...".format( __version__, git_hash ))
		# this construction matches what is done in __init__.py by importing
		# both _version.py and _git_hash.py use "normalized" semantic version string (a.k.a., dots)
		__version__ = __version__+ '+' + git_hash
		with open( os.path.join( pkg_dir, '_git_hash.py' ), 'w+' ) as f:
			f.write( "__git_hash__ = '{0}'\n".format( git_hash) )
	except Exception as e:
		print ("Building WND-CHARM {} release version...".format( __version__ ))
	return (__version__)


__version__ = GetVersions()
Fix_tiff_h()


libcharm_module = Extension('libcharm',
	sources=[
		'src/libcharm/src/colors/FuzzyCalc.cpp',
		'src/libcharm/src/statistics/CombFirst4Moments.cpp',
		'src/libcharm/src/statistics/FeatureStatistics.cpp',
		'src/libcharm/src/textures/gabor.cpp',
		'src/libcharm/src/textures/haralick/CVIPtexture.cpp',
		'src/libcharm/src/textures/haralick/haralick.cpp',
		'src/libcharm/src/textures/tamura.cpp',
		'src/libcharm/src/textures/zernike/complex.cpp',
		'src/libcharm/src/textures/zernike/zernike.cpp',
		'src/libcharm/src/transforms/ChebyshevFourier.cpp',
		'src/libcharm/src/transforms/chebyshev.cpp',
		'src/libcharm/src/transforms/radon.cpp',
		'src/libcharm/src/transforms/wavelet/Common.cpp',
		'src/libcharm/src/transforms/wavelet/convolution.cpp',
		'src/libcharm/src/transforms/wavelet/DataGrid2D.cpp',
		'src/libcharm/src/transforms/wavelet/DataGrid3D.cpp',
		'src/libcharm/src/transforms/wavelet/Filter.cpp',
		'src/libcharm/src/transforms/wavelet/FilterSet.cpp',
		'src/libcharm/src/transforms/wavelet/Symlet5.cpp',
		'src/libcharm/src/transforms/wavelet/Wavelet.cpp',
		'src/libcharm/src/transforms/wavelet/WaveletHigh.cpp',
		'src/libcharm/src/transforms/wavelet/WaveletLow.cpp',
		'src/libcharm/src/transforms/wavelet/WaveletMedium.cpp',
		'src/libcharm/src/transforms/wavelet/wt.cpp',
		'src/libcharm/src/cmatrix.cpp',
		'src/libcharm/src/libcharm.cpp',
		'src/libcharm/src/ImageTransforms.cpp',
		'src/libcharm/src/FeatureAlgorithms.cpp',
		'src/libcharm/src/Tasks.cpp',
		'src/libcharm/src/FeatureNames.cpp',
		'src/libcharm/src/gsl/specfunc.cpp',
		'src/libcharm/src/capi.cpp',
	],
	include_dirs=['src/libcharm/','src/libcharm/src/', '/usr/local/include'],
	libraries=['tiff','fftw3'],
)

# sudo apt-get install gcc libpq-dev -y
# sudo apt-get install python-dev  python-pip -y
# sudo apt-get install python3-dev python3-pip python3-venv python3-wheel -y
# pip3 install wheel
setup (
	name = 'CharmFeatures',
	version = __version__,
	author      = "Ilya Goldberg, Nikita Orlov, Josiah Johnston, Lior Shamir, Chris Coletta",
	author_email = "igg <at> iggtec <dot> com",
	url = 'https://gitlab.com/iggman/charm-features',
	description = """Python bindings for charm features from wnd-charm""",
	# N.b.: the module name has to match in CharmFeatures/__init__.py
	ext_modules = [libcharm_module],
	packages = ['CharmFeatures'],
	setup_requires=['wheel'],
	# bitarray is for pylibtiff
	install_requires=['numpy<2', 'scipy', 'tables', 'pylibtiff', 'fasteners', 'bitarray'],
    entry_points = {
        'console_scripts': ['charm-image-features=CharmFeatures.ProcessImages:main'],
    }
)
