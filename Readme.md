# YouTube Video/Audio Downloader

This is a Python application for downloading YouTube videos and audio using the `yt_dlp` library. It leverages concurrency with `asyncio` and `ThreadPoolExecutor` for faster downloads.

## Features

- Downloads YouTube videos and audio in MP4 and MP3 formats respectively.
- Provides an interactive console interface for input and output.
- Uses `tqdm` for progress bar visualization.
- Logs download events to a file for debugging and tracking.
- Implements best practices for code structure and organization using SOLID principles.

## Prerequisites

- Python 3.6 or higher
- `yt_dlp` library: `pip install yt_dlp`
- `ffmpeg` is required for audio extraction and video conversion:
  - `sudo apt-get install ffmpeg` (Debian/Ubuntu)
  - `brew install ffmpeg` (macOS)

## Setup and Run

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/youtube-downloader.git

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt

3. Run the application:

   ```bash
   python main.py


Usage
The application will display a menu with two options:

Enter YouTube video URL(s): This option allows you to enter one or more YouTube video URLs, separated by commas or spaces.
Exit: This option exits the application.
Enter YouTube video URLs
After selecting the first option, you will be prompted to enter one or more YouTube video URLs.

Choose media type
You will be asked whether you want to download audio (A) or video (V).

Download process
The application will start downloading the videos or audio files based on your chosen media type. A progress bar will be displayed for each download.

Download results
Once all downloads are complete, a message will be displayed indicating the download time and the number of media files downloaded.

Download more
You can choose to download more videos or audio files by entering 'y' when prompted. Entering 'n' will exit the application.

File Structure
main.py: Main application file.
utils.py: Contains helper functions for common tasks.
downloader.py: Contains the downloader logic.
Customization
Download folder: The downloaded videos and audio files will be saved in the "src" directory within the project folder. You can customize the download path by modifying the video_folder and audio_folder variables in the YTDownloadService class.
Max concurrent downloads: You can adjust the maximum number of concurrent downloads by modifying the max_concurrent_downloads variable in the OptimizedDownloader class.
Contributing
Contributions are welcome! Feel free to submit pull requests, report issues, or suggest new features.

License
This project is licensed under the MIT License. See the LICENSE file for more information.
