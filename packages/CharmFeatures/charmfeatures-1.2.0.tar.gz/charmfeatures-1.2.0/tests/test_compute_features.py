import os
import tables
import numpy as np
from CharmFeatures import CharmFeatures
from CharmFeatures import ProcessImages as pi

class TestFeatures():
	def _get_arch_testfile (self, outfile):
		testfile = os.path.join(self.testfiles_dir, os.path.splitext(outfile)[0]+self.arch+os.path.splitext(outfile)[1])
		return (testfile)

	def setup_method (self):
		self.module_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
		self.testfiles_dir = os.path.join(self.module_dir,'tests','files')
		self.testimages_dir = os.path.join(self.module_dir,'tests','images')
		self.extra_files = []
		self.arch = CharmFeatures().get_arch()
		if len(self.arch) > 0:
			self.arch = '-'+self.arch
		else:
			self.arch = ''

	def teardown_method (self):
		# re-creating the test files after commenting out the unlink calls below
		# mv image-features-n.h5 tests/files/
		# mv image-features-n.npz tests/files/
		# mv ./tests/images/binuc/binuc1-n-t2.npz ./tests/files/binuc1-n-t2.npz
		# mv tests/images/binuc/binuc1-n-t3x5.npz tests/files/

		for root, dirs, files in os.walk(self.testimages_dir):
			for file in files:
				if file.endswith ('.npz'):
					f_path = os.path.join (root,file)
					os.unlink (f_path)
		for file in self.extra_files:
			os.unlink (file)


	def test_directory_walk (self):
		outfile = 'image-features-n.h5'
		self.extra_files.append(outfile)
		testfile = self._get_arch_testfile (outfile)

		ip = pi.ProcessImages(normalize=True, tile= (1,1), in_paths=self.testimages_dir, outfile=outfile)
		with tables.open_file(outfile, mode='r') as h5f:
			table_out = h5f.get_node ('/features').read()
		with tables.open_file(testfile, mode='r') as h5f:
			table = h5f.get_node ('/features').read()
		assert all (table == table_out)

	def test_spreadsheet (self):
		outfile = 'image-features-n.h5'
		self.extra_files.append(outfile)
		testfile = self._get_arch_testfile (outfile)

		in_file = os.path.join (self.testfiles_dir, 'test_spreadsheet.tsv')
		ip = pi.ProcessImages(normalize=True, tile= (1,1), outfile=outfile, verbosity=5)
		ip.process_spreadsheet (in_file, relpath='tests/images')
		ip.read_or_compute_features()
		ip.write_output ()
		with tables.open_file(outfile, mode='r') as h5f:
			table_out = h5f.get_node ('/features').read()
		with tables.open_file(testfile, mode='r') as h5f:
			table = h5f.get_node ('/features').read()
		assert all (table == table_out)

	def test_npz (self):
		outfile = 'image-features-n.npz'
		self.extra_files.append(outfile)
		testfile = self._get_arch_testfile (outfile)

		ip = pi.ProcessImages(normalize=True, tile= (1,1), in_paths=self.testimages_dir, outfile=outfile)
		npz_out = np.load(outfile)
		npz = np.load(testfile)
		for key, fv in npz.items():
			assert np.array_equal(npz[key], npz_out[key], equal_nan = (key == 'Features'))

	def test_tiling (self):
		testimage = os.path.join(self.testimages_dir, 'binuc', 'binuc1.tiff')
		outfile = 'binuc1-n-t3x5.npz'
		outfile_path = os.path.join(self.testimages_dir, 'binuc', outfile)
		testfile = self._get_arch_testfile (outfile)
		ip = pi.ProcessImages(normalize=True, tile= (3,5), in_paths=testimage)
		npz_out = np.load(outfile_path)
		npz = np.load(testfile)
		for key, fv in npz.items():
			assert np.array_equal(npz[key], npz_out[key], equal_nan = (key == 'Features'))

		outfile = 'binuc1-n-t2.npz'
		outfile_path = os.path.join(self.testimages_dir, 'binuc', outfile)
		testfile = self._get_arch_testfile (outfile)
		ip = pi.ProcessImages(normalize=True, tile= (2,2), in_paths=testimage)
		npz_out = np.load(outfile_path)
		npz = np.load(testfile)
		for key, fv in npz.items():
			assert np.array_equal(npz[key], npz_out[key], equal_nan = (key == 'Features'))

if __name__ == '__main__':
    unittest.main()
