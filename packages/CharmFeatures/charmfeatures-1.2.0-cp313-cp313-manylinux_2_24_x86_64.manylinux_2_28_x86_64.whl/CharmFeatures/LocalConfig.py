import os
import tempfile
import numpy as np
from PIL import Image
from CharmFeatures.ProcessImages import RemoteConfig

class LocalConfig(RemoteS3Config):

    def init_worker(self):
        global REMOTE_CONFIG
        print("Executing Local filesystem init_worker")
        REMOTE_CONFIG = LocalConfig(self.bucket_name, self.download_location, self.mode, self.session_profile)
        # print("in RemoteConfigLocal and REMOTE_CONFIG is " + str(REMOTE_CONFIG))

        # Nothing to initialize for local files
        REMOTE_CONFIG.remote_session = None
        print("Local filesystem session initialized")
        
    # This is an override of RemoteConfig.fetch_image. This is making sure the local path exists to convert to an image matrix.
    # Also want to change naming of local_rel_path to path here and in base class. Let's keep everything in the interface the same.
    def fetch_image(self, local_rel_path):
        """
        local_rel_path: terminal filename only (e.g., 'img001.tiff')
        
        The image is first looked for in self.bucket_name (if provided), 
        otherwise in self.download_location.
        """
        filename = os.path.basename(local_rel_path)
    
        # Use bucket_name as an alternative local folder
        search_folders = []
        if self.bucket_name:
            search_folders.append(self.bucket_name)
        search_folders.append(self.download_location)
    
        full_path = None
        for folder in search_folders:
            candidate = os.path.join(folder, filename)
            if os.path.exists(candidate):
                full_path = candidate
                break
    
        if full_path is None:
            print(f"File {filename} not found in bucket_name ({self.bucket_name}) or download_location ({self.download_location})")
            return None
    
        try:
            with Image.open(full_path) as img:
                img_matrix = np.array(img)
            print(f"Loaded image {full_path} with shape {img_matrix.shape}")
            return img_matrix
        except Exception as e:
            print(f"Error reading image {full_path}: {e}")
            return None


    def img_to_feat_path(self, local_rel_path):
        """
        Returns absolute path for storing/accessing features derived from the image
        """
        path = os.path.join(self.download_location, local_rel_path)

        print(f"Resolved local feature path: {path}")
        return path
