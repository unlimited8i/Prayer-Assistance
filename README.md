# 🕌 Prayer Assistance Application

A computer vision-based prayer tracking application that uses pose detection to help Muslims track their daily prayers (Salah) with automatic counting of Rakah and Sajdah.

## ✨ Features

- **Automatic Prayer Times**: Fetches accurate prayer times based on your location
- **Pose Detection**: Uses MediaPipe to track prayer movements and count Rakah/Sajdah
- **Prayer Logging**: Maintains detailed Excel logs of prayer performance
- **Missed Prayer Tracking**: Identifies missed prayers
- **Manual Override**: Option to manually mark prayers as completed when camera is unavailable
- **Cross-Platform**: Works on macOS, Windows, and Linux

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam/Camera access
- Internet connection (for prayer times)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Prayer_Assistance
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

### Camera Permissions

#### macOS
1. Go to **System Preferences** > **Security & Privacy** > **Camera**
2. Check the box next to **Terminal** (or **Python**) to allow camera access
3. Restart your terminal

#### Windows
- Windows should prompt for camera access automatically
- If not, go to **Settings** > **Privacy** > **Camera** and enable access for your terminal/Python

#### Linux
- Ensure your user is in the `video` group: `sudo usermod -a -G video $USER`
- Log out and log back in

## 📋 How It Works

1. **Prayer Time Fetching**: The app fetches prayer times from Aladhan API based on your location (Kuwait by default)
2. **Daily Initialization**: Creates daily prayer entries in Excel format
3. **Pose Detection**: Uses MediaPipe to detect body landmarks and track prayer movements
4. **Movement Counting**: 
   - **Rakah**: Counts standing to sitting movements
   - **Sajdah**: Counts prostration movements
5. **Status Tracking**: Updates prayer status (Finished/Not Finished) with timestamps

## 🎯 Prayer Requirements

| Prayer | Rakah | Sajdah |
|--------|-------|--------|
| Fajr   | 2     | 4      |
| Dhuhr  | 4     | 8      |
| Asr    | 4     | 8      |
| Maghrib| 3     | 6      |
| Isha   | 4     | 8      |

## 📁 Project Structure

```
Prayer_Assistance/
├── main.py              # Main application file
├── PoseModule.py        # Pose detection module
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── prayer_log1.xlsx    # Prayer tracking log (auto-generated)
```

## ⚙️ Configuration

### Location Settings
Edit the coordinates in `main.py`:
```python
LAT, LNG = 29.3117, 47.4818  # Change to your location
```

### File Settings
```python
FILE_NAME = 'prayer_log1.xlsx'  # Change log file name if needed
```

## 🔧 Troubleshooting

### Camera Issues
- **"Camera access denied"**: Grant camera permissions to your terminal/Python
- **"Failed to grab frame"**: Check if camera is being used by another application
- **Manual completion**: Use the manual completion option when camera is unavailable

### Dependencies Issues
```bash
# If you encounter import errors, reinstall dependencies:
pip install --upgrade -r requirements.txt
```

### Prayer Times Issues
- Check your internet connection
- Verify your location coordinates are correct
- The app uses Aladhan API (method 2 - Islamic Society of North America)

## 📊 Data Logging

The application creates detailed logs in Excel format with:
- Date and day of the week
- Prayer name and scheduled time
- Actual performed time
- Status (Finished/Not Finished)
- Notes (including makeup prayer information)
- Relative day labels (Today, 1 Day Ago, etc.)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Aladhan API](https://aladhan.com/) for prayer times

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Ensure all dependencies are properly installed

---
