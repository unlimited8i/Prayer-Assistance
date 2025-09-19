# import cv2
# import numpy as np
# import time
# import pandas as pd
# from datetime import datetime, timedelta
# import requests
# import PoseModule as pm

# LAT, LNG = 29.3117, 47.4818  # kuwait
# FILE_NAME = 'prayer_log1.xlsx'

# prayers = {
#     "Fajr": {"rakah": 2, "sajdah": 4},
#     "Dhuhr": {"rakah": 4, "sajdah": 8},
#     "Asr": {"rakah": 4, "sajdah": 8},
#     "Maghrib": {"rakah": 3, "sajdah": 6},
#     "Isha": {"rakah": 4, "sajdah": 8}
# }

# def get_prayer_times():
#     today = datetime.now().strftime("%d-%m-%Y")
#     url = f"http://api.aladhan.com/v1/timings/{today}?latitude={LAT}&longitude={LNG}&method=2"
#     response = requests.get(url)
#     data = response.json()
#     times = data['data']['timings']
#     return {
#         "Fajr": times["Fajr"][:5],
#         "Dhuhr": times["Dhuhr"][:5],
#         "Asr": times["Asr"][:5],
#         "Maghrib": times["Maghrib"][:5],
#         "Isha": times["Isha"][:5]
#     }

# def update_relative_day(file_name=FILE_NAME):
#     try:
#         df = pd.read_excel(file_name)
#         today = datetime.now().date()
#         df['Relative Day'] = df['Date'].apply(lambda d: _relative_day_label(datetime.strptime(str(d), "%Y-%m-%d").date(), today))
#         df.to_excel(file_name, index=False)
#         print("Updated 'Relative Day' column.")
#     except FileNotFoundError:
#         print("No existing file found for updating relative days.")

# def _relative_day_label(date, today):
#     delta = (today - date).days
#     if delta == 0:
#         return "Today"
#     elif delta == 1:
#         return "1 Day Ago"
#     else:
#         return f"{delta} Days Ago"

# def initialize_daily_prayers(scheduled_times, file_name=FILE_NAME):
#     update_relative_day(file_name)
#     today_date = datetime.now().strftime("%Y-%m-%d")
#     if check_already_initialized(today_date, file_name):
#         print("Today's prayers are already initialized.")
#         return

#     day_name = datetime.now().strftime("%A")

#     data = {
#         'Date': [], 'Day': [], 'Prayer': [], 'Scheduled Time': [],
#         'Performed Time': [], 'Status': [],  'Notes': [], 'Relative Day': []
#     }

#     for prayer, time in scheduled_times.items():
#         data['Date'].append(today_date)
#         data['Day'].append(day_name)
#         data['Prayer'].append(prayer)
#         data['Scheduled Time'].append(time)
#         data['Performed Time'].append("")
#         data['Status'].append("Not Finished")
#         data['Notes'].append("")
#         data['Relative Day'].append("Today")

#     df = pd.DataFrame(data)

#     try:
#         existing_df = pd.read_excel(file_name)
#         updated_df = pd.concat([existing_df, df], ignore_index=True)
#     except FileNotFoundError:
#         updated_df = df

#     updated_df.to_excel(file_name, index=False)
#     print(f"Initialized daily prayer log for {today_date}.")

# def check_already_initialized(today, file_name):
#     try:
#         df = pd.read_excel(file_name)
#         return today in df['Date'].astype(str).values
#     except:
#         return False

# def get_current_prayer(scheduled_times):
#     now = datetime.now().strftime("%H:%M")
#     current = None
#     for prayer in list(prayers.keys())[::-1]:  # Check latest first
#         if now >= scheduled_times[prayer]:
#             current = prayer
#             break
#     return current

# def get_pending_prayers(prayer_name, file_name=FILE_NAME):
#     today = datetime.now().strftime("%Y-%m-%d")
#     try:
#         df = pd.read_excel(file_name)
#         today_df = df[df['Date'] == today]
#         prayer_list = list(prayers.keys())
#         idx = prayer_list.index(prayer_name)
#         earlier = prayer_list[:idx]
#         pending = today_df[(today_df['Prayer'].isin(earlier)) & (today_df['Status'] == 'Not Finished')]
#         return list(pending['Prayer'])
#     except FileNotFoundError:
#         return []

# def update_prayer_status(prayer_name, scheduled_times, performed_time, file_name=FILE_NAME):
#     today_date = datetime.now().strftime("%Y-%m-%d")
#     performed_dt = datetime.strptime(performed_time, "%H:%M")
#     scheduled_dt = datetime.strptime(scheduled_times[prayer_name], "%H:%M")

#     status = "Finished"
#     note = ""

#     if performed_dt > scheduled_dt:
#         for later_name in list(prayers.keys()):
#             if later_name != prayer_name and scheduled_times.get(later_name):
#                 later_time = datetime.strptime(scheduled_times[later_name], "%H:%M")
#                 if performed_dt > later_time:
#                     status = "Finished"
#                     note = f"Performed as make up for a missed Prayer"
#                     break
#         else:
#             status = "Finished"
            
#     try:
#         df = pd.read_excel(file_name)
#         idx = df[(df['Date'] == today_date) & (df['Prayer'] == prayer_name)].index
#         if not idx.empty:
#             df.loc[idx, 'Performed Time'] = performed_time
#             df.loc[idx, 'Status'] = status
#             df.loc[idx, 'Notes'] = note
#             df.to_excel(file_name, index=False)
#             print(f"Updated status for {prayer_name}: {status}")
#     except FileNotFoundError:
#         print("Error: Log file not found.")

# def perform_prayer(prayer_name, scheduled_times):

#     if is_prayer_already_done(prayer_name):
#         print(f"\nYou've already performed {prayer_name} today. No need to do it again!\n")
#         return  # or skip this prayer logic

#     print(f"Starting tracking for: {prayer_name}")
#     expected_rakah = prayers[prayer_name]['rakah']
#     expected_sajdah = prayers[prayer_name]['sajdah']

#     cap = cv2.VideoCapture(0)
#     detector = pm.poseDetector()

#     rakah, sajdah, dir, pTime = 0, 0, 0, 0

#     while True:
#         success, img = cap.read()
#         if not success:
#             print("Failed to grab frame.")
#             break

#         img = cv2.resize(img, (1920, 1280))
#         img = detector.findPose(img, False)
#         lmList = detector.findPosition(img, False)

#         if lmList:
#             coccyx = detector.findAngle(img, 12, 24, 26)
#             knee = detector.findAngle(img, 24, 26, 28)

#             rakah_coccyx = np.interp(coccyx, (180, 250), (0, 100))
#             sajdah_coccyx = np.interp(coccyx, (260, 300), (0, 100))
#             sajdah_knee = np.interp(knee, (20, 50), (0, 100))

#             if rakah_coccyx <= 100 and rakah_coccyx >= 80 and  150 <= knee <= 190 and (dir == 0 or dir == 5):
#                 rakah += 0.5
#                 dir = 1
#             elif rakah_coccyx == 0 and 150 <= knee <= 190 and dir == 1:
#                 rakah += 0.5
#                 dir = 2

#             if rakah >= 1 and dir >= 2:
#                 if sajdah_coccyx == 100 and sajdah_knee == 100 and dir == 2:
#                     sajdah += 1
#                     dir = 3
#                 elif sajdah_coccyx >= 0  and sajdah_coccyx <= 20 and sajdah_knee >= 0  and sajdah_knee <= 20 and dir == 3:
#                     sajdah += 0.5
#                     dir = 4
#                 elif sajdah_coccyx <= 100 and sajdah_coccyx >= 80 and sajdah_knee <= 100 and sajdah_knee >= 80 and dir == 4:
#                     sajdah += 0.5
#                     dir = 5

#             # ---- Display Counts ----
#             cv2.rectangle(img, (0, 550), (120, 720), (0, 255, 0), cv2.FILLED)
#             cv2.putText(img, 'R', (40, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(rakah)), (40, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             cv2.rectangle(img, (120, 550), (240, 720), (0, 0, 255), cv2.FILLED)
#             cv2.putText(img, 'S', (160, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(sajdah)), (160, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             if int(rakah) >= expected_rakah and int(sajdah) >= expected_sajdah:
#                 print(f"{prayer_name} prayer completed!")
#                 performed_time = datetime.now().strftime("%H:%M")
#                 update_prayer_status(prayer_name, scheduled_times, performed_time)
#                 break

#         cTime = time.time()
#         fps = 1 / (cTime - pTime) if pTime else 0
#         pTime = cTime
#         cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

#         cv2.imshow("Prayer Tracker", img)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             print("Prayer manually stopped.")
#             break

#     cap.release()
#     cv2.destroyAllWindows()


# def is_prayer_already_done(prayer_name, file_name=FILE_NAME):
#     today = datetime.now().strftime("%Y-%m-%d")
#     try:
#         df = pd.read_excel(file_name)
#         prayer_row = df[(df['Date'] == today) & (df['Prayer'] == prayer_name)]
#         if not prayer_row.empty:
#             return prayer_row.iloc[0]['Status'] == "Finished"
#     except FileNotFoundError:
#         return False
#     return False

# def main():
#     scheduled_times = get_prayer_times()
#     initialize_daily_prayers(scheduled_times)
#     current_prayer = get_current_prayer(scheduled_times)

#     if not current_prayer:
#         print("No current prayer time.")
#         return

#     missed = get_pending_prayers(current_prayer)
#     for prayer in missed:
#         print(f"🟡 Missed: {prayer}. Please perform it before {current_prayer}.")
#         perform_prayer(prayer, scheduled_times)

#     print(f"🟢 Now perform {current_prayer} prayer.")
#     perform_prayer(current_prayer, scheduled_times)

# if __name__ == "__main__":
#     main()


# import cv2
# import numpy as np
# import time
# import pandas as pd
# from datetime import datetime, timedelta
# import requests
# import PoseModule as pm

# LAT, LNG = 29.378586, 47.990341  # kuwait location
# FILE_NAME = 'prayer_log.xlsx'

# prayers = {
#     "Fajr": {"rakah": 2, "sajdah": 4},
#     "Dhuhr": {"rakah": 4, "sajdah": 8},
#     "Asr": {"rakah": 4, "sajdah": 8},
#     "Maghrib": {"rakah": 3, "sajdah": 6},
#     "Isha": {"rakah": 4, "sajdah": 8}
# }

# def get_prayer_times():
#     today = datetime.now().strftime("%d-%m-%Y")
#     url = f"http://api.aladhan.com/v1/timings/{today}?latitude={LAT}&longitude={LNG}&method=2"
#     response = requests.get(url)
#     data = response.json()
#     times = data['data']['timings']
#     return {
#         "Fajr": times["Fajr"][:5],
#         "Dhuhr": times["Dhuhr"][:5],
#         "Asr": times["Asr"][:5],
#         "Maghrib": times["Maghrib"][:5],
#         "Isha": times["Isha"][:5]
#     }

# def update_relative_day(file_name=FILE_NAME):
#     try:
#         df = pd.read_excel(file_name)
#         today = datetime.now().date()

#         relative_days = []
#         for d in pd.to_datetime(df['Date']).dt.date:
#             delta = (today - d).days
#             label = "Today" if delta == 0 else f"{delta} Day{'s' if delta > 1 else ''} Ago"
#             relative_days.append(label)

#         df['Relative Day'] = relative_days
#         df.to_excel(file_name, index=False)
#         print("Updated 'Relative Day' column.")
#     except FileNotFoundError:
#         print("No existing file found for updating relative days.")

# def initialize_daily_prayers(scheduled_times, file_name=FILE_NAME):
#     update_relative_day(file_name)

#     today_date = datetime.now().strftime("%Y-%m-%d")
#     if check_already_initialized(today_date, file_name):
#         print("Today's prayers are already initialized.")
#         return

#     day_name = datetime.now().strftime("%A")

#     data = {
#         'Date': [], 'Day': [], 'Prayer': [], 'Scheduled Time': [],
#         'Performed Time': [], 'Status': [], 'Performed After': [], 'Notes': [], 'Relative Day': []
#     }

#     for prayer, time in scheduled_times.items():
#         data['Date'].append(today_date)
#         data['Day'].append(day_name)
#         data['Prayer'].append(prayer)
#         data['Scheduled Time'].append(time)
#         data['Performed Time'].append("")
#         data['Status'].append("Not Finished")
#         data['Performed After'].append("None")
#         data['Notes'].append("")
#         data['Relative Day'].append("Today")

#     df = pd.DataFrame(data)

#     try:
#         existing_df = pd.read_excel(file_name)
#         updated_df = pd.concat([existing_df, df], ignore_index=True)
#     except FileNotFoundError:
#         updated_df = df

#     updated_df.to_excel(file_name, index=False)
#     print(f"Initialized daily prayer log for {today_date}.")

# def check_already_initialized(today, file_name):
#     try:
#         df = pd.read_excel(file_name)
#         return today in df['Date'].astype(str).values
#     except:
#         return False

# def get_current_prayer(scheduled_times):
#     now = datetime.now().strftime("%H:%M")
#     current = None
#     for prayer in list(prayers.keys())[::-1]:  # Check latest first
#         if now >= scheduled_times[prayer]:
#             current = prayer
#             break
#     return current

# def update_prayer_status(prayer_name, scheduled_times, performed_time, file_name=FILE_NAME):
#     today_date = datetime.now().strftime("%Y-%m-%d")
#     performed_dt = datetime.strptime(performed_time, "%H:%M")
#     scheduled_dt = datetime.strptime(scheduled_times[prayer_name], "%H:%M")

#     status = "Finished"
#     performed_after = "None"

#     if performed_dt > scheduled_dt:
#         found_later = False
#         for later_name in list(prayers.keys()):
#             if later_name != prayer_name and scheduled_times.get(later_name):
#                 later_time = datetime.strptime(scheduled_times[later_name], "%H:%M")
#                 if later_time > scheduled_dt and performed_dt > later_time:
#                     status = "Made Up After Next"
#                     performed_after = later_name
#                     found_later = True
#                     break
#         if not found_later:
#             status = "Late"

#     try:
#         df = pd.read_excel(file_name)
#         idx = df[(df['Date'] == today_date) & (df['Prayer'] == prayer_name)].index
#         if not idx.empty:
#             df.loc[idx, 'Performed Time'] = performed_time
#             df.loc[idx, 'Status'] = status
#             df.loc[idx, 'Performed After'] = performed_after
#             df.to_excel(file_name, index=False)
#             print(f"Updated status for {prayer_name}: {status}")
#     except FileNotFoundError:
#         print("Error: Log file not found.")

# def main():
#     scheduled_times = get_prayer_times()
#     current_time = datetime.now().strftime("%H:%M")
#     today = datetime.now().strftime("%Y-%m-%d")

#     # Initialize daily prayers
#     initialize_daily_prayers(scheduled_times)

#     prayer_name = get_current_prayer(scheduled_times)
#     if not prayer_name:
#         print("No active prayer period right now.")
#         return

#     print(f"Detected time for: {prayer_name} prayer")
#     expected_rakah = prayers[prayer_name]['rakah']
#     expected_sajdah = prayers[prayer_name]['sajdah']

#     cap = cv2.VideoCapture(0)
#     detector = pm.poseDetector()

#     rakah, sajdah, dir, pTime = 0, 0, 0, 0

#     while True:
#         success, img = cap.read()
#         if not success:
#             print("Failed to grab frame.")
#             break

#         img = cv2.resize(img, (1920, 1280))
#         img = detector.findPose(img, False)
#         lmList = detector.findPosition(img, False)

#         if lmList:
#             coccyx = detector.findAngle(img, 12, 24, 26)
#             knee = detector.findAngle(img, 24, 26, 28)

#             rakah_coccyx = np.interp(coccyx, (180, 250), (0, 100))
#             sajdah_coccyx = np.interp(coccyx, (260, 300), (0, 100))
#             sajdah_knee = np.interp(knee, (20, 50), (0, 100))

#             if rakah_coccyx == 100 and 150 <= knee <= 190 and (dir == 0 or dir == 5):
#                 rakah += 0.5
#                 dir = 1
#             elif rakah_coccyx == 0 and 150 <= knee <= 190 and dir == 1:
#                 rakah += 0.5
#                 dir = 2

#             if rakah >= 1 and dir >= 2:
#                 if sajdah_coccyx == 100 and sajdah_knee == 100 and dir == 2:
#                     sajdah += 1
#                     dir = 3
#                 elif sajdah_coccyx >= 0  and sajdah_coccyx <= 20 and sajdah_knee >= 0  and sajdah_knee <= 20 and dir == 3:
#                     sajdah += 0.5
#                     dir = 4
#                 elif sajdah_coccyx <= 100 and sajdah_coccyx >= 80 and sajdah_knee <= 100 and sajdah_knee >= 80 and dir == 4:
#                     sajdah += 0.5
#                     dir = 5

#             # ---- Display Counts ----
#             cv2.rectangle(img, (0, 550), (120, 720), (0, 255, 0), cv2.FILLED)
#             cv2.putText(img, 'R', (40, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(rakah)), (40, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             cv2.rectangle(img, (120, 550), (240, 720), (0, 0, 255), cv2.FILLED)
#             cv2.putText(img, 'S', (160, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(sajdah)), (160, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             if int(rakah) >= expected_rakah and int(sajdah) >= expected_sajdah:
#                 print(f"{prayer_name} prayer completed!")
#                 performed_time = datetime.now().strftime("%H:%M")
#                 update_prayer_status(prayer_name, scheduled_times, performed_time)
#                 break

#         cTime = time.time()
#         fps = 1 / (cTime - pTime) if pTime else 0
#         pTime = cTime
#         cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

#         cv2.imshow("Prayer Tracker", img)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             print("Prayer manually stopped.")
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()

# import cv2
# import numpy as np
# import time
# import pandas as pd
# from datetime import datetime
# import requests
# import PoseModule as pm

# # Define prayers and their sajdah/rakah counts
# prayers = {
#     "Fajr": {"rakah": 2, "sajdah": 4},
#     "Dhuhr": {"rakah": 4, "sajdah": 8},
#     "Asr": {"rakah": 4, "sajdah": 8},
#     "Maghrib": {"rakah": 3, "sajdah": 6},
#     "Isha": {"rakah": 4, "sajdah": 8}
# }

# LAT, LNG = 29.378586, 47.990341  # kuwait location
# FILE_NAME = 'prayer_log.xlsx'

# def get_prayer_times():
#     today = datetime.now().strftime("%d-%m-%Y")
#     url = f"http://api.aladhan.com/v1/timings/{today}?latitude={LAT}&longitude={LNG}&method=2"
#     response = requests.get(url)
#     data = response.json()
#     times = data['data']['timings']
#     return {
#         "Fajr": times["Fajr"][:5],
#         "Dhuhr": times["Dhuhr"][:5],
#         "Asr": times["Asr"][:5],
#         "Maghrib": times["Maghrib"][:5],
#         "Isha": times["Isha"][:5]
#     }

# def initialize_daily_prayers(scheduled_times, file_name='prayer_log.xlsx'):
#     today_date = datetime.now().strftime("%Y-%m-%d")
#     day_name = datetime.now().strftime("%A")

#     data = {
#         'Date': [], 'Day': [], 'Prayer': [], 'Scheduled Time': [],
#         'Performed Time': [], 'Status': [], 'Performed After': [], 'Notes': []
#     }

#     for prayer, time in scheduled_times.items():
#         data['Date'].append(today_date)
#         data['Day'].append(day_name)
#         data['Prayer'].append(prayer)
#         data['Scheduled Time'].append(time)
#         data['Performed Time'].append("")
#         data['Status'].append("Not Finished")
#         data['Performed After'].append("None")
#         data['Notes'].append("")

#     df = pd.DataFrame(data)
#     df.to_excel('prayer_log.xlsx', index=False)
#     print(f"Initialized daily prayer log for {today_date}.")

# def get_current_prayer(scheduled_times):
#     now = datetime.now().strftime("%H:%M")
#     current = None
#     for prayer in list(prayers.keys())[::-1]:  # Check latest first
#         if now >= scheduled_times[prayer]:
#             current = prayer
#             break
#     return current

# def update_prayer_status(prayer_name, scheduled_times, performed_time, file_name='prayer_log.xlsx'):
#     today_date = datetime.now().strftime("%Y-%m-%d")
#     performed_dt = datetime.strptime(performed_time, "%H:%M")
#     scheduled_dt = datetime.strptime(scheduled_times[prayer_name], "%H:%M")

#     status = "Finished"
#     performed_after = "None"

#     if performed_dt > scheduled_dt:
#         found_later = False
#         for later_name in list(prayers.keys()):
#             if later_name != prayer_name and scheduled_times.get(later_name):
#                 later_time = datetime.strptime(scheduled_times[later_name], "%H:%M")
#                 if later_time > scheduled_dt and performed_dt > later_time:
#                     status = "Made Up After Next"
#                     performed_after = later_name
#                     found_later = True
#                     break
#         if not found_later:
#             status = "Late"

#     try:
#         df = pd.read_excel('prayer_log.xlsx')
#         idx = df[(df['Date'] == today_date) & (df['Prayer'] == prayer_name)].index
#         if not idx.empty:
#             df.loc[idx, 'Performed Time'] = performed_time
#             df.loc[idx, 'Status'] = status
#             df.loc[idx, 'Performed After'] = performed_after
#             df.to_excel('prayer_log.xlsx', index=False)
#             print(f"Updated status for {prayer_name}: {status}")
#     except FileNotFoundError:
#         print("Error: Log file not found.")

# def main():
#     scheduled_times = get_prayer_times()
#     current_time = datetime.now().strftime("%H:%M")
#     today = datetime.now().strftime("%Y-%m-%d")

#     # Initialize log file only at Fajr time
#     if current_time <= scheduled_times["Fajr"]:
#         initialize_daily_prayers(scheduled_times)

#     prayer_name = get_current_prayer(scheduled_times)
#     if not prayer_name:
#         print("No active prayer period right now.")
#         return

#     print(f"Detected time for: {prayer_name} prayer")
#     expected_rakah = prayers[prayer_name]['rakah']
#     expected_sajdah = prayers[prayer_name]['sajdah']

#     cap = cv2.VideoCapture(0)
#     detector = pm.poseDetector()

#     rakah, sajdah, dir, pTime = 0, 0, 0, 0

#     while True:
#         success, img = cap.read()
#         if not success:
#             print("Failed to grab frame.")
#             break

#         img = cv2.resize(img, (1920, 1280))
#         img = detector.findPose(img, False)
#         lmList = detector.findPosition(img, False)

#         if lmList:
#             coccyx = detector.findAngle(img, 12, 24, 26)
#             knee = detector.findAngle(img, 24, 26, 28)

#             rakah_coccyx = np.interp(coccyx, (180, 250), (0, 100))
#             sajdah_coccyx = np.interp(coccyx, (260, 300), (0, 100))
#             sajdah_knee = np.interp(knee, (20, 50), (0, 100))

#             # Rakah logic
#             if rakah_coccyx == 100 and 150 <= knee <= 190 and (dir == 0 or dir == 5):
#                 rakah += 0.5
#                 dir = 1
#             elif rakah_coccyx == 0 and 150 <= knee <= 190 and dir == 1:
#                 rakah += 0.5
#                 dir = 2

#             # Sajdah logic
#             if rakah >= 1 and dir >= 2:
#                 if sajdah_coccyx == 100 and sajdah_knee == 100 and dir == 2:
#                     sajdah += 1
#                     dir = 3
#                 elif sajdah_coccyx >= 0  and sajdah_coccyx <= 20 and sajdah_knee >= 0  and sajdah_knee <= 20 and dir == 3:
#                     sajdah += 0.5
#                     dir = 4
#                 elif sajdah_coccyx <= 100 and sajdah_coccyx >= 80 and sajdah_knee <= 100 and sajdah_knee >= 80 and dir == 4:
#                     sajdah += 0.5
#                     dir = 5


#             # ---- Display Counts ----
#             cv2.rectangle(img, (0, 550), (120, 720), (0, 255, 0), cv2.FILLED)
#             cv2.putText(img, 'R', (40, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(rakah)), (40, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             cv2.rectangle(img, (120, 550), (240, 720), (0, 0, 255), cv2.FILLED)
#             cv2.putText(img, 'S', (160, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(sajdah)), (160, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             if int(rakah) >= expected_rakah and int(sajdah) >= expected_sajdah:
#                 print(f"{prayer_name} prayer completed!")
#                 performed_time = datetime.now().strftime("%H:%M")
#                 update_prayer_status(prayer_name, scheduled_times, performed_time)
#                 break

#         # FPS counter
#         cTime = time.time()
#         fps = 1 / (cTime - pTime) if pTime else 0
#         pTime = cTime
#         cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

#         cv2.imshow("Prayer Tracker", img)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             print("Prayer manually stopped.")
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()



# import cv2
# import numpy as np
# import time
# import pandas as pd
# from datetime import datetime
# import requests
# import PoseModule as pm  # Ensure this module is available in your environment

# # Define prayers with rakah and sajdah counts
# prayers = {
#     "Fajr": {"rakah": 2, "sajdah": 4},
#     "Dhuhr": {"rakah": 4, "sajdah": 8},
#     "Asr": {"rakah": 4, "sajdah": 8},
#     "Maghrib": {"rakah": 3, "sajdah": 6},
#     "Isha": {"rakah": 4, "sajdah": 8}
# }

# def get_prayer_times(lat, lon):
#     url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
#     response = requests.get(url)
#     data = response.json()
#     timings = data['data']['timings']
#     prayer_times = {
#         "Fajr": timings['Fajr'],
#         "Dhuhr": timings['Dhuhr'],
#         "Asr": timings['Asr'],
#         "Maghrib": timings['Maghrib'],
#         "Isha": timings['Isha']
#     }
#     return prayer_times

# def get_current_prayer(prayer_times):
#     now = datetime.now().time()
#     prayers_order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

#     time_objects = {}
#     for prayer, t_str in prayer_times.items():
#         h, m = map(int, t_str.split(":"))
#         time_objects[prayer] = datetime.now().replace(hour=h, minute=m, second=0).time()

#     for i in range(len(prayers_order)):
#         current = prayers_order[i]
#         next_prayer = prayers_order[i + 1] if i + 1 < len(prayers_order) else None

#         if next_prayer:
#             if time_objects[current] <= now < time_objects[next_prayer]:
#                 return current
#         else:
#             return current  # Isha is the last

#     return None

# def auto_select_prayer(lat=24.7136, lon=46.6753):  # Default to Riyadh
#     prayer_times = get_prayer_times(lat, lon)
#     current_prayer = get_current_prayer(prayer_times)

#     if current_prayer:
#         print(f"Automatically selected prayer: {current_prayer}")
#         return current_prayer, prayers[current_prayer]['rakah'], prayers[current_prayer]['sajdah']
#     else:
#         print("Couldn't determine current prayer.")
#         exit()

# def save_prayer_to_excel(prayer_name, file_name='prayer_log.xlsx'):
#     today_date = datetime.now().strftime("%Y-%m-%d")
#     day_name = datetime.now().strftime("%A")

#     data = {
#         'Date': [today_date],
#         'Day': [day_name],
#         'Prayer': [prayer_name],
#     }

#     df = pd.DataFrame(data)

#     try:
#         existing_df = pd.read_excel(file_name)
#         is_duplicate = (
#             (existing_df['Date'] == today_date) &
#             (existing_df['Prayer'] == prayer_name)
#         ).any()

#         if is_duplicate:
#             print(f"\n{prayer_name} prayer is already logged for today ({today_date}). Not logging again.\n")
#             return
#         else:
#             updated_df = pd.concat([existing_df, df], ignore_index=True)

#     except FileNotFoundError:
#         updated_df = df

#     updated_df.to_excel(file_name, index=False)
#     print(f"\nPrayer logged successfully to {file_name}!\n")

# def main():
#     # Step 1: Auto Prayer Selection
#     prayer_name, expected_rakah, expected_sajdah = auto_select_prayer()
#     print(prayer_name)
#     # Step 2: Initialize camera and pose detector
#     cap = cv2.VideoCapture(0)
#     detector = pm.poseDetector()

#     rakah = 0
#     sajdah = 0
#     dir = 0
#     pTime = 0

#     while True:
#         success, img = cap.read()
#         if not success:
#             print("Failed to grab frame.")
#             break

#         img = cv2.resize(img, (1920, 1280))
#         img = detector.findPose(img, False)
#         lmList = detector.findPosition(img, False)

#         if len(lmList) != 0:
#             coccyx = detector.findAngle(img, 12, 24, 26)
#             knee = detector.findAngle(img, 24, 26, 28)

#             rakah_coccyx = np.interp(coccyx, (180, 250), (0, 100))
#             sajdah_coccyx = np.interp(coccyx, (260, 300), (0, 100))
#             sajdah_knee = np.interp(knee, (20, 50), (0, 100))

#             color = (255, 0, 255)
#             if rakah_coccyx == 100 and 150 <= knee <= 190:
#                 color = (0, 255, 0)
#                 if dir == 0 or dir == 5:
#                     rakah += 0.5
#                     dir = 1
#             if rakah_coccyx == 0 and 150 <= knee <= 190:
#                 color = (0, 255, 0)
#                 if dir == 1:
#                     rakah += 0.5
#                     dir = 2

#             if rakah >= 1 and dir >= 2:
#                 if sajdah_coccyx == 100 and sajdah_knee == 100:
#                     if dir == 2:
#                         sajdah += 1
#                         dir = 3
#                 if sajdah_coccyx == 0 and sajdah_knee == 0:
#                     if dir == 3:
#                         sajdah += 0.5
#                         dir = 4
#                 if sajdah_coccyx == 100 and sajdah_knee == 100:
#                     if dir == 4:
#                         sajdah += 0.5
#                         dir = 5

#             # ---- Display Counts ----
#             cv2.rectangle(img, (0, 550), (120, 720), (0, 255, 0), cv2.FILLED)
#             cv2.putText(img, 'R', (40, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(rakah)), (40, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             cv2.rectangle(img, (120, 550), (240, 720), (0, 0, 255), cv2.FILLED)
#             cv2.putText(img, 'S', (160, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(sajdah)), (160, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             if int(rakah) >= expected_rakah and int(sajdah) >= expected_sajdah:
#                 print(f"\n{prayer_name} prayer completed!\n")
#                 save_prayer_to_excel(prayer_name)
#                 break

#         # ---- FPS ----
#         cTime = time.time()
#         fps = 1 / (cTime - pTime)
#         pTime = cTime
#         cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

#         cv2.imshow("Prayer Tracker", img)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             print("\nPrayer manually stopped.\n")
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()


# import cv2
# import numpy as np
# import time
# import PoseModule as pm

# cap = cv2.VideoCapture(0)

# detector = pm.poseDetector()
# rakah = 0
# sajdah = 0
# dir = 0
# pTime = 0
# while True:
#     success, img = cap.read()
#     img = cv2.resize(img, (1920, 1280))
#     # img = cv2.imread("AiTrainer/test.jpg")
#     img = detector.findPose(img, False)
#     lmList = detector.findPosition(img, False)
#     # print(lmList)
#     if len(lmList) != 0:
#         # coccyx 
#         coccyx = detector.findAngle(img, 12, 24, 26)
#         knee = detector.findAngle(img, 24, 26, 28)

#         #angle = detector.findAngle(img, 11, 13, 15,False)
#         rakah_coccyx = np.interp(coccyx, (180, 250), (0, 100))
#         sajdah_coccyx = np.interp(coccyx, (260, 300), (0, 100))
#         # print(sajdah_coccyx)
#         sajdah_knee = np.interp(knee, (20, 50), (0, 100))
#         print(sajdah_knee)


#         bar = np.interp(coccyx, (190, 240), (650, 100))
#         # print(angle, rakah_coccyx)

#         # Check for rakah
#         color = (255, 0, 255)
#         if rakah_coccyx == 100 and knee >= 150 and knee <= 190:
#             color = (0, 255, 0)
#             if dir == 0 or dir == 5 :
#                 rakah += 0.5
#                 dir = 1
#         if rakah_coccyx == 0 and knee >= 150 and knee <= 190:
#             color = (0, 255, 0)
#             if dir == 1:
#                 rakah += 0.5
#                 dir = 2
#         # print(rakah)

#         if rakah >=1 and dir >= 2 :
#             if sajdah_coccyx == 100 and sajdah_knee == 100:
#                 if dir == 2:
#                     sajdah +=1
#                     dir = 3
#             # print(sajdah)
#             if sajdah_coccyx == 0 and sajdah_knee == 0:
#                 if dir == 3:
#                     sajdah +=0.5
#                     dir = 4
#             # print(sajdah)

#             if sajdah_coccyx == 100 and sajdah_knee == 100:
#                 if dir == 4:
#                     sajdah +=0.5
#                     dir = 5
#             # print(sajdah)





#         # Draw Bar
#         # cv2.rectangle(img, (1100, 100), (1175, 650), color, 3)
#         # cv2.rectangle(img, (1100, int(bar)), (1175, 650), color, cv2.FILLED)
#         # cv2.putText(img, f'{int(rakah_coccyx)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4,
#         #             color, 4)

#         # rakah count
#         cv2.rectangle(img, (0, 550), (120, 720), (0, 255, 0), cv2.FILLED)
#         cv2.putText(img, 'R', (40, 620), cv2.FONT_HERSHEY_PLAIN, 5,
#                     (255, 0, 0), 15)
#         cv2.putText(img, str(int(rakah)), (40, 690), cv2.FONT_HERSHEY_PLAIN, 5,
#                     (255, 0, 0), 15)

#         # Sajdah count
#         cv2.rectangle(img, (120, 550), (240, 720), (0, 0, 255), cv2.FILLED)
#         cv2.putText(img, 'S', (160, 620), cv2.FONT_HERSHEY_PLAIN, 5,
#                     (255, 0, 0), 15)
#         cv2.putText(img, str(int(sajdah)), (160, 690), cv2.FONT_HERSHEY_PLAIN, 5,
#                     (255, 0, 0), 15)
        

#     cTime = time.time()
#     fps = 1 / (cTime - pTime)
#     pTime = cTime
#     cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5,
#                 (255, 0, 0), 5)

#     cv2.imshow("Image", img)
#     cv2.waitKey(1)


# import cv2
# import numpy as np
# import time
# import pandas as pd
# from datetime import datetime
# import PoseModule as pm

# # Define prayers with rakah and sajdah counts
# prayers = {
#     "Fajr": {"rakah": 2, "sajdah": 4},
#     "Dhuhr": {"rakah": 4, "sajdah": 8},
#     "Asr": {"rakah": 4, "sajdah": 8},
#     "Maghrib": {"rakah": 3, "sajdah": 6},
#     "Isha": {"rakah": 4, "sajdah": 8}
# }

# def select_prayer():
#     print("Select the prayer you want to perform:")
#     for idx, prayer in enumerate(prayers.keys(), 1):
#         print(f"{idx}. {prayer}")
#     choice = int(input("Enter number: "))
#     prayer_name = list(prayers.keys())[choice - 1]
#     print(f"You selected: {prayer_name}")
#     return prayer_name, prayers[prayer_name]['rakah'], prayers[prayer_name]['sajdah']

# def save_prayer_to_excel(prayer_name, rakah_count, sajdah_count, file_name='prayer_log.xlsx'):
#     data = {
#         'Date': [datetime.now().strftime("%Y-%m-%d")],
#         'Time': [datetime.now().strftime("%H:%M:%S")],
#         'Prayer': [prayer_name],
#         'Rakah Count': [rakah_count],
#         'Sajdah Count': [sajdah_count]
#     }
#     df = pd.DataFrame(data)

#     try:
#         existing_df = pd.read_excel(file_name)
#         updated_df = pd.concat([existing_df, df], ignore_index=True)
#     except FileNotFoundError:
#         updated_df = df

#     updated_df.to_excel(file_name, index=False)
#     print(f"\nPrayer logged successfully to {file_name}!\n")

# def main():
#     # Step 1: Prayer selection
#     prayer_name, expected_rakah, expected_sajdah = select_prayer()

#     # Step 2: Initialize camera and pose detector
#     cap = cv2.VideoCapture(0)
#     detector = pm.poseDetector()

#     rakah = 0
#     sajdah = 0
#     dir = 0
#     pTime = 0

#     while True:
#         success, img = cap.read()
#         if not success:
#             print("Failed to grab frame.")
#             break

#         img = cv2.resize(img, (1920, 1280))
#         img = detector.findPose(img, False)
#         lmList = detector.findPosition(img, False)

#         if len(lmList) != 0:
#             coccyx = detector.findAngle(img, 12, 24, 26)
#             knee = detector.findAngle(img, 24, 26, 28)

#             rakah_coccyx = np.interp(coccyx, (180, 250), (0, 100))
#             sajdah_coccyx = np.interp(coccyx, (260, 300), (0, 100))
#             sajdah_knee = np.interp(knee, (20, 50), (0, 100))

#             # ---- Rakah logic ----
#             color = (255, 0, 255)
#             if rakah_coccyx == 100 and knee >= 150 and knee <= 190:
#                 color = (0, 255, 0)
#                 if dir == 0 or dir == 5:
#                     rakah += 0.5
#                     dir = 1
#             if rakah_coccyx == 0 and knee >= 150 and knee <= 190:
#                 color = (0, 255, 0)
#                 if dir == 1:
#                     rakah += 0.5
#                     dir = 2

#             # ---- Sajdah logic ----
#             if rakah >= 1 and dir >= 2:
#                 if sajdah_coccyx == 100 and sajdah_knee == 100:
#                     if dir == 2:
#                         sajdah += 1
#                         dir = 3
#                 if sajdah_coccyx == 0 and sajdah_knee == 0:
#                     if dir == 3:
#                         sajdah += 0.5
#                         dir = 4
#                 if sajdah_coccyx == 100 and sajdah_knee == 100:
#                     if dir == 4:
#                         sajdah += 0.5
#                         dir = 5

#             # ---- Display Counts ----
#             cv2.rectangle(img, (0, 550), (120, 720), (0, 255, 0), cv2.FILLED)
#             cv2.putText(img, 'R', (40, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(rakah)), (40, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             cv2.rectangle(img, (120, 550), (240, 720), (0, 0, 255), cv2.FILLED)
#             cv2.putText(img, 'S', (160, 620), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)
#             cv2.putText(img, str(int(sajdah)), (160, 690), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 15)

#             # ---- Check if Prayer is Complete ----
#             if int(rakah) >= expected_rakah and int(sajdah) >= expected_sajdah:
#                 print(f"\n{prayer_name} prayer completed!\n")
#                 save_prayer_to_excel(prayer_name, int(rakah), int(sajdah))
#                 break

#         # ---- FPS ----
#         cTime = time.time()
#         fps = 1 / (cTime - pTime)
#         pTime = cTime
#         cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

#         cv2.imshow("Prayer Tracker", img)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             print("\nPrayer manually stopped.\n")
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()

