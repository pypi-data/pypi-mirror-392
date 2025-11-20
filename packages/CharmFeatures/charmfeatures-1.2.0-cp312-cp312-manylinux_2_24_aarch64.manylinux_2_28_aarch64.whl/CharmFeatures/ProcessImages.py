#!/usr/bin/env python3parser
'''
compute_features - compute features in a directory tree or spreadsheet.
feature files are numpy npz files (numpy.savez()) with a 'sample_name' -> 'feature_vector' structure.
One or more 'tiles' are saved per file. One sampling spec per npz file per image. ROIs, preprocessing, etc in separate files.
Conventional wndchrm command-line flags are interpreted for tile (-t), ROI, subsampling and pixel normalization
'''
### NEED TO tell tiff to supress the error. malformed gps tag on tiff. the tiff library encounters an unrecognized tiff tag ####
### Error: Directory GPSInfo with 18761 entries considered invalid; not read. ###

import sys, os
import argparse
import libtiff
import csv
import numpy as np
from scipy import ndimage as ndi
import fasteners
import multiprocessing

import logging
logger = logging.getLogger(__name__ if __name__ != "__main__" else __file__.replace('.py', ''))

from CharmFeatures import CharmFeatures
import tables

import configparser
import tempfile

REMOTE_CONFIG = None

class RemoteS3Config():
	'''
	A class to define methods and credentials to access images from a remote server.
	Classes for remotes other that AWS S3 are meant to inherit from this class and override the init_worker() and fetch_image() methods.
	This class is initialized once per worker in the parallel workers of a multiprocessing pool using the remote_config dict.

	The remote_config class field will be passed to the internal worker initializer wrapper, which takes this as an argument
	worker_init_wrapper (RC_instance.__class__, RC_instance.remote_config)
	in worker_init_wrapper(), the class will be instantiated (using __init__()) with the remote_config dict
	This allows any inherited class to be initialized in workers using a dict of primitives for easy pickling.
	'''
	remote_config = {
		'bucket_name'        : None,  # just the bucket name
		'public'             : False, # use a public s3 bucket (bc_UNSIGNED)
		'profile'            : None,  # use a named aws profile (usually in ~/.aws/) or 'default'
	}

	def __init__(self, remote_config):
		'''
		The __init()__ method shouldn't need an override, simply provide additional keys/values
		necessary to establish a remote session in init_worker().
		The same session should be reusable by fetch_image() method.
		'''
		# This is a singleton stored in REMOTE_CONFIG
		global REMOTE_CONFIG
		REMOTE_CONFIG = self
		# logger.debug("In RemoteConfig.__init__ and REMOTE_CONFIG is " + str(REMOTE_CONFIG))
		# Copy the passed-in dict to the class one
		for key, value in remote_config.items():
			REMOTE_CONFIG.remote_config[key] = value

		REMOTE_CONFIG.remote_session = None

	def init_worker(self):
		import boto3
		import botocore as bc
		from botocore.config import Config as bc_Config
		from botocore import UNSIGNED as bc_UNSIGNED
		from botocore.exceptions import NoCredentialsError, BotoCoreError
		global REMOTE_CONFIG

		"""
		Initialize an S3 client with one of the following modes:
		- "public"     : If True, public access to S3 buckets without authentication (default is False).
		- "profile"    : If present, use authenticated access with the specified AWS profile or 'default'.
						 If missing use the default aws session configuration.
		# Example usage:
		1. Public
			rc = RemoteS3Config (remote_config = {
				'bucket_name': 'myBucket',
				'public': True
			})
		2. Default AWS profile
			rc = RemoteS3Config (remote_config = {
				'bucket_name': 'myBucket',
			})
		3. Specified AWS profile
			rc = RemoteS3Config (remote_config = {
				'bucket_name': 'myBucket',
				'profile'    : 'myAWSprofile'
			})
		"""
		if REMOTE_CONFIG is None:
			raise NameError ('REMOTE_CONFIG global singleton is not defined in init_worker()')
		if REMOTE_CONFIG.remote_config is None or len(REMOTE_CONFIG.remote_config) == 0:
			raise NameError ('REMOTE_CONFIG global singleton is not configured in init_worker()')
		rc = REMOTE_CONFIG.remote_config
	
		if 'profile' in rc and rc['profile']:
			profile = rc['profile']
		else:
			profile = None
		logger.debug(f"Initializing S3 for PID {os.getpid()} with public: {rc['public']}, profile: {profile}")
	
		if 'public' in rc and rc['public']:
			# Public UNSIGNED access
			REMOTE_CONFIG.remote_session = boto3.client(
				's3',
				config=bc_Config(signature_version=bc_UNSIGNED)
			)
			logger.debug("S3 initialized with UNSIGNED public access")
	
		elif profile:
			# Authenticated access using a specified AWS profile
			logger.debug(f"Initializing S3 with AWS profile: {profile}")
	
			session = boto3.Session(profile_name=profile)
			REMOTE_CONFIG.remote_session = session.client('s3', config=bc_Config(signature_version="s3v4"))
			logger.debug(f"S3 initialized with profile '{profile}'")
	
		else:
			# Authenticated using default AWS credential provider chain (env vars, ~/.aws/credentials, IAM roles)
			logger.debug("Initializing S3 using default AWS credential chain")
	
			REMOTE_CONFIG.remote_session = boto3.client('s3', config=bc_Config(signature_version="s3v4"))
			logger.debug("S3 initialized with default authenticated access")
	
		logger.debug(f"init_worker() remote_session: {REMOTE_CONFIG.remote_session}")
		return REMOTE_CONFIG.remote_session
 
	def fetch_image(self, s3_link):
		global REMOTE_CONFIG
		rc = REMOTE_CONFIG.remote_config
		bucket_name = rc['bucket_name']

		with tempfile.NamedTemporaryFile(suffix='.tiff') as tf:
			temp_tiff_filename = tf.name
	
			logger.debug("tmp tiff file name set", temp_tiff_filename)
		
			# Download image using boto
			logger.debug("bucket name=" + bucket_name)
			logger.debug("s3_link=" + str(s3_link))
			# logger.debug("in fetch_image and REMOTE_CONFIG.remote_session is " + str(REMOTE_CONFIG.remote_session))
			# logger.debug("in fetch_image and REMOTE_CONFIG is " + str(REMOTE_CONFIG))
			try:
				REMOTE_CONFIG.remote_session.download_file(bucket_name, s3_link, temp_tiff_filename)
			except bc.exceptions.BotoCoreError as e:
				logger.debug(f"Error downloading file {s3_link} from S3: {e}")
			except Exception as e:
				logger.debug(f"Unexpected error downloading file {s3_link} from S3: {e}")
	
			try:
				img_mat = ProcessImages.img_to_mat (temp_tiff_filename)
				logger.debug('image shape: ' + str(np.shape(img_mat)))
			except Exception as e:
				logger.debug(f"Error processing image {s3_link}: {e}")
		return img_mat


class ProcessImages (object):
	featurevec_tag = 'charmfeatures_version'

	def __init__(self, 
		ROI           = None,
		subsample     = None,
		normalize     = False,
		tile          = None,
		verbosity     = 1,
		image_links   = None,
		forks_divisor = 4, #this can be set to control the number of forks 
		in_paths      = [],
		outfile       = None,
		cpus          = 0,
		remote_config = None,
		features_root = None, # None: same path as image.
	):
		self.ROI           = ROI
		self.subsample     = subsample
		self.normalize     = normalize
		self.tile          = tile
		self.verbosity     = verbosity
		self.image_links   = image_links
		self.forks_divisor = forks_divisor
		self.in_paths      = [in_paths] if isinstance(in_paths, str) else in_paths
		self.outfile       = outfile
		self.cpus          = cpus
		self.features_root = features_root

		self.nsamples     = 1 # per path
		self.image_paths  = []
		self.sname_sfx    = ''
		self.fv_fname_ext = '.npz'
		self.path_labels  = {}

		self.sample_names = []
		self.features_mat = None
		self.labels       = []
		self.groups       = []

		self.get_sname_sfx()
		self.CharmFeatures = CharmFeatures()

		if self.verbosity > 2:
			logger.setLevel(logging.DEBUG)
		elif self.verbosity:
			logger.setLevel(logging.INFO)
		else:
			logger.setLevel(logging.ERROR)

		if self.verbosity:
			logger.info ('CharmFeatures v{} ({})'.format(self.CharmFeatures.lib_version, self.CharmFeatures.version))

		global REMOTE_CONFIG
		if remote_config:
			# logger.debug("ProcessImages.__init__(): assigning REMOTE_CONFIG=remote_config  ")
			REMOTE_CONFIG = remote_config
		if REMOTE_CONFIG:
			# For remote images, the default for features_root is cwd
			if self.features_root is None:
				self.features_root = ''

		# The REMOTE_CONFIG can be None for local file access
		# assert (REMOTE_CONFIG is not None)
		# if REMOTE_CONFIG.remote_session is None:
			# logger.debug ('REMOTE_CONFIG.remote_session in ProcessImages init is '+str(REMOTE_CONFIG.remote_session))
		if in_paths:
			self.process_paths ()
			self.read_or_compute_features()
		elif image_links:
			self.read_or_compute_features()
		if outfile and in_paths:
			self.write_output()

	def get_chunky_list_size (self, arr, chunksize = 32):
		return (
			( (len(max(arr, key=len)) // chunksize) + 1 ) * chunksize
		)


	def get_sname_sfx (self):
		self.sname_sfx = ''
		if self.ROI:
			self.sname_sfx += '-r{}'.format('_'.join([str(d) for d in self.ROI]))
		if self.subsample:
			if len(self.subsample) == 2 and self.subsample[0] == self.subsample[1]:
				self.subsample = (self.subsample[0],)
			self.sname_sfx += '-s{}'.format('_'.join([format(d, 'G') for d in self.subsample]))
		if self.normalize:
			self.sname_sfx += '-n'
		if self.tile and len(self.tile) in (1,2):
			if len(self.tile) == 1 and self.tile[0] == 1:
				self.tile = None
			elif len(self.tile) == 2 and self.tile[0] == self.tile[1]:
				if self.tile[0] == 1:
					self.tile = None
				else:
					self.tile = (self.tile[0],)
		elif self.tile is not None:
			raise ValueError ('The tile parameter must be either None or length 1 or 2')
		if self.tile:
				self.nsamples = self.tile[0]**2 if len(self.tile) == 1 else self.tile[0] * self.tile[1]
				if self.verbosity > 4:
					logger.debug ('tile: {}, nsamples: {}'.format(self.tile, self.nsamples))
				self.sname_sfx += '-t{}'.format('x'.join([str(d) for d in self.tile]))          
		else:
				self.nsamples = 1

		return (self.sname_sfx)


	def parse_args(self, in_args = None):
		parser = argparse.ArgumentParser(description='Calculate charm features for tiff files.')
		parser.add_argument('-t', '--tile', metavar='str', type=str,
			help='tile with specified # tiles in rows and columns, or "R,C" for rows and columns')
		parser.add_argument("-n", "--normalize", action="store_true",
			help="normalize per-image pixel values to 1 std, i.e. convert to per-image z-scores")
		parser.add_argument("-s", "--subsample", metavar = 'zoomX[,zoomY]', type=str,
			help="subsample; shrink < 1.0, expand > 1.0")
		parser.add_argument("-r", "--ROI", metavar = 'UL_x,UL_y,LR_x,LR_y', type=str,
			help="ROI; Specify comma-separated X,Y coordinates for upper-left and lower-right")
		parser.add_argument("-o", "--outfile", metavar = 'filename', type=str,
			help="specify a '.npz' output file. This will contain 'samples' (list of sample names), "
			"'features' (matrix of feature vectors) and 'labels' (list of label names) numpy arrays")
		parser.add_argument("-f", "--features-root", metavar = 'features_root', type=str,
			help="specify a root path for outputting feature files instead of using the same path as the image files. "
			"The directory structure in this path will mirror the directory structure of the image file paths.")
		parser.add_argument("-c", "--cpus", metavar = 'cpus', type=int, default=0,
			help="specify number of CPUs to use in parallel. Default is all available.")
		parser.add_argument("--S3-bucket", metavar = 'S3_bucket', type=str,
			help="specify an AWS S3 bucket name for paths.")
		parser.add_argument("--S3-public", metavar = 'S3_public', type=bool, default=False,
			help="specify if the AWS S3 bucket is public. If False (default) the aws cli config settings will be used.")
		parser.add_argument('paths', nargs='+', type=str,
			help="Specify one or more paths to compute features on. "
				"Directory paths will be descended recursively in alphabetical order. A single .tsv or .csv path "
				"will be interpreted as a spreadsheet with image paths in the 1st or paths column")


		parser.add_argument("-v", "--verbosity", type=int, choices=[a for a in range(9)], default=self.verbosity,
			help="increase output verbosity")
		args = parser.parse_args(args=in_args)

		self.verbosity = args.verbosity
		if self.verbosity > 2:
			logger.setLevel(logging.DEBUG)
		elif self.verbosity:
			logger.setLevel(logging.INFO)
		else:
			logger.setLevel(logging.ERROR)
		if self.verbosity > 2:
			logger.debug ('verbosity: {}'.format(self.verbosity))

		if self.verbosity:
			logger.info ('CharmFeatures v{} ({})'.format(self.CharmFeatures.lib_version, self.CharmFeatures.version))

		if args.ROI:
			ROI = str(args.ROI).split(',')
			if len(ROI) != 4:
				parser.print_help()
				logger.critical ('Expected 4 comma-separated integers for ROI, got "{}"'.format(args.ROI), file=sys.stderr)
				parser.exit()
			try:
				ROI = tuple(int(d) for d in ROI)
			except ValueError:
				parser.print_help()
				logger.critical ('Expected 4 comma-separated integers for ROI, got "{}"'.format(args.ROI), file=sys.stderr)
				parser.exit()
			self.ROI = ROI
			if self.verbosity > 2:
				logger.info ('ROI: {}'.format(self.ROI))

		if args.subsample:
			try:
				subs = tuple(float(d) for d in str(args.subsample).split(','))
			except ValueError:
				parser.print_help()
				logger.critical ('Expected 2 comma-separated numbers for subsample, got "{}"'.format(args.subsample), file=sys.stderr)
				parser.exit()
			if len(subs) not in (1,2):
				parser.print_help()
				logger.critical ('Expected 2 comma-separated numbers for subsample, got "{}"'.format(args.subsample), file=sys.stderr)
				parser.exit()
			if len(subs) == 2 and subs[0] == subs[1]:
				subs = (subs[0],)
			self.subsample = subs
			if self.verbosity > 2:
				logger.info ('subsample: {}'.format(self.subsample))

		if args.normalize:
			self.normalize = args.normalize
			if self.verbosity > 2:
				logger.info ('normalize: {}'.format(self.normalize))

		if args.tile:
			try:
				tile = tuple(int(d) for d in str(args.tile).split(','))
			except ValueError:
				parser.print_help()
				logger.critical ('Expected 1 or 2 comma-separated integers for tiling, got "{}"'.format(args.tile), file=sys.stderr)
				parser.exit()
			if len(tile) not in (1,2):
				parser.print_help()
				logger.critical ('Expected 1 or 2 comma-separated integers for tiling, got "{}"'.format(args.tile), file=sys.stderr)
				parser.exit()
			self.tile = tile
			if self.verbosity > 2:
				logger.info ('tile: {}'.format(self.tile))

		if args.outfile:
			self.outfile = args.outfile
			if self.verbosity > 2:
				logger.info ('outfile: {}'.format(self.outfile))

		if args.features_root:
			self.features_root = args.features_root
			if self.verbosity > 2:
				logger.info ('features_root: {}'.format(self.features_root))

		if args.cpus:
			self.cpus = args.cpus
			if self.verbosity > 2:
				logger.info ('CPUs: {}'.format(self.cpus))

		if args.S3_bucket:
			remote_config = {
				'bucket_name' : args.S3_bucket,
			}
			if args.S3_public:
				remote_config['public'] = True
			if args.features_root:
				self.features_root = args.features_root
			else:
				# the default for remote images is to store features in cwd
				self.features_root = ''

			rc = RemoteS3Config(remote_config = remote_config)
			if self.verbosity > 2:
				logger.info (f"S3_bucket: "
					"{REMOTE_CONFIG.remote_config['bucket_name']}, "
					"public: {REMOTE_CONFIG.remote_config['public']')"
				)

		if args.paths:
			self.in_paths = list(args.paths)
			if self.verbosity > 2:
				logger.info ('paths: {}'.format(self.in_paths))

		self.sname_sfx = self.get_sname_sfx()
		if self.verbosity > 2:
			logger.info ('feature file name suffix: {}'.format(self.sname_sfx + self.fv_fname_ext))

		return (self)

	@classmethod
	def img_to_mat (cls, img_path):
		libtiff.libtiff_ctypes.suppress_warnings()
		tif = libtiff.TIFF.open (img_path)
		# convert to doubles
		img_mat = tif.read_image().astype(np.double)
		if tif.GetField('Photometric') == 2:
			# These are used in matlab, wnd-charm, etc.
			img_mat = np.dot(img_mat[...,:3], [0.2990, 0.5870, 0.1140])
			# These are used by skimage.color.rgb2gray
			# img_mat = np.dot(img_mat[...,:3], [0.2125, 0.7154, 0.0721])
		elif len(img_mat.shape) > 2:
			img_mat = img_mat[...,0]

		return (img_mat)


	def compute_features (self, img_path, fv_file):
		global REMOTE_CONFIG
		if REMOTE_CONFIG:
			img_mat = REMOTE_CONFIG.fetch_image(img_path)
		else: 
			img_mat = self.img_to_mat (img_path)
		img_mean = img_mat.mean()
		img_std = img_mat.std()
		img_name = os.path.splitext ( os.path.basename(img_path) )[0]
		fv_sample_name = img_name + self.sname_sfx
		if self.verbosity > 5:
			logger.debug ('fv_sample_name: {}'.format (fv_sample_name))

		if self.ROI:
			img_mat = img_mat[self.ROI[1]:self.ROI[3]+1, self.ROI[0]:self.ROI[2]+1]

		if self.subsample:
			subsample = self.subsample[0] if len (self.subsample) == 1 else self.subsample
			img_mat = ndi.zoom(img_mat, subsample, mode='constant', cval=img_mean)

		if self.normalize:
			# z-scores:
			#     z = (x - u) / s
			img_mat = (img_mat - img_mean) / img_std
			img_mean = img_mat.mean()
			img_std = img_mat.std()

		tiles = self.tile if self.tile is not None else (1,1)
		tiles = tiles if len(tiles) == 2 else (tiles[0],tiles[0])
		tile_fmt = '-t{:0'+str(len(str(tiles[0])))+'d}_{:0'+str(len(str(tiles[1])))+'d}'
		# N.B.: floor division here ensures that we will have exactly the number of full tiles specified,
		# with potentially a tile - 1 pixel remainder
		if self.verbosity > 2:
			logger.debug ('computing {}: shape: {}  tiles: {}'.format(img_path, img_mat.shape, tiles))
		tile_sz_r = img_mat.shape[0] // tiles[0]
		tile_sz_c = img_mat.shape[1] // tiles[1]

		cf = self.CharmFeatures
		fvs = {}
		for tile_idx_r in range (tiles[0]):
			for tile_idx_c in range (tiles[1]):
				row_strt, row_stop = tile_idx_r*tile_sz_r, (tile_idx_r+1)*tile_sz_r
				col_strt, col_stop = tile_idx_c*tile_sz_c, (tile_idx_c+1)*tile_sz_c
				tile_mat = img_mat[row_strt:row_stop, col_strt:col_stop]
				fv_name = fv_sample_name + (tile_fmt.format(tile_idx_r, tile_idx_c) if self.tile else '')
				if self.verbosity > 5:
					logger.debug (f'tile {fv_name} = img[{row_strt}:{row_stop}, {col_strt}:{col_stop}]')
				fvs[fv_name] = cf.get_features(tile_mat).astype(np.float32)

		fvs[ProcessImages.featurevec_tag] = self.CharmFeatures.featurevec_version
		np.savez (fv_file,**fvs)
		return (fvs)

	def check_npz (self, npz):
		if not all ([len(npz[k]) == self.CharmFeatures.n_features for k in npz.keys() if k != ProcessImages.featurevec_tag]):
			logger.error ("number of features doesn't match expected: {}".format (self.CharmFeatures.n_features))
			return (False)
		if not npz[ProcessImages.featurevec_tag] == self.CharmFeatures.featurevec_version:
			logger.error ("charm feature vector version in file ({}) doesn't match expected: {}".format (
				npz[ProcessImages.featurevec_tag], self.CharmFeatures.n_features)
			)
			return (False)
		return (True)

	def ex_open (self, npz_fname, check_npz = True):
		'''Opens npz_fname for either shared reading or exclusive writing. Returns npz and lock (either or both can be None).
		The npz feature-vector file is the lockfile.
		'''
		ntries = 3
		rdwr_lock = None
		npz = None
		npz_file = None
		while ntries > 0 and npz is None and rdwr_lock is None:
			npz = None
			rdwr_lock = fasteners.InterProcessReaderWriterLock (npz_fname)
			# if the file exists, try to get a read lock
			if os.path.exists (npz_fname) and os.path.getsize (npz_fname) > 2 and rdwr_lock.acquire_read_lock(blocking = False):
				# open the file ourselves to make sure numpy doesn't close it (which will release locks).
				# We can't use rd_lock.lockfile (a file-like object) because it is open non-binary, and np.load() assumes binary.
				if check_npz: 
					with open (npz_fname, 'rb') as npz_file:
						npz = {}
						with np.load(npz_file) as data:
							for key, fv in data.items():
								npz[key] = fv
						rdwr_lock.release_read_lock()
					npz_file = rdwr_lock = None
					if self.verbosity > 4:
						logger.debug ('readlock: npz {}, len(npz) {}, nsamples {}'.format (npz, len(npz) if npz else 'N/A',self.nsamples))
					if npz is None or not self.check_npz (npz):
						if (self.verbosity > 4):
							logger.debug ('deleting '+npz_fname)
						os.remove(npz_fname)
						npz = None
					else:
						del npz[ProcessImages.featurevec_tag]

			# file doesn't exist or read lock failed: try to get a write lock
			elif rdwr_lock.acquire_write_lock(blocking = False):
				if (self.verbosity > 4):
					logger.debug ('write lock '+npz_fname)
				pass

			# Can't get a read or write lock, so try the sequence again a limited number of times
			else:
				ntries -= 1
				rdwr_lock = None
				npz = rdwr_lock = None
				if (self.verbosity > 5):
					logger.debug ('re-trying {}, ntries={}'.format(npz_fname, ntries))

		return (npz, rdwr_lock)

	@classmethod
	def is_image_path (cls, img_path):
		'''
		This method should only depend on things in the path string.
		Potentially, it could be moved to the Remote*Config classes to do something fancier.
		'''
		ext = os.path.splitext (img_path)[1].lower()
		if ext in ['.tiff', '.tif']:
			return (True)
		return (False)

	@classmethod
	def strip_leading_parents (cls, img_path):
		components = os.path.normpath(img_path).split(os.sep)
		# Filter out leading '..' components
		skip_count = 0
		for comp in components:
			if comp == '..':
				skip_count += 1
			else:
				break

		return os.sep.join(components[skip_count:])

	def image_path_to_fv_path (self, img_path):
		fv_path = os.path.splitext (img_path)[0] + self.get_sname_sfx() + self.fv_fname_ext
		if self.features_root is not None:
			fv_path = self.strip_leading_parents (fv_path)
			fv_path = os.path.join (self.features_root, fv_path)
		return (fv_path)

	# not used.
	def image_path_has_fv (self, img_path):
		fv_path = self.image_path_to_fv_path (img_path)
		if os.path.isfile (fv_path) and os.path.getsize(img_path) > 2:
			return (True)
		return (False)


	def read_or_compute_fv (self, img_path):
		#Add optional parameter where fv_fname folder is externally set 
		fv_fname = self.image_path_to_fv_path (img_path)
		if self.verbosity:
			logger.info ('reading or computing features for {}: {}'.format(img_path, fv_fname))

		fv, wr_lock = self.ex_open (fv_fname)
		if wr_lock:
			if self.verbosity > 4:
				logger.debug ('computing features for {}'.format(img_path))
			# If we close any open file descriptor for this file, we lose the lock.
			# So, we give numpy already open file-lock objects so it doesn't close them itself.
			# we need a binary file-like object for numpy, so we can't just use the already open lockfile.
			with open (fv_fname, 'wb') as fv_file:
				fv = self.compute_features (img_path, fv_file)
				fv_file.flush()
				os.fsync(fv_file.fileno())
				wr_lock.release_write_lock()

		return (fv)

	def get_feature_matrix (self):
		# make sure nsamples is correct, and other attributes set
		self.get_sname_sfx()
		self.features_mat = np.zeros ( ( len(self.image_paths) * self.nsamples, self.CharmFeatures.n_features ), dtype=np.float32 )
		# determine length of string arrays

		sample_names = []
		labels = []
		groups = []
		group_dict = {}

		for idx, path in enumerate(self.image_paths):
			sample_num = idx * self.nsamples
			for sample, fv in self.read_or_compute_fv (path).items():
				if sample == ProcessImages.featurevec_tag:
					continue
				if self.verbosity > 5:
					logger.debug ('sample, sample_num: {}, {}'.format (sample, sample_num))
				sample_names.append(sample)
				self.features_mat[sample_num] = fv
				sample_num += 1

			labels += [self.path_labels[path]] * self.nsamples
			if path not in group_dict:
				group_dict[path] = len (group_dict)
			groups += [group_dict[path]] * self.nsamples

		# vstack will work correctly by
		# expanding string size to accomodate larger strings as necessary
		self.sample_names = np.array(sample_names)
		self.labels       = np.array(labels)
		self.groups       = np.array(groups, dtype='uint16')

		return (self.sample_names, self.features_mat, self.labels, self.groups)

	def read_or_compute_features (self, nprocs = None):
		global REMOTE_CONFIG
		if not nprocs and not self.cpus:
			nprocs = len(os.sched_getaffinity(0)) // self.forks_divisor
			if nprocs < 1: nprocs = 1
		elif self.cpus:
			nprocs = self.cpus

		logger.info('Creating pool with %d processes\n' % nprocs)

		tasks = [(self.ROI, self.subsample, self.normalize, self.tile, self.verbosity, path) for path in self.image_paths]

		#If you are given a different set of path ids, set tasks to those 
		if self.image_links: 
			tasks = [(self.ROI, self.subsample, self.normalize, self.tile, self.verbosity, path) for path in self.image_links]
		if REMOTE_CONFIG:
			initargs = [REMOTE_CONFIG.__class__, REMOTE_CONFIG.remote_config]
		else:
			initargs = [None, None]
		with multiprocessing.Pool(nprocs, initializer = init_worker_wrapper, initargs = initargs) as pool:
			logger.debug("tasks = " + str(tasks))
			res = pool.map_async(calc_one_fv_star, tasks).get()
		if not all(res):
			if self.image_paths: 
				badres = [self.image_paths[i] for i,r in enumerate(res) if not r]
			if self.image_links: 
				badres = [self.image_links[i] for i,r in enumerate(res) if not r]
			logger.error ('Features could not be computed for the following files:\n'+'  '+'\n  '.join(badres))
		else:
			self.get_feature_matrix()
		return (res)

	def process_spreadsheet (self, fname, relpath=None):
		ext = os.path.splitext (fname)[1].lower()
		if ext not in ['.csv', '.tsv']:
			return (None)

		# make sure nsamples is correct, and other attributes set
		self.get_sname_sfx()
		# keep the paths relative to maintain compatibility with remote paths
		# relpath = os.getcwd() if relpath is None else relpath
		relpath = '' if relpath is None else relpath

		if self.verbosity > 2:
			logger.info ('processing {} as spreadsheet. Rel path: {}'.format(fname, relpath))
		with open(fname) as fd:
			if ext == '.tsv':
				rd = csv.reader(fd, delimiter="\t")
			else:
				rd = csv.reader(fd)
			firstrow = True
			pathcol = labelcol = None
			for row in rd:
				if self.verbosity > 4:
					logger.debug ('  {}'.format(row))
				if row[0].startswith ('#'):
					continue
				if firstrow:
					rowpath = os.path.join(relpath, row[0])
					if self.verbosity > 4:
						logger.debug ('    isfile({}): {}, ext: {}'.format(rowpath, os.path.isfile(rowpath), os.path.splitext (rowpath)[1].lower()))
					if self.is_image_path(rowpath):
						pathcol = 0
						if len(row) > 1:
							labelcol = 1
					else:
						for idx, colname in enumerate (row):
							if colname.lower() in ['path', 'paths', 'file', 'files', 'file names', 'file paths']:
								pathcol = idx
							if colname.lower() in ['class', 'label']:
								labelcol = idx
					if pathcol is None:
						raise ValueError ('Expected the first column to be paths to files, or a column named "paths" or "files"')
					firstrow = False

				rowpath = os.path.join(relpath, row[pathcol])
				if self.is_image_path (rowpath):
					if self.verbosity > 3:
						logger.debug ('adding image file {}'.format(rowpath))
					self.image_paths.append(rowpath)
					self.path_labels[rowpath] = row[labelcol] if labelcol is not None else None
		return (True)

	def process_paths (self, paths = [], filters = [], labels = {}):
		# make sure nsamples is correct, and other attributes set
		self.get_sname_sfx()
		# some flexibility for specifying filters and patterns as singletons
		for lab,pat in labels.items():
			labels[lab] = [pat] if isinstance (pat, str) else pat
		filters = [filters] if isinstance (filters, str) else filters
		paths = [paths] if isinstance (paths, str) else paths

		for path in self.in_paths if not paths else paths:
			path = os.path.normpath(path)
			if self.verbosity > 2:
				logger.debug ('processing path {}'.format(path))
			if os.path.isdir(path):
				for dirpath, dirnames, files in os.walk(path, followlinks = True):
					dirnames.sort()
					dirname = os.path.basename (dirpath)
					if self.verbosity > 4:
						logger.debug ('processing path {}'.format(dirname))
					for fname in sorted(files):
						path = os.path.join(dirpath, fname)
						# for e in [l] if isinstance(l, str) else l
						if self.is_image_path (path) and all ([f not in path for f in filters]):
							self.image_paths.append(path)
							label = None
							for lab,pat in labels.items():
								if any ([p in path for p in pat]):
									self.labels[path] = lab
									break
							if path not in self.path_labels:
								self.path_labels[path] = dirname
							if self.verbosity > 3:
								logger.debug ('image path {}: {}'.format(path,self.path_labels[path]))
			elif os.path.isfile(path):
				if self.process_spreadsheet (path) is None and self.is_image_path (path):
					self.image_paths.append(path)
					self.path_labels[path] = os.path.basename (os.path.dirname(path))
			# FIXME: process paths on the commandline which are on the remote
			elif REMOTE_CONFIG and self.is_image_path (path):
				if self.image_links is None:
					self.image_links = []
				self.image_links.append(path)
				self.path_labels[path] = os.path.basename (os.path.dirname(path))



	def write_output (self, outfile=None):
		if not outfile and not self.outfile:
			return None
		outfile = self.outfile if not outfile else outfile
		if ( not (len (self.sample_names) == len(self.features_mat) ==
				len(self.labels) == len(self.groups) == len(self.image_paths)*self.nsamples)
		):
			raise ValueError ('The number of samples ({}), feature vectors ({}), labels ({}) and groups ({}) '+
				'does not match number of images ({}) * samples per image ({}) = {}'.format(
					len(self.sample_names), len(self.features_mat), len(self.labels), len(self.groups),
					len(self.image_paths), self.nsamples, len(self.image_paths) * self.nsamples
				))
		if not len (self.features_mat > 0):
			logger.info ('Not recreating an empty outfile "{}" with no samples.'.format(outfile))
			return

		chrm_vers = self.CharmFeatures.featurevec_version

		# open the file for exclusive creation
		# read all of the features in
		npz, wr_lock = self.ex_open(outfile, check_npz = False)
		if wr_lock is None and npz is None:
			raise ValueError ('Could not open file "{}"" for writing.'.format (outfile))
		elif wr_lock is None and ( len (npz) != 3 or not all ([x in npz for x in ['samples', 'features', 'labels', 'groups']]) ):
			raise ValueError ('Expected three arrays in existing output file {}'.format(outfile))
		elif wr_lock is None and not (len(npz['samples']) == len(npz['features']) ==
			len(npz['labels']) == len(npz['groups']) == len(self.image_paths)*self.nsamples
		):
			raise ValueError ('The number of samples ({}), features ({}), labels ({}), and groups ({}) '
				'in the existing output file does not match number of images ({}) * samples per image ({}) = {}'.format(
					len(npz['samples']), len(npz['features']), len(npz['labels']), len(npz['groups']),
					len(self.image_paths), self.nsamples, len(self.image_paths) * self.nsamples
				))
		elif npz:
			logger.info ('Not recreating existing outfile "{}" with expected number of samples ({}).'.format(outfile, len(npz['samples'])))
			return

		if wr_lock and outfile.endswith('.npz'):
			if self.verbosity > 4:
				logger.debug ('writing {}'.format(outfile))
			mat_file = open (outfile, 'wb')
			npz_dict = {
				'samples'  : self.sample_names,
				'features' : self.features_mat,
				'labels'   : self.labels,
				'groups'   : self.groups,
				ProcessImages.featurevec_tag : chrm_vers
			}
			np.savez (mat_file, **npz_dict)

			mat_file.flush()
			os.fsync(mat_file.fileno())
			wr_lock.release_write_lock()
			mat_file.close()

		elif wr_lock and outfile.endswith(('.hdf5','.h5','.hdf')):
			# This declaration may be a surprise at this point in the program, but
			# we don't know the sizes of the string columns until we get here
			class FeatureTableHD5 (tables.IsDescription):
				samples   = tables.StringCol(self.get_chunky_list_size(self.sample_names))
				features  = tables.Float32Col(self.CharmFeatures.n_features)
				labels    = tables.StringCol(self.get_chunky_list_size(self.labels))
				groups    = tables.UInt16Col()

			wr_lock.release_write_lock()
			with tables.open_file(outfile, mode='a', title='Image Features from CharmFeatures v'+chrm_vers) as h5f:
				try:
					table = h5f.create_table('/', 'features', FeatureTableHD5, title='CharmFeatures v'+chrm_vers)
					row = table.row
					if self.verbosity > 4:
						logger.debug ('writing {} samples to hdf5 {}'.format(len(self.sample_names), outfile))
					for idx in range(len(self.sample_names)):
						row['samples']  = self.sample_names[idx]
						row['features'] = self.features_mat[idx]
						row['labels']   = self.labels[idx]
						row['groups']   = self.groups[idx]
						row.append()
					h5f.flush()
					os.fsync(h5f.fileno())
				except tables.exceptions.NodeError:
					table = h5f.get_node ('/features')
					if table.title.endswith (chrm_vers) and len(table) == len(self.sample_names):
						logger.info ('Not recreating existing outfile "{}" with expected number of samples ({}) and CharmFeatures version ({}).'.
							format(outfile, len(table), chrm_vers)
						)
					else:
						raise ValueError ('The number of samples ({}) and CharmFeatures vector version ({}) must match expected: ({}, {}) '
							.format(len(table), table.title.partition(" v")[-1], len(self.sample_names), chrm_vers)
						)
		elif wr_lock:
			raise ValueError ('Unrecognized file format requested "{}"'.format (outfile))
		else:
			raise ValueError ('Could not obtain write lock on "{}"'.format (outfile))

		return (self)


# for parallel processing, self-contained, minimal params, minimal return functions
# one that gets a param tuple, and one with regular params
def calc_one_fv_star (args):
	return (calc_one_fv (*args))

def calc_one_fv(ROI, subsample, normalize, tile, verbosity, path):
	global REMOTE_CONFIG
	logger.debug (f'in calc_one_fv(PID={os.getpid()}), REMOTE_CONFIG = {REMOTE_CONFIG}')
	if REMOTE_CONFIG and REMOTE_CONFIG.remote_session is None:
		# logger.debug ('in calc_one_fv, calling REMOTE_CONFIG.init_worker()')
		REMOTE_CONFIG.init_worker()
	# logger.debug("Checking what remote_session is " + str(REMOTE_CONFIG.remote_session))
	pi = ProcessImages(ROI, subsample, normalize, tile, verbosity)
	fv = pi.read_or_compute_fv(path)
	return fv is not None

def init_worker_wrapper (remote_cls, remote_config):
	"""
	This function runs once in each worker process to initialize the session.
	"""
	global REMOTE_CONFIG
	logger.debug (f'in init_worker_wrapper global REMOTE_CONFIG is {REMOTE_CONFIG}')
	if remote_config is None:
		logger.debug (f'in init_worker_wrapper initializing REMOTE_CONFIG to None')
		REMOTE_CONFIG = None
	else:
		logger.debug (f'initializing global REMOTE_CONFIG to {remote_cls} with {remote_config}')
		REMOTE_CONFIG = remote_cls (remote_config = remote_config)


def hdf5_features_to_npz_hash (h5_file, table_path = '/features', features_column='features',
		labels_column='labels', sample_names_column='samples', groups_column='groups'
	):
	'''Chunked read of feature data from an hdf5 file, return a {samples, features, labels, groups} dict.'''

	with tables.open_file(h5_file) as h5:
		table = h5.get_node (table_path)
		readnum   = 0
		row_start = 0
		chunksize = 4096
		rows_left = table.nrows
		nptable = None

		labels_len = table.coldtypes[labels_column].itemsize
		samples_len = table.coldtypes[sample_names_column].itemsize
		features = np.zeros((len(table),table.coldtypes[features_column].shape[0]), dtype='float32')
		labels = np.zeros((len(table),), dtype=f'U{labels_len}')
		samples = np.zeros((len(table),), dtype=f'U{samples_len}')
		groups = np.zeros((len(table),), dtype='int32')
		while rows_left > 0:
			row_stop = row_start + min(chunksize, rows_left)
			intable = table.read(start=row_start, stop=row_stop)
			logger.debug (f'reading rows {row_start}-{row_stop}')
			row_stop = row_start + len(intable)
			features[row_start:row_stop,:] = intable[features_column][0:,]
			labels  [row_start:row_stop]   = intable[labels_column]
			samples [row_start:row_stop]   = intable[sample_names_column]
			groups  [row_start:row_stop]   = intable[groups_column]

			row_start = row_stop
			rows_left = table.nrows - row_start
			readnum  += 1
		h5.close()
	npz = {
		'samples'  : samples,
		'features' : features,
		'labels'   : labels,
		'groups'   : groups,
	}
	return (npz)


# console_scripts entry_point from setup.py
def main():
	logger.addHandler(logging.StreamHandler(sys.stdout))
	pi = ProcessImages()
	pi.parse_args ()
	pi.process_paths ()
	pi.read_or_compute_features()
	pi.write_output()

# can also run python -m CharmFeatures.ProcessImages or using the module path explicitly
if __name__ == "__main__":
	main()