# Module definition for the libcharm library wrapper
# Provides simple integration of wndcharm feature computation with for e.g. sklearn.
import os, sys
import importlib
import ctypes

# dependencies
import numpy as np

# internal globals
__version__ = "unknown"
from CharmFeatures._version import __version__
from CharmFeatures._lib_version import __lib_version__
from CharmFeatures._git_hash import __git_hash__
__version__ += '+' + __git_hash__
__lib_version__ += '+' + __git_hash__

# Find the shared library we compiled
# Make use of the fact that extensions are meant to be imported as modules
# Here our extension is just sources for a C++ library and a bare C api.
# Importing it will cause an exception because of the missing PyInit_module entry point.
# so, we ask where the import would have found it instead.
_mod_path = os.path.abspath(os.path.dirname(__file__))
# _libname = 'libcharmtest'
_LIBNAME = 'libcharm'

class CharmFeatures (object):
	""" This class is a numpy interface (via ctypes) to compute wndcharm image features, otherwise known as libcharm.
	The intent is to provide for easy integration with other packages that use numpy for machine learning, for e.g. sklearn.
	Synopsis:
	  from libtiff import TIFF
	  from CharmFeatures import CharmFeatures
	  # Initialize computing of standard long feature vectors (2895 features in version 5)
	  cf = CharmFeatures()
	  # A contiguous 2D array of doubles will avoid copying
	  image = tif.read_image().astype(np.double)
	  # Compute image features, returning a 1D numpy array of 2895 doubles.
	  fv = cf.get_features(image)
	API:
	  An instance of the CharmFeatures class is initialized to compute one of the standard feature vectors,
	  or a custom feature vector by specifying a list of feature algorithms and optional image transforms.
	  Subsequently, the get_features() method is called repeatedly with an image as a 2D numpy array.
	  The get_features() call either places the feature vector in the provided (or newly allocated)
	  1D numpy array.
	"""
	# These are all class-level definitions
	_libname = _LIBNAME
	_lib_search_paths = sys.path + [os.path.dirname(_mod_path)]
	_libspec = importlib.machinery.PathFinder().find_spec(_libname, _lib_search_paths)
	_libpath = _libspec.origin if _libspec else None
	version = __version__
	lib_version = __lib_version__
	# The indexes correspond to the enum in StdFeatureComputationPlans::featurevec_types
	# These are also the minor version of the feature vector.
	std_featurevec_types = [
		'custom',
		'short',
		'long',
		'short_color',
		'long_color',
	]

	# library global settings
	verbosity = os.getenv('WNDCHRM_VERBOSITY', 2)
	forking_executor = os.getenv('WNDCHRM_FORKING_EXECUTOR', True)
	forking_gabor = os.getenv('WNDCHRM_FORKING_GABOR', True)
	forking_haralick = os.getenv('WNDCHRM_FORKING_HARALICK', True)

	# The order for these arrays corresponds to featurevec_types
	std_feature_counts = [None]*len(std_featurevec_types)
	std_feature_names = [[]]*len(std_featurevec_types)

	# Load the shared library
	print ( "loading {} from {}".format(_libname, _libpath) )
	_libcharm = np.ctypeslib.load_library(_libname, _libpath)
	# Define arguments and return types for library calls.
	# Get the library's feature vector version on import
	# get_featurevec_version()
	_libcharm.get_featurevec_version.restype = ctypes.c_uint
	_libcharm.get_featurevec_version.argtypes = []
	featurevec_version = _libcharm.get_featurevec_version()

	# Get the library's global settings on import
	# void get_libparam (int *verbosity, bool *forking_executor, bool *forking_haralick, bool *forking_gabor) {
	_libcharm.get_featurevec_version.restype = None
	_libcharm.get_libparam.argtypes = [
		ctypes.POINTER(ctypes.c_int),
		ctypes.POINTER(ctypes.c_bool),
		ctypes.POINTER(ctypes.c_bool),
		ctypes.POINTER(ctypes.c_bool),
	]
	ct_v, ct_fe, ct_fh, ct_fg  = (ctypes.c_int(), ctypes.c_bool(), ctypes.c_bool(), ctypes.c_bool())
	_libcharm.get_libparam(
		ctypes.byref(ct_v), ctypes.byref(ct_fe), ctypes.byref(ct_fh), ctypes.byref(ct_fg)
	)
	verbosity, forking_executor, forking_haralick, forking_gabor = (
		ct_v.value, ct_fe.value, ct_fh.value, ct_fg.value
	)

	# 
	# test_custom_feature_executor()
	# const FeatureComputationPlanExecutor *test_custom_feature_executor ()
	_libcharm.test_custom_feature_executor.restype = ctypes.c_void_p
	_libcharm.test_custom_feature_executor.argtypes = []

	# std_feature_executor()
	# const FeatureComputationPlan *std_feature_executor (
	# 	const bool color = false, const bool short_features = false)
	_libcharm.std_feature_executor.restype = ctypes.c_void_p
	_libcharm.std_feature_executor.argtypes = [ctypes.c_bool, ctypes.c_bool]

	# custom_features_executor()
	# const FeatureComputationPlan *custom_feature_plan (const char *plan_name,
	# 	const char *feature_names[], size_t n_features)
	_libcharm.custom_features_executor.restype = ctypes.c_void_p
	_libcharm.custom_features_executor.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t]

	# del_executor()
	# void del_executor (FeatureComputationPlanExecutor *executor) {
	_libcharm.del_executor.restype = None
	_libcharm.del_executor.argtypes = [ctypes.c_void_p]

	# get_feature_names()
	# const char **get_feature_names (unsigned int *f_count,
	# 	FeatureComputationPlanExecutor *executor)
	_libcharm.get_feature_names.restype = ctypes.POINTER(ctypes.c_char_p)
	_libcharm.get_feature_names.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.c_void_p]

	# del_feature_names()
	_libcharm.del_feature_names.restype = None
	_libcharm.del_feature_names.argtypes = [ctypes.POINTER(ctypes.c_char_p)]

	# get_features()
	# int get_features (double *vec_ptr, double *mat_ptr,
	#     const unsigned int width, const unsigned int height,
	#     FeatureComputationPlanExecutor *executor)
	_libcharm.get_features.restype = ctypes.c_int
	_libcharm.get_features.argtypes = [
		np.ctypeslib.ndpointer(np.double, ndim=1,
			flags='aligned, contiguous, writeable'),
		np.ctypeslib.ndpointer(np.double, ndim=2,
			flags='aligned, contiguous, writeable'),
		ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,
	]

	# get_error()
	_libcharm.get_error.restype = ctypes.c_char_p
	_libcharm.get_error.argtypes = []

	# The constructor initializes the object to compute a specific feature vector
	def __init__ (self, f_names = [], color=False, short=False,
		forking_executor = True, forking_gabor = True, forking_haralick = True, verbosity = 2
	):
		"""
		Constructor parameters determine the feature execution plan that will be used for processing
		subsequent images.
		Without parameters, the long greyscale feature vector will be computed.
		Parameters:
		  f_names = []: An optional array of feature names (e.g. f_names=['Edge Features ()','Otsu Object Features (Fourier ())'])
		    Used for constructing custom feature vectors using a combination of image transform and feature algorithms.
		    Each algorithm specified will result in 1 or more entries in the feature vector.
		    One of the 4 standard feature vectors will be computed if f_names is not specified.
		    Unrecognized feature name specifications will throw an exception.
		    Available feature name algorithms and transforms can be obtained from:
		      fnames = CharmFeatures().feature_names
		  short=False: If True, compute the standard short feature vector.
		    If short=True, 1047 features for color=False, 2179 for color=True.
		    If short=False, 2895 features for color=False (default), 4027 features for color=True.
		  color=False: If True, compute color features for a 3-plane (RGB) set of 2D arrays.
		    N.B.: color=True is not currently supported.
		  verbosity=2: The verbosity level (0: silent, 1: minimal, 2: normal, etc up to 7 for memory messages)
		  forking_ececutor=True: The executor will perform the computations in parallel
		  forking_gabor=True: The gabor textures computaiton will be done with a parallel algorithm
		  forking_haralick=True: The haralick features will be done with a parallel algorithm
		Attributes:
		  Class:
		    featurevec_version: Major version of the feature algorithms in the library (currently 5)
		      feature vectors computed from the same version are "numerically equivalent" (minimum 5 sig figs)
		    lib_version: libcharm library version
		    version: Wrapper version (i.e. CharmFeatures python, C API, and ctypes version)
		  Object:
		    std_featurevec: int feature vector type for standard feature vectors, 0 for custom.
		    feature_names: Fully expanded list of feature names for the feature vector.
		    n_features: Number of features in the feature vector.
	    """
	    # Object attributes:
		self.executor            = None
		self.std_featurevec      = 0
		self.feature_names       = None
		self.safe_feature_names  = None
		self.n_features          = None
		self.featurevec_version  = None

		# reflect the fact that these are global, and set them
		CharmFeatures.verbosity = verbosity if verbosity is not None else CharmFeatures.verbosity
		CharmFeatures.forking_executor = forking_executor if forking_executor is not None else CharmFeatures.forking_executor
		CharmFeatures.forking_haralick = forking_haralick if forking_haralick is not None else CharmFeatures.forking_haralick
		CharmFeatures.forking_gabor = forking_gabor if forking_gabor is not None else CharmFeatures.forking_gabor
		CharmFeatures._libcharm.set_libparam(CharmFeatures.verbosity,
			CharmFeatures.forking_executor, CharmFeatures.forking_haralick, CharmFeatures.forking_gabor)

		if len(f_names) > 0:
			self.std_featurevec = 0
			c_arr = (ctypes.c_char_p * len(f_names))()
			# C wants a utf-8 encoding of strings.
			# This is valid in python 2 and python 3.
			c_arr[:] = [f.encode('utf-8') for f in f_names]
			self.executor = CharmFeatures._libcharm.custom_features_executor ('custom FV'.encode('utf-8'), c_arr, len(f_names))
			if not self.executor:
				raise ValueError ('CharmFeatures.__init__(): Unable to instantiate executor with provided f_names.:\n  {}'.
					format(self.get_lib_error()))

			# Note that what we provide only the list of algorithms, the list of feature names is expanded
			# to include all of the names for the individual feature values that the algorithms produce
			self.get_feature_names ()

		# One of the standard feature vectors
		else:
			self.executor = CharmFeatures._libcharm.std_feature_executor (color, short)
			self.std_featurevec = self.featurevec_type_idx (color, short)

			self.get_feature_names ()
			# Note that the executor here is ultimately a static, so we do not free it

		# Discover the architecture.
		# There is a known incompatibility (i.e. float inequality) b/w features computed on arm64 vs amd64.
		# This appears limited to features involving Fourier transforms.
		# The incompatibility is typically in the 5th or higher significant figure.
		# Easy fixes have been tried like casting the image to float from double before and/or after the FFT.
		# Solution for now is to flag arm64 features with a new version number to avoid mixing them with amd64.
		arch = self.get_arch()
		if len(arch) > 0:
			arch = '-'+arch
		self.featurevec_version = f'{CharmFeatures.featurevec_version}{arch}.{self.std_featurevec}'

	def get_features (self, ndarray, featurevec = None):
		""" Compute the feature vector for the image, provided as a 2D numpy array of doubles.
		Required parameters:
		  ndarray: a 2D numpy array. If the array is contiguous doubles, it will be used as is,
		    or copied otherwise.
		Optional parameters:
		  featurevec: A 1D numpy array of doubles to be used to store the feature vector result.
		    Can be provided as a slice of a larger feature matrix, for e.g.
		"""
		# int get_features (double *vec_ptr, double *mat_ptr,
		#     const unsigned int width, const unsigned int height,
		#     const bool color = false, const bool short_features = false)

		ndarray = np.require (ndarray, dtype = np.double, requirements = ['C', 'A', 'W'])
		if len (ndarray.shape) < 2:
			raise ValueError("get_features() ndarray less than 2D")
		width, height = ndarray.shape
		if featurevec is None:
			featurevec = np.zeros ( (self.n_features,), dtype = np.double)
		else:
			featurevec = np.require (featurevec, dtype = np.double, requirements = ['C_CONTIGUOUS','ALIGNED','WRITEABLE'])
		if featurevec.shape[0] < self.n_features:
			raise IndexError("featurevec array not large enough for requested features: {} provided {} needed".
				format(featurevec.shape[0], self.n_features))

		nfeatures = CharmFeatures._libcharm.get_features (featurevec, ndarray, width, height, self.executor)

		if nfeatures != self.n_features:
			raise ValueError ("Features calculation failed:{}".format(self.get_lib_error()))
		return (featurevec)

	def get_feature_names (self):
		""" Return the names of the features in the feature vector.
		Note that feature names are expanded to account for feature algorithms computing multiple features.
		For e.g. the "Edge Features ()" algorithm computes 27 features: "Edge Features () [0]",
		"Edge Features () [1]", etc.
		"""
		if not (self.std_featurevec and self.std_feature_counts[self.std_featurevec]):
			f_count_c = ctypes.c_uint(0)
			ret = CharmFeatures._libcharm.get_feature_names (ctypes.byref(f_count_c), self.executor)

			feat_type = ctypes.POINTER(ctypes.c_char_p * f_count_c.value)
			cfeats = ctypes.cast (ret, feat_type)

			pstr_feature_names = [cf.decode('utf-8') for cf in cfeats.contents]
			CharmFeatures._libcharm.del_feature_names (ret)

			self.feature_names = pstr_feature_names
			self.n_features = len(pstr_feature_names)

			if self.std_featurevec:
				CharmFeatures.std_feature_names[self.std_featurevec] = pstr_feature_names
				CharmFeatures.std_feature_counts[self.std_featurevec] = len(pstr_feature_names)
		else:
			self.feature_names = CharmFeatures.std_feature_names[self.std_featurevec]
			self.n_features = len(CharmFeatures.std_feature_names[self.std_featurevec])

		self.safe_feature_names = []
		for fname in self.feature_names:
			fg = fname[:fname.find(' (')].replace(' ','_').replace('-','_')
			trs = fname.split(' (')[1:-1]
			trs = '_x' + '_x'.join(trs) if trs else ''
			idx = fname[fname.find('[') + 1:fname.find(']')]
			self.safe_feature_names.append(fg + trs + '_' + idx.zfill(2))

		return (self.feature_names)

	def get_lib_error (self):
		""" Return the error string from the libcharm library.
		If CharmFeatures throws an exception, it will contian this string in the text.
		"""
		err_buf = ctypes.create_string_buffer(1024)
		CharmFeatures._libcharm.get_error(err_buf, 1024)
		return (err_buf.value.decode('utf-8'))

	def featurevec_type_idx (self, color=False, short=False):
		""" Return an int representing the feature vector type.
		      0: custom feature vectors
		      1: Short=True,  Color=False
		      2: Short=False, Color=False
		      3: Short=True,  Color=True
		      4: Short=False, Color=True
		"""
		if not color and short:
			return (1)
		elif not color and not short:
			return (2)
		elif color and short:
			return (3)
		elif color and not short:
			return (4)

	def get_arch (self):
		import platform, warnings
		arch = str(platform.machine()).lower()
		if arch == "aarch64" or arch == "arm64":
			arch = "arm64"
		elif arch == "x86_64" or arch == "amd64":
			# FIXME: Right now for backwards compatibility, we're leaving the arch off of the version if it's amd64.
			arch = "" # should be "amd64"
		else:
			warnings.warn (f"Python's platform.machine() returned {arch}. Expecting 'x86_64','amd64', 'aarch64' or 'arm64'")
			arch = "unknown"
		return (arch)

	def __del__ (self):
		""" Destructor. Cleans up internal references to libcharm's feature computation plan and executor object.
		"""
		# call del* on all objects allocated in C
		# del_IM
		CharmFeatures._libcharm.del_executor (self.executor)
