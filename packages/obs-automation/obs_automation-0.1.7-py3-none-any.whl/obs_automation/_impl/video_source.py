from .client_manager import _ClientManager
class _VideoSource:


    @staticmethod
    def create_media_source(name: str, file_path_or_url: str):
        client = _ClientManager.get_instance().get_client()

        is_url = file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://")

        if is_url:
            # On macOS, VLC plugin is unavailable → USE browser_source for URL playback
            input_kind = "browser_source"
            settings = {
                "url": file_path_or_url,
                "fps": 30,
                "width": 1280,
                "height": 720,
                "shutdown": False
            }
        else:
            # Local file → ffmpeg_source
            input_kind = "ffmpeg_source"
            settings = {
                "local_file": file_path_or_url,
                "looping": True,
                "is_local_file": True,
                "speed_percent": 100,
                "restart_on_activate": True
            }

        client.create_input(
            sceneName="Scene",
            inputName=name,
            inputKind=input_kind,
            inputSettings=settings,
            sceneItemEnabled=True
        )



    @staticmethod
    def set_media(input_name: str, file_path_or_url: str):
        client = _ClientManager.get_instance().get_client()

        # First: detect what type of input this is
        inp = client.get_input_settings(input_name)
        input_kind = inp.input_kind

        is_url = file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://")

        # CASE 1 → browser_source (used when media was a URL during creation)
        if input_kind == "browser_source":
            if not is_url:
                raise Exception("This input is a browser_source but you provided a local file. Use ffmpeg_source for local files.")

            settings = {
                "url": file_path_or_url
            }

        # CASE 2 → ffmpeg_source (local media files)
        elif input_kind == "ffmpeg_source":
            if is_url:
                raise Exception("ffmpeg_source cannot play URL media. Use browser_source for URLs.")

            settings = {
                "local_file": file_path_or_url,
                "looping": True,
                "restart_on_activate": True,
            }

        else:
            raise Exception(f"Unsupported input_kind '{input_kind}' for set_media()")

        client.set_input_settings(
            input_name,
            settings,
            overlay=False
        )



    @staticmethod
    def create_browser_source(name: str, url: str, width: int = 1920, height: int = 1080):
        client = _ClientManager.get_instance().get_client()
        settings = {
            "url": url,
            "width": width,
            "height": height,
            "fps": 30,
            "custom_css": "",
            "shutdown_source_on_scene_switch": False
        }
        client.create_input(
        sceneName="Scene",              # or whatever your scene name is
        inputName=name,
        inputKind="browser_source",     # OBS expects lowercase
        inputSettings=settings,
        sceneItemEnabled=True
        )

    
    @staticmethod
    def set_browser(input_name:str,url: str, width: int = 1920, height: int = 1080):
        client = _ClientManager.get_instance().get_client()
        
        client.set_input_settings(input_name, { "url": url, "width": width,
            "height": height, }, overlay=False)
