from ._impl.client_manager import _ClientManager
from ._impl.streamer import _Streamer
from ._impl.video_source import _VideoSource

class ObsController:
    """Public interface for OBS automation"""

    @staticmethod
    def configure_connection(host: str = "localhost", port: int = 4455, password: str = "LocoTeam", timeout: int = 3):
        """
        Configure OBS WebSocket connection before initialization.
        Example:
            ObsController.configure_connection(host="192.168.1.10", password="secret")
        """
        manager = _ClientManager.get_instance()
        manager.configure(host=host, port=port, password=password, timeout=timeout)

    @staticmethod
    def init(server: str, stream_key: str):
        """Initialize OBS stream configuration"""
        _Streamer.init(server, stream_key)

    @staticmethod
    def set_stream_key(stream_key: str):
        """Set the stream key for the stream"""
        _Streamer.set_stream_key(stream_key)

    @staticmethod
    def create_media_source(name: str, file_path_or_url: str):
        """Create a media source in OBS"""
        _VideoSource.create_media_source(name, file_path_or_url)    

    @staticmethod
    def set_video_source_media(input_name:str,file_path_or_url: str):
        """Set video source as local file or URL"""
        _VideoSource.set_media(input_name,file_path_or_url)

    @staticmethod
    def create_browser_source(name: str, url: str, width: int = 1920, height: int = 1080):
        """Create a browser source in OBS"""
        _VideoSource.create_browser_source(name, url, width, height)      

    @staticmethod
    def set_video_source_browser(input_name:str,url: str,width: int = 1920, height: int = 1080):
        """Set video source as browser source"""
        _VideoSource.set_browser(input_name,url, width, height)

    @staticmethod
    def start():
        """Start the stream"""
        _Streamer.start()

    @staticmethod
    def stop():
        """Stop the stream"""
        _Streamer.stop()
