from .client_manager import _ClientManager

class _Streamer:
    @staticmethod
    def init(server: str, stream_key: str):
        client = _ClientManager.get_instance().get_client()
        client.set_stream_service_settings(
            'rtmp_custom',
            {
                "server": server,
                "key": stream_key,
                "use_auth": False
            }
        )

    @staticmethod
    def set_stream_key(stream_key: str):
        client = _ClientManager.get_instance().get_client()
        settings = client.get_stream_service_settings()
        settings['key'] = stream_key
        client.set_stream_service_settings('rtmp_custom', settings)    

    @staticmethod
    def start():
        client = _ClientManager.get_instance().get_client()
        client.start_stream()

    @staticmethod
    def stop():
        client = _ClientManager.get_instance().get_client()
        client.stop_stream()
