import os
import datetime
import urllib.request

import glob

import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plot
from spyre import server

def download_file(i, year1, year2):
    time_now = datetime.datetime.now()
    date_now = datetime.date.today()

    files = glob.glob('*.csv') 
        
    filename = f"{i}___{date_now.year}_{date_now.month}_{date_now.day}___{time_now.hour}_{time_now.minute}.csv"

    isExists = False
    for file in files:
        if file.startswith(f"{i}___"):
            isExists = True

    if isExists:
        print(f"VHI {i} exists in {filename}")        
    else:
        vhi_url = urllib.request.urlopen(f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={i}&year1={year1}&year2={year2}&type=Mean")

        with open(filename, 'wb') as out:
            out.write(vhi_url.read())

        print(f"VHI {i} is downloaded...")

year1 = 2000
year2 = 2020

for i in range (1,28):
    download_file(i, year1, year2)

def make_dataframe(path:str = "D:\\KPI\\DataAnalys\\Lab3"):
    frames = []
    headers = ["Year", "Week", "SMN", "SMT", "VCI", "TCI", "VHI", "empty"]

    #Отримуємо всі csv файли в каталозі
    files = glob.glob(path + '/*.csv') 

    for file in files:
        file = file.replace(f"{path}\\", "")
        province = int(file.split("_")[0])

        df = pd.read_csv(file, header=1, names = headers)
        df = df.drop(df.index[-1])
        
        #Конвертація років та тижнів в Integer, потрібно для процедур, де потрібно порівняти ці значення
        df.at[0, "Year"] = df.at[0, "Year"][9:] #Виправлення першого рядка
        df["Year"] = df["Year"].astype(int)
        df["Week"] = df["Week"].astype(int)

        df.insert(0, "pID", province, True)
        df = df.drop("empty", axis=1)
                
        frames.append(df)

    df = pd.concat(frames).drop_duplicates().reset_index(drop=True)

    #12 - Київ, 20 - Севастополь
    df = df.loc[(df.pID != 12) & (df.pID != 20)]

    return df

def set_new_pid(dataframe):
    ids = {
        1: 22, # Черкаська
        2: 24, # Чернігівська
        3: 23, # Чернівецька
        4: 25, # Крим
        5: 3, # Дніпропетровська
        6: 4, # Донецька
        7: 8, # Івано-Франківська
        8: 19, # Харківська 
        9: 20, # Херсонська
        10: 21, # Хмельницька
        11: 9, # Київська
        13: 10, # Кіровоградська
        14: 11, # Луганська
        15: 12, # Львівська
        16: 13, # Миколаївська
        17: 14, # Одеська
        18: 15, # Полтавська
        19: 16, # Рівненська
        21: 17, # Сумська
        22: 18, # Терноспільська
        23: 6, # Закарпатська
        24: 1, # Віницька 
        25: 2, # Волинська
        26: 7, # Запорізька
        27: 5 # Житомирська 
    }

    df = dataframe.copy()
    df["pID"] = df["pID"].replace(ids)
    return df 

p_names = {
    1: 'Вінницька', 
    2: 'Волинська', 
    3: 'Дніпропетровська', 
    4: 'Донецька', 
    5: 'Житомирська', 
    6: 'Закарпатська', 
    7: 'Запорізька', 
    8: 'Івано-Франківська', 
    9: 'Київська', 
    10: 'Кіровоградська', 
    11: 'Луганська', 
    12: 'Львівська', 
    13: 'Миколаївська', 
    14: 'Одеська', 
    15: 'Полтавська',
    16: 'Рівенська', 
    17: 'Сумська', 
    18: 'Тернопільська', 
    19: 'Харківська', 
    20: 'Херсонська', 
    21: 'Хмельницька',
    22: 'Черкаська', 
    23: 'Чернівецька', 
    24: 'Чернігівська', 
    25: 'Республіка Крим'
}


class WebApp(server.App):
    title = "Лабораторна робота 3"

    inputs = [{
        "type": "dropdown",
        "label": "Select Data",
        "options": [
            {"label": "VHI",
            "value": "VHI"},

            {"label": "VCI",
            "value": "VCI"},

            {"label": "TCI",
            "value": "TCI"}
        ],
        "key": "index",
        "action_id": "update_data"
    },

    {
        "type": "dropdown",
        "label": "Select Province",
        "options": [{"label": f"{p_names[pid]}", "value": pid} 
                   for pid in range(1, 26) if pid not in [12, 20]],
        
        "key": "pid",
        "action_id": "update_data"
    },
    
    {
        "type": 'text',
        "key": 'wrange',
        "label": 'Week Range (1 52)',
        "value": '1 52',
        "action_id": 'update_data'
    }, 

    {
        "type": 'text',
        "key": 'yrange',
        "label": 'Year Range (2000 2010)',
        "value": 'none',
        "action_id": 'update_data'
    },
    {
        "type": "simple",
        "label": 'Submit',
        "key": 'submit_button',
        "id": "update_data"
    }
    ]

    controls = [{
        "type": "button",
        "label": "Select",
        "id": "update_data"
    }
    ]

    tabs = ["Table", "Plot"]
    outputs = [
        {
            "type": "table",
            "id": "table",
            "tab": "Table",
            "control_id": "update_data"
        },
        
        {
            "type": "plot",
            "id": "plot",
            "tab": "Plot",
            "control_id": "update_data"
        }
    ]

    def getData(self, args):
        index = args["index"]
        pid = args.get("pid", None)

        df = make_dataframe()
        df = set_new_pid(df)
        weeks = args["wrange"].split(" ")
        years = args["yrange"]

        df = df[(df["Week"] >= int(weeks[0]) ) & (df["Week"] <= int(weeks[1]) )]

        if years != "none":
            years = years.split(" ")

            df = df[(df["Year"] >= int(years[0])) & (df["Year"] <= int(years[1]))]

        if pid is not None:
            pid = int(pid)
            df = df[df["pID"] == pid]

            df.insert(0, "Province", p_names[pid], True)
            df = df.drop("pID", axis=1)

        return df[['Province', "Year", "Week", index]]



    def getPlot(self, args):
        df = self.getData(args)
        
        index_ = args["index"]
        pid = int(args["pid"])
        pname = p_names[pid]
        years = args["yrange"]

        if years != "none":
            years = years.split(" ")
            yrange = f"{years[0]} - {years[1]}"

        else:
            yrange = "No years range"

        plot.figure(figsize=(10, 15))
        plot.subplot(2, 1, 1)
        sns.heatmap(df.pivot(index = "Year", columns="Week", values=index_), cmap="viridis", cbar_kws={"label": index_}, linewidths=0.5)
        plot.title(f"{index_} heatmap for {pname} область | Years: {yrange}")
        plot.xlabel("Week")
        plot.ylabel("Year")

        plot.subplot(2, 1, 2)

        avgs = df.groupby("Year")[index_].mean()
        plot.barh(df["Year"].unique().astype(int), avgs)
        plot.title(f"Average {index_} by years for {p_names[pid]} область")
        plot.xlabel(f"Average {index_}")
        plot.ylabel("Years")
        plot.yticks(df["Year"].unique().astype(int))
        plot.grid(True)
        

        return plot.gcf()
    
web = WebApp()
web.launch()