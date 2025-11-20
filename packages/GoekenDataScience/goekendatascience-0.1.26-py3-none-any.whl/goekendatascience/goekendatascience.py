import os
import pandas as pd
from datetime import date, timedelta
import yfinance as yf
import requests
import ast
from sqlalchemy import create_engine

class TickerDataFetch:

    def __init__(self):
        self.todays_date = str(date.today())
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_folder = os.path.join(self.script_dir, "Ticker Data")

    def folder_scan(self):
        os.makedirs(self.output_folder, exist_ok=True)
        self.List = os.listdir(self.output_folder)
        self.namelist = {}
        for item in self.List:
            if '.csv' not in item:
                self.List.remove(item)
        for item in self.List:
            ticker_name = item.split('.')[0].split()[0]
            ticker_date = item.split('.')[0].split()[1]
            self.namelist[ticker_name] = ticker_date

    def fetch_historical_data(self, ticker):
        ticker_data = yf.download(ticker, period='max')
        os.makedirs(self.output_folder, exist_ok=True)
        csv_path = os.path.join(self.output_folder, f"{ticker} {self.todays_date}.csv")
        DataFrame = pd.DataFrame(ticker_data)
        DataFrame.columns = ['Close','High','Low','Open','Volume']
        DataFrame = DataFrame[::-1]
        DataFrame = DataFrame.dropna()
        DataFrame.to_csv(csv_path,index=True,header=True)
        print(f"Saved CSV to: {csv_path}")

    def update_tickers (self,tickers): 
        self.folder_scan()
        for ticker in tickers:
            if ticker in self.namelist:
                if self.namelist[ticker] == self.todays_date:
                    print(ticker,"data found for",self.todays_date)
                else:
                    os.remove(os.path.join(self.output_folder, f"{ticker} {self.namelist[ticker]}.csv"))
                    self.fetch_historical_data(ticker)
                    print(ticker,"data found for",self.namelist[ticker],". Updating data for",self.todays_date)
            else:
                self.fetch_historical_data(ticker)
                print(ticker,"data not found",{ticker},". Updating data for",self.todays_date)
        for ticker in self.namelist:
            if ticker in tickers:
                pass
            else:
                os.remove(os.path.join(self.output_folder, f"{ticker} {self.namelist[ticker]}.csv"))
                print("Removed",ticker,".")
        self.folder_scan()

    def import_tickers(self):
        ticker_data = {}
        self.folder_scan()
        for ticker in self.namelist:
            data = pd.read_csv(os.path.join(self.output_folder, f"{ticker} {self.namelist[ticker]}.csv"))
            data.sort_index(ascending=False)
            data.set_index('Date',inplace=True)
            ticker_data[ticker] = data
        return ticker_data

class WeatherDataFetch:

    def __init__(self):
        self.todays_date = str(date.today())
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.daily_output_folder = os.path.join(self.script_dir, "Daily Weather Data")
        self.hourly_output_folder = os.path.join(self.script_dir, "Hourly Weather Data")
        os.makedirs(self.daily_output_folder, exist_ok=True)
        os.makedirs(self.hourly_output_folder, exist_ok=True)

    def folder_scan(self):
        self.List = os.listdir(self.daily_output_folder)
        for item in self.List:
            if '.csv' not in item:
                self.List.remove(item)
        self.namelist = {}
        for item in self.List:
            location_name = item.split('.')[0].split(';')[0]
            location_date = item.split('.')[0].split(';')[1]
            self.namelist[location_name] = location_date

    def build_weather_data(self, locations, date1=str(date.today()-timedelta(days=3)),date2=str(date.today()-timedelta(days=1))):
        for location in locations:
            self.folder_scan()
            daily_csv_path = os.path.join(self.daily_output_folder, f"{location};{self.todays_date}.csv")
            hourly_csv_path = os.path.join(self.hourly_output_folder, f"{location};{self.todays_date}.csv")
            
            def fetch_daily_weather_data(location,date1,date2):
                API_key_list = ['L47PTMRQVEJG8KJKMWBTL59PU','XBMH6Z8MYAJ4PVQKSVHA9WAHA','FHTPG24QT5CW2LASRD36UURDE','9UD2MMRS8D7FNEQFWSDE2QQFU','46HSRX26YUSMBN4GBGLSTNVN4','BCSXDCW5MD78U5WP2AQJ5M247']
                for i in API_key_list:
                    URL = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date1}/{date2}?key={i}'
                    response = requests.get(URL)
                    if response.status_code == 200:
                        data = response.json()
                        break
                    else:
                        print(response)
                        print(i,"key API limit reached. Trying next key . . .")
                if 'days' not in data:
                    print("API limit reached or network error occured.")
                new_weather_data = pd.DataFrame(data['days'])
                new_weather_data = new_weather_data[::-1]
                return new_weather_data

            def fetch_hourly_weather_data(location):
                hourly_weather_data = {}
                self.folder_scan()
                data = pd.read_csv(os.path.join(self.daily_output_folder, f"{location};{self.namelist[location]}.csv"))
                data.sort_index(ascending=False)
                data.set_index('datetime',inplace=True)
                data = data.iloc[:,-1]
                hourly_weather_data[location] = data.to_dict()
                hourly_weather_data_date_dict = {}
                for date in hourly_weather_data[location]:
                    hour_data = ast.literal_eval(hourly_weather_data[location][date])
                    hour_data_df = pd.DataFrame.from_dict(hour_data)
                    hour_data_df.set_index('datetime',inplace=True)
                    hour_data_df = hour_data_df.iloc[:,:-2][::-1]
                    hourly_weather_data_date_dict[date]= hour_data_df
                hourly_weather_data_date_df = pd.concat(hourly_weather_data_date_dict,axis=0)
                return hourly_weather_data_date_df

            if location in self.namelist:
                if self.namelist[location] != self.todays_date:
                    old_weather_data = pd.read_csv(os.path.join(self.daily_output_folder, f"{location};{self.namelist[location]}.csv"))
                    new_weather_data = fetch_daily_weather_data(location,date1,date2)
                    weather_data = pd.concat([old_weather_data,new_weather_data]).drop_duplicates()
                    os.remove(os.path.join(self.daily_output_folder, f"{location};{self.namelist[location]}.csv"))
                    weather_data.to_csv(daily_csv_path,index=True,header=True)
                    print(f"{location};{self.todays_date}.csv to: {daily_csv_path}")
                    new_weather_hourly_data = fetch_hourly_weather_data(location)
                    new_weather_hourly_data.to_csv(hourly_csv_path,index=True,header=True)

                else:
                    print(f"Current data for {location} found.")
                    new_weather_hourly_data = fetch_hourly_weather_data(location)
                    new_weather_hourly_data.to_csv(hourly_csv_path,index=True,header=True)
            else:
                new_weather_data = fetch_daily_weather_data(location,date1,date2)
                new_weather_data.to_csv(daily_csv_path,index=False,header=True)
                new_weather_hourly_data = fetch_hourly_weather_data(location)
                new_weather_hourly_data.to_csv(hourly_csv_path,index=True,header=True)
                print(f"{location};{self.todays_date}.csv to: {daily_csv_path}")
            
    def import_daily_weather_data(self):
        weather_data = {}
        self.folder_scan()
        for location in self.namelist:
            data = pd.read_csv(os.path.join(self.daily_output_folder, f"{location};{self.namelist[location]}.csv"))
            data.sort_index(ascending=False)
            data.set_index('datetime',inplace=True)
            weather_data[location] = data
        return weather_data

    def import_hourly_weather_data(self):
        self.folder_scan()
        hourly_weather_data ={}
        for location in self.namelist:
            hourly_data = pd.read_csv(os.path.join(self.hourly_output_folder, f"{location};{self.todays_date}.csv"),index_col=[0,1])
            hourly_weather_data[location] = hourly_data
        return hourly_weather_data

class CleanData:
    def remove_duplicate_columns(data):
        data = data.transpose()
        data = data.drop_duplicates()
        data = data.transpose()
        print('Dropped duplicate columns.')
        return data
        
class DataManipulation:
    def __init__(self):
        pass



    def csv_to_sql(self, folder_path):
        db_name = folder_path.split('\\')[-1]
        db_name = f'{db_name}.db'
        db_path = os.path.join(folder_path,db_name)
        engine = create_engine(f'sqlite:///{db_path}')
        file_list = os.listdir(folder_path)
        print
        for i in file_list:
            if '.csv' in i:
                df = pd.read_csv(os.path.join(folder_path, i))
                print(df)
                df.to_sql(i,engine,if_exists="replace")

    def target_creation(self,data,targets,shift=0):
        def creation(data,targets,shift):
            data_dict = {}
            recent_obs = data.iloc[0]
            target_data_dict = {}
            feature_data = data

            for target in targets:
                try:
                    if shift>0:
                        feature_data = data.iloc[shift:]                    
                        target_data = data[[target]].iloc[:-shift]
                        target_data.index = feature_data.index
                        target_data.rename(columns={target:f'{target} {shift} Ahead'},inplace=True)
                    elif shift<0:
                        feature_data = data.iloc[:shift]                    
                        target_data = data[[target]].iloc[-shift:]
                        feature_data.index = target_data.index
                        target_data.rename(columns={target:f'{target} {-shift} Behind'},inplace=True)
                    else:
                        feature_data = feature_data.drop(target, axis=1)
                        target_data = data[[target]]
                    target_data_dict[target] = target_data
                except:
                    print('Target',target,'does not exist in data')
                    print(feature_data.columns)
        
            data_dict['Feature Data'] = feature_data
            data_dict['Target Data'] = target_data_dict
            data_dict['Most Recent Observation'] = recent_obs
            return data_dict
        for i in data:
            data[i] = creation(data[i],targets,shift)
        return data

    def feature_engineering(self, feature_data, operations=['all']):
        if 'all' in operations:
            operations = [
                #Powers:
                'power 2', 'power 3', 'power 4', 'power 5',
                
                #Pairs
                'pair mult','pair div','pair add','pair sub'
                ]

        for i in feature_data:
            for operation in operations:
                list = operation.split()
                #powers
                powers = pd.DataFrame()
                if list[0] == 'power':
                    powers[f'Power {list[1]} {i}'] = feature_data[f'{i}']**float(list[1])
                    
                #pairs
                pairs = pd.DataFrame()
                if list[0] == 'pair':
                    for j in feature_data:
                        if list[1] == 'mult':
                            pairs[f'mult {i}-{j}'] = feature_data[f'{i}'] * feature_data[f'{j}']
                        if list[1] == 'div':
                            pairs[f'div {i}-{j}'] = feature_data[f'{i}'] / feature_data[f'{j}']
                        if list[1] == 'add':
                            pairs[f'{list[1]} {i}-{j}'] = feature_data[f'{i}'] + feature_data[f'{j}']
                        if list[1] == 'sub':
                            pairs[f'{list[1]} {i}-{j}'] = feature_data[f'{i}'] - feature_data[f'{j}']



            feature_data = pd.concat([feature_data,powers,pairs],axis=1)

        print(feature_data)



