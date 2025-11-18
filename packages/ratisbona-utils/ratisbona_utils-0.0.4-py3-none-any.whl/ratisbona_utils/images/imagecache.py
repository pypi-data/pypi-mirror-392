
# coding: utf-8
import os
import urllib.request
import json
from pathlib import Path


class ImageCache:
    """
        This class is a simple image cache that stores images locally.
        It is intended to be used as a context manager. So use it like this:

            ``` python
            with ImageCache(Path('/tmp/imgcachetest')) as mgr:
                local_file=mgr.get_file_for_url(url)
                mgr.download_all()
            ```

        The `local_file` will contain the local path to the image.

    """
    
    def __init__(self, dirname: Path):
        """
            Constructor.
        Args:
            dirname: The directory where the images are stored.
        """
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        self.jsoncontent = {}
        self.dirname = dirname
        self.indexfile = self.get_local_file_by_count('index.json')
        if os.path.exists(self.indexfile):
            with open(self.indexfile, 'r') as file:
                self.jsoncontent = json.loads(file.read())
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        with open(self.indexfile, 'w') as file:
            file.write(json.dumps(self.jsoncontent, indent=2))
    
    def add_url(self, url) -> Path:
        """
            Adds a URL to the cache.
        Args:
            url: The URL to add.

        Returns:
            The local path to the image.
        """
        countval = self.jsoncontent.get('counter',-1)+1
        self.jsoncontent.update({'counter': countval})
        name_map = self.jsoncontent.get('nameMap',{})
        name_map.update({url: countval})
        self.jsoncontent.update({'nameMap': name_map})
        return self.get_local_file_by_count(str(countval))
        
    def get_file_for_url(self, url) -> Path:
        """
            Gets the local file for a URL, if downloading was successful.
            If download was not successful, the file will not exist.
            It might turn up later, if you call `download_all` again, because it will retry failed downloads.
        Args:
            url: The URL to get the local file for.

        Returns:
            The local path to the image.
        """
        nameMap = self.jsoncontent.get('nameMap',{})
        if url in nameMap:
            return self.get_local_file_by_count(nameMap.get(url))
        return self.add_url(url)
    
    def get_local_file_by_count(self, count) -> Path:
        return self.dirname / str(count)
    
    def download_all(self, retry_failed=False):
        """
            Downloads all images that are not yet downloaded.
        Args:
            retry_failed: False by default. If true, failed downloads will be retried.

        Returns:
            Nothing
        """
        name_map = self.jsoncontent.get('nameMap', {})
        download_map = self.jsoncontent.get('downloadMap',{})
        total = len(name_map)
        count = 0
        for url,countval in name_map.items():
            if url is None: continue
            map_entry = download_map.get(url, None)
            print(
                'Considering {} Mapentry: {} ({}/{})'.format(
                    url, map_entry, count, total
                )
            )
            if map_entry is None or map_entry == 'FAILED' and retry_failed:
                filename = self.get_local_file_by_count(str(countval))
                if os.path.exists(filename):
                    download_map.update({url: 'OK'})
                else:
                    try:
                        #print("Downloading: " + url)
                        urllib.request.urlretrieve(url, filename)
                        download_map.update({url: 'OK'})
                    except Exception as e:
                        download_map.update({url: 'FAILED'})
            self.jsoncontent.update({'downloadMap': download_map})
            count += 1
        

      
        
        
