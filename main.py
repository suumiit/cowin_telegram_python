"""
Created on Tue May  18 03:19:56 2021
@author: Sumit Kumar
insta:@suu_miits
"""
import json
import requests
import datetime
import time
import hashlib
from fake_useragent import UserAgent
import os.path
from os import path
import filecmp
from shutil import copy
import difflib


#  IMP
#  get your token from botfather on Telegram and figure out the chat_id (Can be by sending a message in the created
#  group and looking at the https://api.telegram.org/bot{token}/getUpdates page. Save them in a txt file 'keys' in
#  consecutive lines

with open('keys.txt', 'r') as file:
    token = file.readline().strip('\n')
    chat_id = file.readline()

# max age
age = 18

# Fetch data
localFlag = 'Y'

# Print details flag
telegramFlag = 'Y'

# Number of days to check ahead
#numdays (for general dist of delhi)
casualDays = 3
#numdays (for specific dist of delhi)
specificDays = 8

"""
140	New Delhi
141	Central Delhi
142	West Delhi
143	North West Delhi
144	South East Delhi
145	East Delhi
146	North Delhi
147	North East Delhi
148	Shahdara
149	South Delhi
150	South West Delhi
"""
#Header required due to changes to API
#Generate random "User-Agent", to bypass the API limit 100 hits per 5 mins
temp_user_agent = UserAgent()
browser_header = {'User-Agent': temp_user_agent.random}

#For loop to get more than one dist (Note: if you want details of only 1 dist, the finalDistCode must be +1)
#Jharkhand (240-263), Dhanbad(257), East Singhbhum(Jamshedpur)(247), Ranchi(240)
#Currently Delhi
initialDistCode=140
finalDistCode=151

#Change the operation directory
current_directory = os.getcwd()
fileF = os.path.join(current_directory, r'fileFolder')
if not os.path.exists(fileF):
    os.makedirs(fileF)
cwd = os.getcwd()
pwd = os.chdir('fileFolder')

# For timing the loop
loop_starts = time.time()
while True:
    # district ID (Delhi)
    for i in range(initialDistCode, finalDistCode):
        if i==140 or i==143 or i==150:
            numdays=specificDays
        else:
            numdays=casualDays
        #  Getting the dates
        base = datetime.datetime.today()
        date_list = [base + datetime.timedelta(days=x) for x in range(numdays)]
        date_str = [x.strftime("%d-%m-%Y") for x in date_list]
        # print(base,"\n", date_list, "\n", date_str)
        for INP_DATE in date_str:
            #  URL for testing
            #URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=140&date=
            #18-05-2021"
            #API to get planned vaccination sessions on a specific date in a given district. Reading API documentation
            #recommended
            URL = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={i}&" \
                  f"date={INP_DATE}"
            response = requests.get(URL, headers=browser_header)
            if (response.status_code == 200 and (localFlag == 'y' or localFlag == 'Y')):
                print("\n",response.status_code)
            if response.status_code != 200:
                print("\n",response.status_code, "ERROR IN RESPONSE CODE", sep=' ')

            #assert response.status_code == 200, "Error in response code"
            #print(response.text)
            #Create file (content_{i}_{INP_DATE}.txt) for received data to compare from old data received
            # (Only if the response code is 200)
            if response.status_code==200:
                file1 = open(f'content_{i}_{INP_DATE}.txt', "w")
                file1.write(response.text)
                file1.close()

            # To get hash key of the text file:
            def hash_file(filename1, filename2):
                h1 = hashlib.sha1()
                h2 = hashlib.sha1()
                with open(filename1, 'rb') as file1:
                    chunk = 0
                    while chunk != b'':
                        chunk = file1.read(1024)
                        h1.update(chunk)
                with open(filename2, 'rb') as file2:
                    chunk = 0
                    while chunk != b'':
                        chunk = file2.read(1024)
                        h2.update(chunk)
                return [h1.hexdigest(), h2.hexdigest()]

            if not path.exists(f'pcontent_{i}_{INP_DATE}.txt'):
                f = open(f'pcontent_{i}_{INP_DATE}.txt', "w")
                assert path.exists(f'pcontent_{i}_{INP_DATE}.txt'), "File over written"
                f.close()
            if not path.exists(f'content_{i}_{INP_DATE}.txt'):
                f = open(f'content_{i}_{INP_DATE}.txt', "w")
                assert path.exists(f'content_{i}_{INP_DATE}.txt'), "File over written"
                f.close()

            """
            #copy(f'content_{i}_{INP_DATE}.txt', f'pcontent_{i}_{INP_DATE}.txt')
            #message1 = 1
            #message2 = 2
            """
            #Hash code of files:
            message1, message2 = hash_file(f'content_{i}_{INP_DATE}.txt', f'pcontent_{i}_{INP_DATE}.txt')

            #2nd method for comparison of files:
            message=filecmp.cmp(f'content_{i}_{INP_DATE}.txt', f'pcontent_{i}_{INP_DATE}.txt',)

            if localFlag == 'y' or localFlag == 'Y':
                print(i, "|", (INP_DATE))
                print(message1, message2, sep='\n')
                print("Match:",message)

            #Main Logic:
            if message1 != message2 and message != "False":
                #Transfer the data to old file i.e "pcontent_{i}_{INP_DATE}.txt"
                file1 = open(f'content_{i}_{INP_DATE}.txt', "r")
                file2 = open(f'pcontent_{i}_{INP_DATE}.txt', "w")
                for data1 in file1:
                    file2.write(data1)
                file2.close()
                file1.close()
            #Below to see the hit URL
            #print(response.url)
            #print(i)
                if response.ok:
                    resp_json = response.json()
                    #   print(json.dumps(resp_json, indent = 1))
                    #   flag = False
                    #   read documentation to understand following if/else tree
                    if resp_json["sessions"]:
                        # Data Fetching
                        for center in resp_json["sessions"]:
                            if (center["min_age_limit"]==age and center["available_capacity"]>1):# and center["vaccine"]=="COVAXIN"):
                                #print("center:", center)
                                center_id=center["center_id"]
                                #print("center_id", center_id)
                                if not path.exists(f'teleOutput_{i}_{INP_DATE}_{center_id}.txt'):
                                    f = open(f'teleOutput_{i}_{INP_DATE}_{center_id}.txt', "w")
                                    assert path.exists(f'teleOutput_{i}_{INP_DATE}_{center_id}.txt'), "File over written"
                                    f.close()
                                if not path.exists(f'telePOutput_{i}_{INP_DATE}_{center_id}.txt'):
                                    f = open(f'telePOutput_{i}_{INP_DATE}_{center_id}.txt', "w")
                                    assert path.exists(f'telePOutput_{i}_{INP_DATE}_{center_id}.txt'), "File over written"
                                    f.close()

                                with open(f'teleOutput_{i}_{INP_DATE}_{center_id}.txt', "w") as t_file:
                                    t_file.write(json.dumps(center))
                                    t_file.close()

                                # Hash code of files:
                                t_out, t_pout = hash_file(f'teleOutput_{i}_{INP_DATE}_{center_id}.txt',f'telePOutput_{i}_{INP_DATE}_{center_id}.txt')

                                # 2nd method for comparison of files:
                                alt_com_2 = filecmp.cmp(f'teleOutput_{i}_{INP_DATE}_{center_id}.txt',f'telePOutput_{i}_{INP_DATE}_{center_id}.txt', )

                                if localFlag == 'y' or localFlag == 'Y':
                                    print("Center:",center_id)
                                    print(t_out, t_pout, sep='\n')
                                    print("Match:", alt_com_2)

                                if t_out != t_pout:
                                    tfile1 = open(f'teleOutput_{i}_{INP_DATE}_{center_id}.txt', "r")
                                    tfile2 = open(f'telePOutput_{i}_{INP_DATE}_{center_id}.txt', "w")
                                    for data in tfile1:
                                        tfile2.write(data)
                                    tfile2.close()
                                    tfile1.close()

                                    if center['fee_type'] != "Free":
                                        f = center["fee"]
                                        p_fee = "Rs. {}".format(f)
                                    else:
                                        center["fee"] = 'Free'
                                        p_fee = center["fee"]
                                    if localFlag == 'y' or localFlag == 'Y':
                                        #if center["capacity"] > 0
                                        print("On{}".format(INP_DATE))
                                        print("\t",center["district_name"])
                                        print("\t","Name:", center["name"])
                                        #   print("\t", "Block Name:", center["block_name"])
                                        print("\t","Pin Code:", center["pincode"])
                                        #   print("\t", "Center:", center)
                                        print("\t","Min Age:", center['min_age_limit'])
                                        print("\t Free/Paid: ", center["fee_type"])
                                        print("\t Amount:", p_fee)
                                        print("\t Capacity:", center["available_capacity"])
                                        print("\t 1st Dose:", center["available_capacity_dose1"])
                                        print("\t 2nd Dose:", center["available_capacity_dose2"])
                                        if center["vaccine"] != '':
                                            print("\t Vaccine: ", center["vaccine"])
                                        else:
                                            center["vaccine"] = 'Unknown'
                                        # Creating text to send to telegram
                                    txt = f'On:{INP_DATE}\n' \
                                          f'{center["district_name"]}\n' \
                                          f'{center["name"]}\n' \
                                          f'<b>{center["pincode"]}</b>\n' \
                                          f'{center["min_age_limit"]}\n' \
                                          f'<b>Amount: {p_fee}\n</b>' \
                                          f'1st Dose: {center["available_capacity_dose1"]}\n' \
                                          f'2nd Dose: {center["available_capacity_dose2"]}\n' \
                                          f'<b>Vaccine: {center["vaccine"]}</b>\n\nhttps://selfregistration.cowin.gov.in'

                                    to_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.\
                                        format(token, chat_id, txt)

                                    if telegramFlag == 'y' or telegramFlag == 'Y':
                                        # Telegram API hit URL
                                        resp = requests.get(to_url)
                                    #print(to_url)
                    else:
                        print("No available slots on {}".format(INP_DATE))
    time.sleep(140)
    #   timing the loop
    now = time.time()
    print("\n**********************************************************************\n "
          "It has been {} seconds since the loop started. "
          "Current time: {}".format((now - loop_starts),datetime.datetime.today()))