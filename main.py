import os
import logging
import yt_dlp
import asyncio
import shutil
import platform

from concurrent.futures import ThreadPoolExecutor
from tqdm.asyncio import tqdm


# Color class to handle colored output
class Colors:
    RED = "\033[91m"  # Red text for errors
    GREEN = "\033[92m"  # Green text for success
    YELLOW = "\033[93m"  # Yellow text for warnings
    CYAN = "\033[96m"  # Cyan text for information
    ENDC = "\033[0m"  # Reset text color


# Abstract class/interface for download services (SRP, DIP)
class IDownloadService:
    async def download(self, url: str, is_audio: bool):
        pass


# Concrete implementation of the download service using yt_dlp (SRP)
class YTDownloadService(IDownloadService):
    def __init__(self):
        # Check if ffmpeg is installed
        if not shutil.which("ffmpeg"):
            logging.error("ffmpeg is not installed. Please install ffmpeg to proceed.")
            raise RuntimeError("FFmpeg is required but not installed.")

    def create_folder_if_not_exists(self, path: str):
        """Ensure the folder exists, create if not."""
        if not os.path.exists(path):
            os.makedirs(path)

    async def download(self, url: str, is_audio: bool):
        # Define base path for the app directory
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Define output paths for video and audio
        video_folder = os.path.join(base_dir, "src", "video")
        audio_folder = os.path.join(base_dir, "src", "audio")

        # Ensure the respective folders exist
        self.create_folder_if_not_exists(video_folder)
        self.create_folder_if_not_exists(audio_folder)

        # Set the download folder based on whether it's audio or video
        download_folder = audio_folder if is_audio else video_folder

        ydl_opts = {
            "format": (
                "bestaudio/best"
                if is_audio
                else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
            ),
            "postprocessors": (
                [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
                if is_audio
                else [
                    {
                        "key": "FFmpegVideoConvertor",
                        "preferedformat": "mp4",
                    }
                ]
            ),
            # Save file in the specified folder
            "outtmpl": os.path.join(download_folder, "%(title)s.%(ext)s"),
            "concurrent_fragment_downloads": 5,
            "http_chunk_size": 10485760,
            "nocheckcertificate": True,
            "http_headers": {"User-Agent": "Mozilla/5.0"},
        }

        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await loop.run_in_executor(None, ydl.download, [url])


# Class for managing user input/output (SRP)
class ConsoleUI:
    def display_menu(self):
        print(f"\n{Colors.CYAN}{'='*50}{Colors.ENDC}")
        print(f"\t{Colors.CYAN}YouTube Video/Audio Downloader{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}")
        print("1. Enter YouTube video URL(s)")
        print("2. Exit")
        print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}")

    def get_user_choice(self):
        return input(f"{Colors.YELLOW}Choose an option (1/2): {Colors.ENDC}")

    def get_urls(self):
        urls_input = input(
            f"\n{Colors.GREEN}Enter YouTube video URL(s), separated by commas or spaces: {Colors.ENDC}"
        )
        return [url.strip() for url in urls_input.replace(",", " ").split()]

    def get_media_type(self):
        return input(
            f"\n{Colors.CYAN}Do you want to download audio (A) or video (V)? {Colors.ENDC}"
        ).lower()

    def display_message(self, message: str, color: str = Colors.ENDC):
        print(f"{color}{message}{Colors.ENDC}")


# Logger class (SRP)
class Logger:
    @staticmethod
    def setup_logger():
        # Define base path for the app directory
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Ensure the Logs directory exists within the app folder
        log_dir = os.path.join(base_dir, "Logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Setup logging to file and console
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(os.path.join(log_dir, "downloader.log")),
                logging.StreamHandler(),
            ],
        )

    @staticmethod
    def log_info(message):
        logging.info(message)

    @staticmethod
    def log_warning(message):
        logging.warning(message)

    @staticmethod
    def log_error(message):
        logging.error(message)


# Downloader class that coordinates downloading with multiple URLs (SRP)
class OptimizedDownloader:
    def __init__(
        self, download_service: IDownloadService, max_concurrent_downloads: int = 3
    ):
        """
        Initialize the downloader with a download service.
        """
        self.download_service = download_service
        self.max_concurrent_downloads = max_concurrent_downloads
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_downloads)

    async def download_multiple(self, urls: list, is_audio: bool = False):
        """
        Download multiple YouTube videos or audio.
        """
        tasks = [self.download_service.download(url, is_audio) for url in urls]
        for f in tqdm(
            asyncio.as_completed(tasks), total=len(tasks), desc="Downloading"
        ):
            await f


# Application class to orchestrate the downloader (SRP)
class YouTubeDownloaderApp:
    def __init__(self, downloader: OptimizedDownloader, ui: ConsoleUI, logger: Logger):
        self.downloader = downloader
        self.ui = ui
        self.logger = logger

    async def run(self):
        while True:
            self.ui.display_menu()
            choice = self.ui.get_user_choice()

            if choice == "1":
                urls = self.ui.get_urls()

                if not urls:
                    self.ui.display_message("No URLs entered!", Colors.RED)
                    self.logger.log_warning("No URLs were entered.")
                    continue

                media_type = self.ui.get_media_type()
                is_audio = media_type == "a"

                self.ui.display_message("Downloading...", Colors.YELLOW)
                start_time = asyncio.get_event_loop().time()
                await self.downloader.download_multiple(urls, is_audio)
                end_time = asyncio.get_event_loop().time()

                self.ui.display_message(
                    f"Downloaded {len(urls)} media in {end_time - start_time:.2f} seconds!",
                    Colors.GREEN,
                )
                self.logger.log_info(
                    f"Downloaded {len(urls)} media in {end_time - start_time:.2f} seconds."
                )

                more_urls = input(
                    f"\n{Colors.YELLOW}Do you want to download more? (y/n): {Colors.ENDC}"
                ).lower()
                if more_urls == "n":
                    break
            elif choice == "2":
                self.ui.display_message("Goodbye!", Colors.CYAN)
                break
            else:
                self.ui.display_message(
                    "Invalid choice. Please select 1 or 2.", Colors.RED
                )
                self.logger.log_warning("Invalid choice selected.")


# Main entry point for running the app
if __name__ == "__main__":
    Logger.setup_logger()
    download_service = YTDownloadService()
    ui = ConsoleUI()
    logger = Logger()
    downloader = OptimizedDownloader(download_service)

    app = YouTubeDownloaderApp(downloader, ui, logger)
    asyncio.run(app.run())
