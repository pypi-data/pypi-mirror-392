import io
import json
from typing import Dict, Optional, Any

from .exception import ApiException


class Response(io.IOBase):

    _headers: Dict[str, str]
    _status_code: int

    def __init__(self, resp):
        '''
        Create RestResponse object

        :param resp:
            response object from urllib3
        '''

        self.response = resp
        self._status_code = resp.status_code
        self.reason = resp.reason
        self._headers = {}
        for k in resp.headers:
            self._headers[str(k).lower()] = str(resp.headers[k])

        try:
            self._data = json.loads(resp.content.decode('utf-8'))
        except ValueError:
            self._data = resp.content

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def headers(self) -> Dict[str, str]:
        """Returns a dictionary of the response headers."""
        return self._headers

    def is_json(self) -> bool:
        '''
        Check that response data is json document

        :rtype:
            bool
        '''
        ct = self.header('content-type')
        if ct is None:
            return False

        return 'application/json' in ct

    def header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        '''
        Returns a given response header.
        
        :param name:
            Header name
        :param default:
            Set default value if header not exists
        :rtype:
            string
        '''
        if name not in self._headers:
            return default

        return self._headers[name]

    def data(self) -> Any:
        '''
        Return data downloaded from api
        
        :return:
            return data from api
        '''

        return self._data

    def save(self, path: str) -> str:
        '''
        Save response data to file.
        If you set file path without extension method will auto detect output file extension from mime type.
        Example you take screenshot and want to save to jpg.
        Set path to:
        1. /tmp/example_1_file_name -> will detect extension from mime type and save file to /tmp/example_1_file_name.jpg
        2. /tmp/example_2_file_name.jpg -> extension is in file path so dont detect extension from mime and save to /tmp/example_2_file_name.jpg

        :param path:
            string file path
        :return:
            return saved file path
        :rtype:
            string saved full file path
        '''

        #find extension
        ext = None
        dirs = path.split('/')
        if len(dirs) > 0:
            ext_s = dirs[-1].split('.')
            if len(ext_s) > 1:
                ext = ext_s[-1]

        add_extension = False
        if not ext or len(ext) == 0:
            content_type = self.header('content-type')
            if content_type is not None:
                if 'jpeg' in content_type:
                    ext = 'jpg'
                elif 'png' in content_type:
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'
                elif 'pdf' in content_type:
                    ext = 'pdf'
                elif 'json' in content_type:
                    ext = 'json'
                elif 'webp' in content_type:
                    ext = 'webp'
                elif 'webm' in content_type:
                    ext = 'webm'
                elif 'mp4' in content_type:
                    ext = 'mp4'
                elif 'avi' in content_type:
                    ext = 'avi'

            if ext is not None and len(ext) > 0:
                add_extension = True

        save_path = path
        if add_extension and ext is not None:
            save_path = path + '.' +ext

        if ext not in ['json']:
            f = open(save_path, 'wb')
            f.write(self._data)
            f.close()
        else:
            json.dump(self._data, open(save_path,'w'))

        return save_path
