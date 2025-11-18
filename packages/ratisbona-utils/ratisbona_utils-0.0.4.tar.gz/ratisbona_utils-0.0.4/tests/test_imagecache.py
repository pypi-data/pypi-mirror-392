from pathlib import Path
from unittest import TestCase

from ratisbona_utils.images import ImageCache
from shutil import rmtree

url='https://www.duh.de/fileadmin/_processed_/f/a/csm_woods_ad5acec37a.png'

class TestImageCache(TestCase):

    def test_get_file_for_url_must_yield_path(self):
        path=Path('/tmp/imgcachetest')
        if path.exists():
            #recursively delete directory with content
            rmtree(path)
        with ImageCache(path) as mgr:
            sudopath=mgr.get_file_for_url(url)
        self.assertEqual(sudopath, path / '0')

    def test_downloading_must_fetch_files(self):
        path=Path('/tmp/imgcachetest')
        if path.exists():
            #recursively delete directory with content
            rmtree(path)
        with ImageCache(path) as mgr:
            sudopath=mgr.get_file_for_url(url)
            mgr.download_all()
        self.assertTrue(sudopath.exists())