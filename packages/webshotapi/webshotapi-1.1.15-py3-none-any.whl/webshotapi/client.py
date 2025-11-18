#  Copyright (c) 2025. WebShotApi All right reserved
from gawsoft.api_client import Request, Response

from .client_exception import WebshotapiClientError
from .types import ScreenshotJsonResponse, ExtractResponse
from .version import __version__
import os

class Client(Request):
    """
    Client for webshotapi server
    """

    _request_timeout = 75

    def __init__(
        self,
        api_key: str = "",
        api_host: str = '',
        user_agent: str = f"Webshotapi Python client {__version__}"
     ):
        if (not api_key or len(api_key)==0) and 'WEBSHOTAPI_KEY' in os.environ:
            api_key = os.environ['WEBSHOTAPI_KEY']

        if (not api_host or len(api_host)==0) and 'WEBSHOTAPI_ENDPOINT' in os.environ:
            api_host = os.environ['WEBSHOTAPI_ENDPOINT']
        elif api_host:
            pass
        else:
            api_host = "https://api.webshotapi.com/v1/"

        super().__init__(api_key, api_host, user_agent)

    def video(self, params:dict) -> Response:
       '''
           Take video of website and return video binary

           :param params:
                dict with parameters check available parameters in https://webshotapi.com/docs/get-started/parameters/
           :return:
                Response object
        Example:
            >>> client = Client()
            >>> client.video({
                "video_format": "mp4"
            })

       '''

       return self.request(f'video/binary','POST', params)

    def video_json(self, params: dict) -> ScreenshotJsonResponse:
        '''
        Take video and return url to video file

        :param params:
             dict with parameters check available parameters in https://webshotapi.com/docs/get-started/parameters/
        :return:
             Response object
        '''

        response = self.request(f'video/json', 'POST', params)
        if response.status_code != 200:
            raise WebshotapiClientError(f"Response return status code: {response.status_code}")

        parsed_data = response.data()

        return ScreenshotJsonResponse(
            url = parsed_data['url'],
            expire_sec = parsed_data['expire_sec']
        )

    def screenshot(self, params:dict) -> Response:
       '''
           Take screenshot and return image

           :param params:
                dict with parameters check available parameters in https://webshotapi.com/docs/get-started/parameters/
           :return:
                Response object
        Example:
            >>> client = Client()
            >>> client.screenshot("https://example.com", {
                "image_type": "webp"
            })

       '''

       return self.request(f'screenshot/binary','POST', params)


    def screenshot_json(self, params: dict) -> ScreenshotJsonResponse:
        '''
        Take screenshot and return url to image

        :param params:
             dict with parameters check available parameters in https://webshotapi.com/docs/get-started/parameters/
        :return:
             Response object
        '''

        response = self.request(f'screenshot/json', 'POST', params)
        if response.status_code != 200:
            raise WebshotapiClientError(f"Response return status code: {response.status_code}")

        parsed_data = response.data()

        return ScreenshotJsonResponse(
            url = parsed_data['url'],
            expire_sec = parsed_data['expire_sec']
        )

    def pdf(self, params:dict) -> Response:
        '''
        Take screenshot and return pdf file

        :param params:
            dict with parameters check available parameters in https://webshotapi.com/docs/get-started/parameters/
        :return:
            Response object
        '''

        params['image_type'] = 'pdf'
        return self.request('screenshot/binary','POST', params)

    def extract(self, params:dict) -> ExtractResponse:
        """
        Extract html selectors with css styles, words with coordinates(x,y,width,height).
        You can also extract html of rendered page and clean text

        @param params: dict with params
            dict with parameters check available parameters in https://webshotapi.com/docs/get-started/parameters/

        @return: ExtractResponse
        """
        response = self.request('extract', 'POST', params)
        if response.status_code != 200:
            raise WebshotapiClientError(f"Response return status code: {response.status_code}")

        parsed_data = response.data()

        return ExtractResponse(
            status_code=parsed_data["status_code"],
            html=parsed_data["html"],
            text=parsed_data["text"],
            elements=parsed_data["elements"],
            words=parsed_data["words"],
            page_properties=parsed_data["page_properties"],
            saved_in_cloud=parsed_data["saved_in_cloud"]
        )

    def info(self) -> dict:
        """
        Get info about your account

        @return: dict
        """
        response = self.request('info', 'GET')
        if response.status_code != 200:
            raise WebshotapiClientError(f"Response return status code: {response.status_code}")

        return response.data()