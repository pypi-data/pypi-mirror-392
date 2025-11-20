# CharmFeatures
CharmFeatures is a ctypes library, module and command-line utility for extracting [Wnd-Charm image features](https://gitlab.com/iggman/wnd-charm) from large collections of TIFF files. It can compute any subset of the full feature set, or new combinations of transforms and feature algorithms.

#### Dependencies
* libtiff: `sudo apt-get install libtiff-dev`
* fftw3: `sudo apt-get install libfftw3-dev`

#### N.B.: See note below on arm64 vs amd64 compatibnility

# charm-image-features
Command-line utility based on `CharmFeatures.ProcessImages` for extracting charm features from large collections of tiff files and saving intermediates for later re-use.

This utility will consume all CPU resources available on the machine it is launched on. It does not use or benefit from GPUs. It can be launched multiple times on different machines on a cluster sharing the same file system in order to cooperatively compute large feature sets on a common directory tree of tiff files. This cooperative distributed multiprocessing requires POSIX-style file locking (sometimes called fcntl-style file locking).

### Synopsis
```shell
charm-image-features -t4 -n -o test-t4.npz ../images
```
Recursively descend the `../images` directory tree, calculating features for 4x4 tiles (`-t4`) of every TIFF file encountered,
using directory names of tiff files as labels. Images are normalized to STDs (i.e. z-scores) prior to tiling (`-n`). Intermediate feature vectors are saved in numpy "npz" format alongside tiff files with sample names
as keys (file/tile names) and feature vectors as values. The entire set of samples is assembled into the outfile `test-t4.npz` (`-o`) with `samples`, `features` and `labels` keys and values containing the sample name vector, feature matrix and label vector.

See `charm-image-features -h` for additional options.

# ProcessImages
ProcessImages is a module designed for ease of integration between wnd-charm features and other AI/ML libraries (e.g. [scikit-learn](https://scikit-learn.org/)) for feature normalization, selection, classifier or regressor training, etc. Please note that 2895 features are computed per image sample in the current version, so a good feature selection strategy is paramount.

### Scikit-learn integration example
```python
from CharmFeatures import ProcessImages as pi

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.feature_selection import SelectKBest, mutual_info_classif

# Gather image features. Feature vectors will not be recomputed in subsequent calls with same parameters
ip = pi.ProcessImages(normalize=True, tile= (4,4), in_paths='images/', outfile='image-features-t4.npz')
# Conventional naming for feature matrix and label vector
X, y, grp = ip.features_mat, ip.labels, ip.groups

# Split dataset into test and train sets, stratified by images to avoid
# having any image exist in both training and test sets.
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=grp)

clf_selected = make_pipeline(
        SelectKBest(mutual_info_classif, k=150), MinMaxScaler(),
        RandomForestClassifier(max_depth=25, n_estimators=75)
)
clf_selected.fit(X_train, y_train)
print('Classification accuracy: {:.3f}'.format(clf_selected.score(X_test, y_test)))
```

### Other options

Separate calls for more control over processing. The constructor will not compute features automatically if no paths are specified.
```python
from CharmFeatures import ProcessImages as pi
ip = pi.ProcessImages(normalize=True, tile= (4,4))
```
The `process_paths()` method can be used to filter out files or assign labels based on things other than directory names.
```python
ip.process_paths (paths = ['../images/cond1','../images/cntrl','../images/cond2'], filters = ['_ch01'], labels = {'cntrl': ['cond1','cntrl'],'trtmnt':'cond2'})
```
Here two separate directories are traversed, any file containing `_ch01` anywhere in its name or path is ignored. Files containing `cond1` or `cntrl` anywhere in their name or path are assigned the `cntrl` label, and those containing `cond2`, the `trtmnt` label.

`process_paths()` can be called multiple times to accumulate files to process.

The sample name vector, feature matrix, label vector and group vector have to be gotten explicitly after `process_paths()`:
```python
(sn, X, y, gr) = ip.get_feature_matrix()
```
If necessary, the features will be computed in parallel in this call, using all available processors. Or, if feature vector files with the same parameters have been computed previously, they will be used instead.


# CharmFeatures
Python ctypes interface to [wnd-charm image features](https://gitlab.com/iggman/wnd-charm) image features.

### Synopsis:
``` python
from libtiff import TIFF
from CharmFeatures import CharmFeatures
import numpy as np
# Initialize computing of standard long feature vectors (2895 features in version 5)
cf = CharmFeatures()
# A contiguous 2D array of doubles will avoid copying
image = TIFF.open('foo.tiff').read_image().astype(np.double)
# Compute image features, returning a 1D numpy array of 2895 doubles.
fv = cf.get_features(image)
feature_names = cf.get_feature_names ()
```

## Notes
- `feature_names` are the fully expanded names of the features returned by the get_features() call.
With few exceptions, each feature extraction algorithm produces multiple features in the vector, all following
the '<feature_name> [d]' convention, where 'd' is an integer from 0-n.
- `get_features()` can be supplied with a slice of a pre-allocated feature matrix using the `featurevec` parameter.
- The `get_features()` method is meant to be called repeatedly on the same `cf` object with different images for efficiently computing features for many images.
### Optional `CharmFeatures()` parameters
- `f_names` can be used to specify a subset of feature extraction algorithms and transforms to run (all features produced by the specified algorithm+transform will be computed).
    ```python
    cf = CharmFeatures (f_names=['Tamura Textures ()', 'Tamura Textures (Fourier (Edge ()))'])
    ```
    This will compute only Tamura Textures on the raw image and on a Fourier transform of an Edge transform of the raw image. The full set of default feature algorithms and transforms can be obtained from CharmFeatures().get_feature_names(). The list of strings supplied to f_names can be any combination of feature algorithms and transforms.

- `forking_executor`, `forking_gabor`, and `forking_haralick` control forking (all `true` by default)
- `short` parameter will produce a 1047-long feature vector if true
- `verbosity` controls the amount of output written, from 0 to 7; default=2.

# Docker
A `Dockerfile` and `compose.yml` is provided for portability and ease of deployment. The image produced (`charmfeatures`) does not specify an entry point, so the conatiner must be run with the charm-image-features command specified explicitly:

```shell
docker compose run -v /data/images:/data/images charmfeatures charm-image-features -n -t4 /data/images
```
This mounts the local folder `/data/images` inside the `charmfeatures` container and then uses the `charm-image-features` command to compute features for all of the image files found in there with normalization and 4x4 tiling.


# Compatibility b/w arm64 and amd64
The features produced on arm64 architecture are not all bit-wise identical to those produced on amd64. For a fraction of the image tiles, a minority of the features (~1%) are identical to 4 significant figures, and a larger minority (~10%) is identical to 5 significant figures, while the majority (~90%) are bit-wise identical. The differing features involve those that use Fourier transforms. It is not believed that the differences will cause significant (or even observable) differences in AI performance as long as all of the features are computed on the same architecture. Because of the occasional differences, the feature vector version now contains '-arm64' when computed on arm architecture. Features computed on amd64 do not reflect this in the version string to maintain backward compatibility.


# Remote image access

CharmFeatures supports flexible configuration classes to manage how images are retrieved and how `.npy` feature files are stored.  
All remote access classes share the same API: `init_worker()`, and `fetch_image()`.

## RemoteS3Config (Remote access to AWS S3)
Used to connect to an AWS S3 bucket to fetch images and save derived features.
Authentication using the user's AWS configuration & profiles or unauthenticated public S3 bucket access is possible.
By default, feature files will be saved in a local directory tree mirroring the remote image directory tree. The root of this
directory tree is  the current working directory unless specified by the `-f` cli flag or `features_root` parameter to ProcessImages.

```python
from CharmFeatures import ProcessImages as pi

# S3 paths to images
image_links = ['pub/example_image1.tiff','pub/example_image2.tiff']
# AWS S3 access settings.
# NB: specifying aws_access_key_id/aws_secret_access_key not currently implemented
remote_config = {
    'bucket_name' : 'myBucket',       # AWS S3 bucket name
    # public s3 buckets can be used by setting 'public' : True
    # if the profile is not specified, then the default profile will be used
    'profile' : 'myAWSProfile'        # usually in ~/.aws/config
}
rc = pi.RemoteS3Config(remote_config = remote_config)
ip = pi.ProcessImages(normalize=True, tile=(4,4), image_links=image_links, remote_config=rc)
```

## Your own remote API

Your own API access can be implemented by inheriting from `RemoteS3Config`.
This example uses a remote API based on a hypothetical `FooSession` from the `MyRemoteAPI` package.

Here, the hypothetical session object has a `fetch_blob_as_numpy()` method, but any type of blob/image fetching
is possible including the use of local temporary file storage (as is done by `RemoteS3Config`).
The `init_worker()` method is called internally once per parallelized worker in a worker poool to establish
a remote session using settings in the `remote_config` dict, and store the resulting session object
in the `remote_session` field. The `fetch_image()`, method is then called once per image, reusing the `remote_session` object.
```python
from CharmFeatures import ProcessImages as pi
from MyRemoteAPI import FooSession # Note this doesn't actually exist
import numpy as np
# inherit from RemoteS3Config
class RemoteFooConfig (pi.RemoteS3Config):
    # The super().__init__() method just copies the provided configuration dict
    # to the class remote_config field. No need to override it normally.
    # The remote_config dict must be picklable, so it should just contain
    # simple strings to initiate the session.
    def init_worker (self):
        # initiate a session using values stored in the remote_config dict
        self.remote_session = FooSession (self.remote_config['foo_profile'])
        return (self.remote_session)
    def fetch_image (self, path):
        # The numpy matrix returned should be a 2D matrix of doubles
        img_mat = self.remote_session.fetch_blob_as_numpy (path, np_type = np.double)
        return (img_mat)
# initialize the parameters necessary to establish a remote session
rc = RemoteFooConfig(remote_config = {'foo_profile' : 'myProfileName'})
ip = pi.ProcessImages(normalize=True, tile=(4,4), image_links=image_links, remote_config=rc)
```

