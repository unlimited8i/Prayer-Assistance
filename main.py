import cv2
import numpy as np
import time
import pandas as pd
from datetime import datetime, timedelta
import requests
import PoseModule as pm
import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = ['cv2', 'numpy', 'pandas', 'requests', 'mediapipe']
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'cv2':
                import cv2
            elif module == 'numpy':
                import numpy
            elif module == 'pandas':
                import pandas
            elif module == 'requests':
                import requests
            elif module == 'mediapipe':
                import mediapipe
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Missing required dependencies:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\nPlease install missing dependencies using:")
        print("pip install opencv-python numpy pandas requests mediapipe openpyxl")
        return False
    
    print("✅ All dependencies are installed.")
    return True

LAT, LNG = 29.3117, 47.4818  # kuwait
FILE_NAME = 'prayer_log1.xlsx'

prayers = {
    "Fajr": {"rakah": 2, "sajdah": 4},
    "Dhuhr": {"rakah": 4, "sajdah": 8},
    "Asr": {"rakah": 4, "sajdah": 8},
    "Maghrib": {"rakah": 3, "sajdah": 6},
    "Isha": {"rakah": 4, "sajdah": 8}
}

def get_prayer_times():
    today = datetime.now().strftime("%d-%m-%Y")
    url = f"http://api.aladhan.com/v1/timings/{today}?latitude={LAT}&longitude={LNG}&method=2"
    response = requests.get(url)
    data = response.json()
    times = data['data']['timings']
    return {
        "Fajr": times["Fajr"][:5],
        "Dhuhr": times["Dhuhr"][:5],
        "Asr": times["Asr"][:5],
        "Maghrib": times["Maghrib"][:5],
        "Isha": times["Isha"][:5]
    }

def update_relative_day(file_name=FILE_NAME):
    try:
        df = pd.read_excel(file_name)
        today = datetime.now().date()
        df['Relative Day'] = df['Date'].apply(lambda d: _relative_day_label(datetime.strptime(str(d), "%Y-%m-%d").date(), today))
        df.to_excel(file_name, index=False)
        print("Updated 'Relative Day' column.")
    except FileNotFoundError:
        print("No existing file found for updating relative days.")

def _relative_day_label(date, today):
    delta = (today - date).days
    if delta == 0:
        return "Today"
    elif delta == 1:
        return "1 Day Ago"
    else:
        return f"{delta} Days Ago"

def initialize_daily_prayers(scheduled_times, file_name=FILE_NAME):
    update_relative_day(file_name)
    today_date = datetime.now().strftime("%Y-%m-%d")
    if check_already_initialized(today_date, file_name):
        print("Today's prayers are already initialized.")
        return

    day_name = datetime.now().strftime("%A")

    data = {
        'Date': [], 'Day': [], 'Prayer': [], 'Scheduled Time': [],
        'Performed Time': [], 'Status': [],  'Notes': [], 'Relative Day': []
    }

    for prayer, time in scheduled_times.items():
        data['Date'].append(today_date)
        data['Day'].append(day_name)
        data['Prayer'].append(prayer)
        data['Scheduled Time'].append(time)
        data['Performed Time'].append("")
        data['Status'].append("Not Finished")
        data['Notes'].append("")
        data['Relative Day'].append("Today")

    df = pd.DataFrame(data)

    try:
        existing_df = pd.read_excel(file_name)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        updated_df = df

    updated_df.to_excel(file_name, index=False)
    print(f"Initialized daily prayer log for {today_date}.")

def check_already_initialized(today, file_name):
    try:
        df = pd.read_excel(file_name)
        return today in df['Date'].astype(str).values
    except:
        return False

def get_current_prayer(scheduled_times):
    now = datetime.now().strftime("%H:%M")
    current = None
    for prayer in list(prayers.keys())[::-1]:  # Check latest first
        if now >= scheduled_times[prayer]:
            current = prayer
            break
    return current

def get_pending_prayers(prayer_name, file_name=FILE_NAME):
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        df = pd.read_excel(file_name)
        today_df = df[df['Date'] == today]
        prayer_list = list(prayers.keys())
        idx = prayer_list.index(prayer_name)
        earlier = prayer_list[:idx]
        pending = today_df[(today_df['Prayer'].isin(earlier)) & (today_df['Status'] == 'Not Finished')]
        return list(pending['Prayer'])
    except FileNotFoundError:
        return []

def update_prayer_status(prayer_name, scheduled_times, performed_time, file_name=FILE_NAME):
    today_date = datetime.now().strftime("%Y-%m-%d")
    performed_dt = datetime.strptime(performed_time, "%H:%M")
    scheduled_dt = datetime.strptime(scheduled_times[prayer_name], "%H:%M")

    status = "Finished"
    note = ""

    if performed_dt > scheduled_dt:
        for later_name in list(prayers.keys()):
            if later_name != prayer_name and scheduled_times.get(later_name):
                later_time = datetime.strptime(scheduled_times[later_name], "%H:%M")
                if performed_dt > later_time:
                    status = "Finished"
                    note = f"Performed as make up for a missed Prayer"
                    break
        else:
            status = "Finished"
            
    try:
        df = pd.read_excel(file_name)
        idx = df[(df['Date'] == today_date) & (df['Prayer'] == prayer_name)].index
        if not idx.empty:
            df.loc[idx, 'Performed Time'] = performed_time
            df.loc[idx, 'Status'] = status
            df.loc[idx, 'Notes'] = note
            df.to_excel(file_name, index=False)
            print(f"Updated status for {prayer_name}: {status}")
    except FileNotFoundError:
        print("Error: Log file not found.")

def perform_prayer(prayer_name, scheduled_times):

    if is_prayer_already_done(prayer_name):
        print(f"\nYou've already performed {prayer_name} today. No need to do it again!\n")
        return  # or skip this prayer logic

    print(f"Starting tracking for: {prayer_name}")
    expected_rakah = prayers[prayer_name]['rakah']
    expected_sajdah = prayers[prayer_name]['sajdah']

    # Try to initialize camera with better error handling
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera access denied or not available.")
        print("Please grant camera permissions to your terminal/Python application.")
        print("On macOS: System Preferences > Security & Privacy > Camera > Allow Terminal/Python")
        print("\nAlternatively, you can manually mark this prayer as completed.")
        manual_completion = input("Would you like to mark this prayer as completed manually? (y/n): ").lower().strip()
        if manual_completion == 'y':
            performed_time = datetime.now().strftime("%H:%M")
            update_prayer_status(prayer_name, scheduled_times, performed_time)
            print(f"✅ {prayer_name} prayer marked as completed manually.")
        return

    detector = pm.poseDetector()

    rakah, sajdah, dir, pTime = 0, 0, 0, 0

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame. Camera may have been disconnected.")
            break

        img = cv2.resize(img, (1920, 1280))
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)

        if lmList:
            coccyx = detector.findAngle(img, 12, 24, 26)
            knee = detector.findAngle(img, 24, 26, 28)

            rakah_coccyx = np.interp(coccyx, (180, 250), (0, 100))
            sajdah_coccyx = np.interp(coccyx, (260, 300), (0, 100))
            sajdah_knee = np.interp(knee, (20, 50), (0, 100))

            if rakah_coccyx <= 100 and rakah_coccyx >= 80 and  150 <= knee <= 190 and (dir == 0 or dir == 5):
                rakah += 0.5
                dir = 1
            elif rakah_coccyx == 0 and 150 <= knee <= 190 and dir == 1:
                rakah += 0.5
                dir = 2

            if rakah >= 1 and dir >= 2:
                if sajdah_coccyx == 100 and sajdah_knee == 100 and dir == 2:
                    sajdah += 1
                    dir = 3
                elif sajdah_coccyx >= 0  and sajdah_coccyx <= 20 and sajdah_knee >= 0  and sajdah_knee <= 20 and dir == 3:
                    sajdah += 0.5
                    dir = 4
                elif sajdah_coccyx <= 100 and sajdah_coccyx >= 80 and sajdah_knee <= 100 and sajdah_knee >= 80 and dir == 4:
                    sajdah += 0.5
                    dir = 5

            # ---- Display Counts ----
            cv2.rectangle(img, (0, 550), (120, 720), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, 'R', (40, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
            cv2.putText(img, str(int(rakah)), (40, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

            cv2.rectangle(img, (120, 550), (240, 720), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, 'S', (160, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
            cv2.putText(img, str(int(sajdah)), (160, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

            if int(rakah) >= expected_rakah and int(sajdah) >= expected_sajdah:
                print(f"{prayer_name} prayer completed!")
                performed_time = datetime.now().strftime("%H:%M")
                update_prayer_status(prayer_name, scheduled_times, performed_time)
                break

        cTime = time.time()
        fps = 1 / (cTime - pTime) if pTime else 0
        pTime = cTime
        cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

        cv2.imshow("Prayer Tracker", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Prayer manually stopped.")
            break

    cap.release()
    cv2.destroyAllWindows()


def is_prayer_already_done(prayer_name, file_name=FILE_NAME):
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        df = pd.read_excel(file_name)
        prayer_row = df[(df['Date'] == today) & (df['Prayer'] == prayer_name)]
        if not prayer_row.empty:
            return prayer_row.iloc[0]['Status'] == "Finished"
    except FileNotFoundError:
        return False
    return False

def main():
    # Check dependencies first
    if not check_dependencies():
        return
    
    print("🕌 Prayer Assistance Application Starting...")
    
    try:
        scheduled_times = get_prayer_times()
        print("✅ Prayer times retrieved successfully.")
    except Exception as e:
        print(f"❌ Failed to get prayer times: {e}")
        print("Please check your internet connection.")
        return
    
    initialize_daily_prayers(scheduled_times)
    current_prayer = get_current_prayer(scheduled_times)

    if not current_prayer:
        print("No current prayer time.")
        return

    missed = get_pending_prayers(current_prayer)
    for prayer in missed:
        print(f"🟡 Missed: {prayer}. Please perform it before {current_prayer}.")
        perform_prayer(prayer, scheduled_times)

    print(f"🟢 Now perform {current_prayer} prayer.")
    perform_prayer(current_prayer, scheduled_times)

if __name__ == "__main__":
    main()

