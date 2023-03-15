import re
import json
import time
import csv
import threading
import schedule
from urllib.request import urlopen
from datetime import datetime, timedelta
from bs4 import BeautifulSoup



def get_kandilli_data():
    array = []
    data = urlopen('http://www.koeri.boun.edu.tr/scripts/sondepremler.asp').read()
    soup = BeautifulSoup(data, 'html.parser')
    data = soup.find_all('pre')
    data = str(data).strip().split('--------------')[2]

    data = data.split('\n')
    data.pop(0)
    data.pop()
    data.pop()
    for index in range(len(data)):
        element = str(data[index].rstrip())
        element = re.sub(r'\s\s\s', ' ', element)
        element = re.sub(r'\s\s\s\s', ' ', element)
        element = re.sub(r'\s\s', ' ', element)
        element = re.sub(r'\s\s', ' ', element)
        Args=element.split(' ')
        location = Args[8]+element.split(Args[8])[len(element.split(Args[8])) - 1].split('İlksel')[0].split('REVIZE')[0]

        data_dict = {
            "id": index+1,
            "Tarih": Args[0]+" "+Args[1],
            "Saat": int(datetime.strptime(Args[0]+" "+Args[1], "%Y.%m.%d %H:%M:%S").timestamp()),
            "Enlem(N)": float(Args[2]),
            "Boylam(E)": float(Args[3]),
            "Derinlik(km)": float(Args[4]),
            "MD": float(Args[5].replace('-.-', '0')),
            "ML": float(Args[6].replace('-.-', '0')),
            "MW": float(Args[7].replace('-.-', '0')),
            "Yer": location.strip(),
            "Çözüm Niteliği": element.split(location)[1].split()[0]
        }

        array.append(data_dict)

    # Write the data to a CSV file
    with open('kandilli_data.csv', mode='w', newline='') as csv_file:
        fieldnames = ['id', 'Tarih', 'Saat', 'Enlem(N)', 'Boylam(E)', 'Derinlik(km)', 'MD', 'ML', 'MW', 'Yer', 'Çözüm Niteliği']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for data_dict in array:
            writer.writerow(data_dict)

    return array


def get_afad_data():
    
    # Veri güncellemesi sırasında zamanı yazdırmak için
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    
    array = []
    data = urlopen('https://deprem.afad.gov.tr/last-earthquakes.html').read()
    soup = BeautifulSoup(data, 'html.parser')
    data = soup.find_all('tr')
    data.pop(0)
    
    with open('afad_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'Tarih', 'Saat', 'Enlem(N)', 'Boylam(E)', 'Derinlik(km)', 'MD', 'ML', 'MW', 'Yer', 'afad_id', 'Çözüm Niteliği'])

        for i in range(len(data)):
            earthquakeType = data[i].find_all('td')[4].text

            row = [
                i+1,
                data[i].find_all('td')[0].text,
                int(datetime.strptime(data[i].find_all('td')[0].text, "%Y-%m-%d %H:%M:%S").timestamp()),
                float(data[i].find_all('td')[1].text),
                float(data[i].find_all('td')[2].text),
                float(data[i].find_all('td')[3].text),
                float(data[i].find_all('td')[5].text) if earthquakeType == "MD" else  0,
                float(data[i].find_all('td')[5].text) if earthquakeType == "ML" else 0,
                float(data[i].find_all('td')[5].text) if earthquakeType == "MW" else 0,
                data[i].find_all('td')[6].text,
                data[i].find_all('td')[7].text,
                earthquakeType
            ]

            writer.writerow(row)
            array.append(row)
    print(f'{current_time}: AFAD data has appended.')
    return array


def job():
    global kandilliData
    global afadData
    afadData = get_afad_data()
    kandilliData = get_kandilli_data()

job()
schedule.every(1).minutes.do(job)

def thread_function():
    while True:
        schedule.run_pending()
        time.sleep(1)

x = threading.Thread(target=thread_function)
x.start()