from pathlib import Path
from unittest import TestCase

from ratisbona_utils.images import ImageCache
from ratisbona_utils.images.image_encoding import encode_base64_embedded


class TestImageEncode(TestCase):

    url = 'https://www.duh.de/fileadmin/_processed_/f/a/csm_woods_ad5acec37a.png'

    def test_encode_image(self):
        with ImageCache(Path('/tmp/imgcachetest')) as mgr:
            local_file = mgr.get_file_for_url(self.url)
            mgr.download_all()
        result = encode_base64_embedded(local_file.read_bytes())
        self.assertTrue(result.startswith('data:image/png;base64,'))
