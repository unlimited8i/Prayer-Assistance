import cv2
import numpy as np
import time
import pandas as pd
from datetime import datetime
import PoseModule as pm
import requests

# Define prayers with rakah and sajdah counts
prayers = {
    "Fajr": {"rakah": 2, "sajdah": 4},
    "Dhuhr": {"rakah": 4, "sajdah": 8},
    "Asr": {"rakah": 4, "sajdah": 8},
    "Maghrib": {"rakah": 3, "sajdah": 6},
    "Isha": {"rakah": 4, "sajdah": 8}
}

def select_prayer():
    print("Select the prayer you want to perform:")
    for idx, prayer in enumerate(prayers.keys(), 1):
        print(f"{idx}. {prayer}")
    choice = int(input("Enter number: "))
    prayer_name = list(prayers.keys())[choice - 1]
    print(f"You selected: {prayer_name}")
    return prayer_name, prayers[prayer_name]['rakah'], prayers[prayer_name]['sajdah']

def save_prayer_to_excel(prayer_name, file_name='prayer_log.xlsx'):
    today_date = datetime.now().strftime("%Y-%m-%d")
    day_name = datetime.now().strftime("%A")  # E.g., Sunday

    # Create a dataframe for the completed prayer
    data = {
        'Date': [today_date],
        'Day': [day_name],
        'Prayer': [prayer_name],
    }

    df = pd.DataFrame(data)

    try:
        existing_df = pd.read_excel(file_name)

        # Check if the prayer was already logged today
        is_duplicate = (
            (existing_df['Date'] == today_date) &
            (existing_df['Prayer'] == prayer_name)
        ).any()

        if is_duplicate:
            print(f"\n{prayer_name} prayer is already logged for today ({today_date}). Not logging again.\n")
            return
        else:
            updated_df = pd.concat([existing_df, df], ignore_index=True)

    except FileNotFoundError:
        # No existing file, create a new one
        updated_df = df

    # Save the updated dataframe to Excel
    updated_df.to_excel(file_name, index=False)
    print(f"\nPrayer logged successfully to {file_name}!\n")

def main():
    # Step 1: Prayer selection
    prayer_name, expected_rakah, expected_sajdah = select_prayer()

    # Step 2: Initialize camera and pose detector
    cap = cv2.VideoCapture(0)
    detector = pm.poseDetector()

    rakah = 0
    sajdah = 0
    dir = 0
    pTime = 0

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame.")
            break

        img = cv2.resize(img, (1920, 1280))
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)

        if len(lmList) != 0:
            coccyx = detector.findAngle(img, 12, 24, 26)
            knee = detector.findAngle(img, 24, 26, 28)

            rakah_coccyx = np.interp(coccyx, (180, 250), (0, 100))
            sajdah_coccyx = np.interp(coccyx, (260, 300), (0, 100))
            sajdah_knee = np.interp(knee, (20, 50), (0, 100))

            # ---- Rakah logic ----
            color = (255, 0, 255)
            if rakah_coccyx == 100 and knee >= 150 and knee <= 190:
                color = (0, 255, 0)
                if dir == 0 or dir == 5:
                    rakah += 0.5
                    dir = 1
            if rakah_coccyx == 0 and knee >= 150 and knee <= 190:
                color = (0, 255, 0)
                if dir == 1:
                    rakah += 0.5
                    dir = 2

            # ---- Sajdah logic ----
            if rakah >= 1 and dir >= 2:
                if sajdah_coccyx == 100 and sajdah_knee == 100:
                    if dir == 2:
                        sajdah += 1
                        dir = 3
                if sajdah_coccyx == 0 and sajdah_knee == 0:
                    if dir == 3:
                        sajdah += 0.5
                        dir = 4
                if sajdah_coccyx == 100 and sajdah_knee == 100:
                    if dir == 4:
                        sajdah += 0.5
                        dir = 5

            # ---- Display Counts ----
            cv2.rectangle(img, (0, 550), (120, 720), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, 'R', (40, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
            cv2.putText(img, str(int(rakah)), (40, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

            cv2.rectangle(img, (120, 550), (240, 720), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, 'S', (160, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
            cv2.putText(img, str(int(sajdah)), (160, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

            # ---- Check if Prayer is Complete ----
            if int(rakah) >= expected_rakah and int(sajdah) >= expected_sajdah:
                print(f"\n{prayer_name} prayer completed!\n")
                save_prayer_to_excel(prayer_name)
                break

        # ---- FPS ----
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

        cv2.imshow("Prayer Tracker", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nPrayer manually stopped.\n")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
