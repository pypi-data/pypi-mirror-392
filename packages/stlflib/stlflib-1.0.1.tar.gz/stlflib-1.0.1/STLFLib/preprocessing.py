from .dependency import *

def get_type_day(df):
    
    '''
    SYNOPSYS: Функция кодирования типа дня на основании столбца df.Date формата DataTime. 
    Кодирование выполняется на основании производственного календаря республики Татарстан
    Признак 'TypeDay' кодируется по принципу label encoder:
    0 – рабочий (workdays)
    1 – предпраздничный (pre_holidays)
    2 – праздничный (holidays)
    3 – выходной (weekend)

    KEYWORD ARGUMENTS:
    df -- объект типа pandas.core.frame.DataFrame
    
    WARNING:
    Аргумент df должен обязательно содержать колонку 'Date' с данными типа datetime

    RETURNS:
    TypeDay : Literal[0, 1, 3, 2]
    
    EXAMPLES:
    >>> df['TypeDay'] = df.apply(get_type_day, axis=1)
    '''
    
    # перечень всех выходных и праздничных дней в Татарстане с 2013 по 2025 годы
    holidays = [
                datetime(2013, 1, 1).date(), datetime(2013, 1, 2).date(), datetime(2013, 1, 3).date(), datetime(2013, 1, 4).date(), datetime(2013, 1, 5).date(), datetime(2013, 1, 6).date(), datetime(2013, 1, 7).date(), datetime(2013, 1, 8).date(), datetime(2013, 2, 23).date(), datetime(2013, 3, 8).date(), datetime(2013, 5, 1).date(), datetime(2013, 5, 9).date(), datetime(2013, 6, 12).date(), datetime(2013, 8, 8).date(), datetime(2013, 8, 30).date(), datetime(2013, 10, 15).date(), datetime(2013, 11, 4).date(), datetime(2013, 11, 6).date(),
                datetime(2014, 1, 1).date(), datetime(2014, 1, 2).date(), datetime(2014, 1, 3).date(), datetime(2014, 1, 4).date(), datetime(2014, 1, 5).date(), datetime(2014, 1, 6).date(), datetime(2014, 1, 7).date(), datetime(2014, 1, 8).date(), datetime(2014, 2, 23).date(), datetime(2014, 3, 8).date(), datetime(2014, 5, 1).date(), datetime(2014, 5, 9).date(), datetime(2014, 6, 12).date(), datetime(2014, 7, 28).date(), datetime(2014, 8, 30).date(), datetime(2014, 10, 4).date(), datetime(2014, 11, 4).date(), datetime(2014, 11, 6).date(),
                datetime(2015, 1, 1).date(), datetime(2015, 1, 2).date(), datetime(2015, 1, 3).date(), datetime(2015, 1, 4).date(), datetime(2015, 1, 5).date(), datetime(2015, 1, 6).date(), datetime(2015, 1, 7).date(), datetime(2015, 1, 8).date(), datetime(2015, 2, 23).date(), datetime(2015, 3, 8).date(), datetime(2015, 5, 1).date(), datetime(2015, 5, 9).date(), datetime(2015, 6, 12).date(), datetime(2015, 7, 17).date(), datetime(2015, 8, 30).date(), datetime(2015, 9, 24).date(), datetime(2015, 11, 4).date(), datetime(2015, 11, 6).date(),
                datetime(2016, 1, 1).date(), datetime(2016, 1, 2).date(), datetime(2016, 1, 3).date(), datetime(2016, 1, 4).date(), datetime(2016, 1, 5).date(), datetime(2016, 1, 6).date(), datetime(2016, 1, 7).date(), datetime(2016, 1, 8).date(), datetime(2016, 2, 23).date(), datetime(2016, 3, 8).date(), datetime(2016, 5, 1).date(), datetime(2016, 5, 9).date(), datetime(2016, 6, 12).date(), datetime(2016, 7, 5).date(), datetime(2016, 8, 30).date(), datetime(2016, 9, 12).date(), datetime(2016, 11, 4).date(), datetime(2016, 11, 6).date(),
                datetime(2017, 1, 1).date(), datetime(2017, 1, 2).date(), datetime(2017, 1, 3).date(), datetime(2017, 1, 4).date(), datetime(2017, 1, 5).date(), datetime(2017, 1, 6).date(), datetime(2017, 1, 7).date(), datetime(2017, 1, 8).date(), datetime(2017, 2, 23).date(), datetime(2017, 3, 8).date(), datetime(2017, 5, 1).date(), datetime(2017, 5, 9).date(), datetime(2017, 6, 12).date(), datetime(2017, 6, 25).date(), datetime(2017, 8, 30).date(), datetime(2017, 9, 1).date(), datetime(2017, 11, 4).date(), datetime(2017, 11, 6).date(),
                datetime(2018, 1, 1).date(), datetime(2018, 1, 2).date(), datetime(2018, 1, 3).date(), datetime(2018, 1, 4).date(), datetime(2018, 1, 5).date(), datetime(2018, 1, 6).date(), datetime(2018, 1, 7).date(), datetime(2018, 1, 8).date(), datetime(2018, 2, 23).date(), datetime(2018, 3, 8).date(), datetime(2018, 5, 1).date(), datetime(2018, 5, 9).date(), datetime(2018, 6, 12).date(), datetime(2018, 6, 15).date(), datetime(2018, 8, 21).date(), datetime(2018, 8, 30).date(), datetime(2018, 11, 4).date(), datetime(2018, 11, 6).date(),
                datetime(2019, 1, 1).date(), datetime(2019, 1, 2).date(), datetime(2019, 1, 3).date(), datetime(2019, 1, 4).date(), datetime(2019, 1, 5).date(), datetime(2019, 1, 6).date(), datetime(2019, 1, 7).date(), datetime(2019, 1, 8).date(), datetime(2019, 2, 23).date(), datetime(2019, 3, 8).date(), datetime(2019, 5, 1).date(), datetime(2019, 5, 9).date(), datetime(2019, 6, 4).date(), datetime(2019, 6, 12).date(), datetime(2019, 8, 11).date(), datetime(2019, 8, 30).date(), datetime(2019, 11, 4).date(), datetime(2019, 11, 6).date(),
                datetime(2020, 1, 1).date(), datetime(2020, 1, 2).date(), datetime(2020, 1, 3).date(), datetime(2020, 1, 4).date(), datetime(2020, 1, 5).date(), datetime(2020, 1, 6).date(), datetime(2020, 1, 7).date(), datetime(2020, 1, 8).date(), datetime(2020, 2, 23).date(), datetime(2020, 3, 8).date(), datetime(2020, 5, 1).date(), datetime(2020, 5, 9).date(), datetime(2020, 5, 24).date(), datetime(2020, 6, 12).date(), datetime(2020, 7, 31).date(), datetime(2020, 8, 30).date(), datetime(2020, 11, 4).date(), datetime(2020, 11, 6).date(),
                datetime(2021, 1, 1).date(), datetime(2021, 1, 2).date(), datetime(2021, 1, 3).date(), datetime(2021, 1, 4).date(), datetime(2021, 1, 5).date(), datetime(2021, 1, 6).date(), datetime(2021, 1, 7).date(), datetime(2021, 1, 8).date(), datetime(2021, 2, 23).date(), datetime(2021, 3, 8).date(), datetime(2021, 5, 1).date(), datetime(2021, 5, 9).date(), datetime(2021, 5, 13).date(), datetime(2021, 6, 12).date(), datetime(2021, 7, 20).date(), datetime(2021, 8, 30).date(), datetime(2021, 11, 4).date(), datetime(2021, 11, 4).date(),
                datetime(2022, 1, 1).date(), datetime(2022, 1, 2).date(), datetime(2022, 1, 3).date(), datetime(2022, 1, 4).date(), datetime(2022, 1, 5).date(), datetime(2022, 1, 6).date(), datetime(2022, 1, 7).date(), datetime(2022, 1, 8).date(), datetime(2022, 2, 23).date(), datetime(2022, 3, 8).date(), datetime(2022, 5, 1).date(), datetime(2022, 5, 2).date(), datetime(2022, 5, 9).date(), datetime(2022, 6, 12).date(), datetime(2022, 7, 9).date(), datetime(2022, 8, 30).date(), datetime(2022, 11, 4).date(), datetime(2022, 11, 6).date(),
                datetime(2023, 1, 1).date(), datetime(2023, 1, 2).date(), datetime(2023, 1, 3).date(), datetime(2023, 1, 4).date(), datetime(2023, 1, 5).date(), datetime(2023, 1, 6).date(), datetime(2023, 1, 7).date(), datetime(2023, 1, 8).date(), datetime(2023, 2, 23).date(), datetime(2023, 3, 8).date(), datetime(2023, 4, 21).date(), datetime(2023, 5, 1).date(), datetime(2023, 5, 9).date(), datetime(2023, 6, 12).date(), datetime(2023, 6, 28).date(), datetime(2023, 8, 30).date(), datetime(2023, 11, 4).date(), datetime(2023, 11, 6).date(),
                datetime(2024, 1, 1).date(), datetime(2024, 1, 2).date(), datetime(2024, 1, 3).date(), datetime(2024, 1, 4).date(), datetime(2024, 1, 5).date(), datetime(2024, 1, 6).date(), datetime(2024, 1, 7).date(), datetime(2024, 1, 8).date(), datetime(2024, 2, 23).date(), datetime(2024, 3, 8).date(), datetime(2024, 4, 10).date(), datetime(2024, 5, 1).date(), datetime(2024, 5, 9).date(), datetime(2024, 6, 12).date(), datetime(2024, 6, 16).date(), datetime(2024, 8, 30).date(), datetime(2024, 11, 4).date(), datetime(2024, 11, 6).date(),
                datetime(2025, 1, 1).date(), datetime(2025, 1, 2).date(), datetime(2025, 1, 3).date(), datetime(2025, 1, 4).date(), datetime(2025, 1, 5).date(), datetime(2025, 1, 6).date(), datetime(2025, 1, 7).date(), datetime(2025, 1, 8).date(), datetime(2025, 2, 23).date(), datetime(2025, 3, 8).date(), datetime(2025, 3, 30).date(), datetime(2025, 5, 1).date(), datetime(2025, 5, 9).date(), datetime(2025, 6, 6).date(), datetime(2025, 6, 12).date(), datetime(2025, 8, 30).date(), datetime(2025, 11, 4).date(), datetime(2025, 11, 6).date(),
                datetime(2026, 1, 1).date(), datetime(2026, 1, 2).date(), datetime(2026, 1, 3).date(), datetime(2026, 1, 4).date(), datetime(2026, 1, 5).date(), datetime(2026, 1, 6).date(), datetime(2026, 1, 7).date(), datetime(2026, 1, 8).date(), datetime(2026, 2, 23).date(), datetime(2026, 3, 8).date(), datetime(2026, 3, 20).date(), datetime(2026, 5, 1).date(), datetime(2026, 5, 9).date(), datetime(2026, 5, 27).date(), datetime(2026, 6, 12).date(), datetime(2026, 8, 30).date(), datetime(2026, 11, 4).date(), datetime(2026, 11, 6).date(), 
               ]
    
    weekend = [
               datetime(2013, 5, 2).date(), datetime(2013, 5, 3).date(), datetime(2013, 5, 10).date(),
               datetime(2014, 3, 10).date(), datetime(2014, 5, 2).date(), datetime(2014, 6, 13).date(), datetime(2014, 9, 1).date(), datetime(2014, 10, 6).date(), datetime(2014, 11, 3).date(), 
               datetime(2015, 1, 9).date(), datetime(2015, 3, 9).date(), datetime(2015, 5, 4).date(), datetime(2015, 5, 11).date(), datetime(2015, 8, 31).date(),
               datetime(2016, 2, 22).date(), datetime(2016, 3, 7).date(), datetime(2016, 5, 2).date(), datetime(2016, 5, 3).date(), datetime(2016, 6, 13).date(), datetime(2016, 11, 7).date(),
               datetime(2017, 2, 24).date(), datetime(2017, 5, 8).date(),
               datetime(2018, 3, 9).date(), datetime(2018, 4, 30).date(), datetime(2018, 5, 2).date(), datetime(2018, 6, 11).date(), datetime(2018, 11, 5).date(), datetime(2018, 12, 31).date(),
               datetime(2019, 5, 2).date(), datetime(2019, 5, 3).date(), datetime(2019, 5, 10).date(),
               datetime(2020, 2, 24).date(), datetime(2020, 3, 9).date(), datetime(2020, 5, 4).date(), datetime(2020, 5, 5).date(), datetime(2020, 5, 11).date(),
               datetime(2021, 2, 22).date(), datetime(2021, 5, 3).date(), datetime(2021, 5, 10).date(), datetime(2021, 6, 14).date(), datetime(2021, 11, 5).date(), datetime(2021, 12, 31).date(),
               datetime(2022, 3, 7).date(), datetime(2022, 5, 3).date(), datetime(2022, 5, 10).date(), datetime(2022, 6, 13).date(),
               datetime(2023, 2, 24).date(), datetime(2023, 5, 8).date(),
               datetime(2024, 4, 29).date(), datetime(2024, 4, 30).date(), datetime(2024, 5, 10).date(), datetime(2024, 12, 30).date(), datetime(2024, 12, 31).date(),
               datetime(2025, 5, 2).date(), datetime(2025, 5, 8).date(), datetime(2025, 6, 13).date(), datetime(2025, 11, 3).date(), datetime(2025, 12, 31).date(),
               datetime(2026, 1, 9).date(), datetime(2026, 3, 9).date(), datetime(2026, 5, 11).date(), datetime(2026, 12, 31).date(),
              ]
    
    pre_holidays = [
                    datetime(2013, 2, 22).date(), datetime(2013, 3, 7).date(), datetime(2013, 4, 30).date(), datetime(2013, 5, 8).date(), datetime(2013, 6, 11).date(), datetime(2013, 8, 7).date(), datetime(2013, 8, 29).date(), datetime(2013, 10, 14).date(), datetime(2013, 11, 5).date(), datetime(2013, 12, 31).date(),
                    datetime(2014, 2, 24).date(), datetime(2014, 3, 7).date(), datetime(2014, 4, 30).date(), datetime(2014, 5, 8).date(), datetime(2014, 6, 11).date(), datetime(2014, 8, 29).date(), datetime(2014, 10, 3).date(), datetime(2014, 11, 5).date(), datetime(2014, 12, 31).date(),
                    datetime(2015, 4, 30).date(), datetime(2015, 5, 8).date(), datetime(2015, 6, 11).date(), datetime(2015, 7, 16).date(), datetime(2015, 9, 23).date(), datetime(2015, 11, 3).date(), datetime(2015, 11, 5).date(), datetime(2015, 12, 31).date(),
                    datetime(2016, 2, 20).date(), datetime(2016, 7, 4).date(), datetime(2016, 8, 29).date(), datetime(2016, 11, 3).date(),
                    datetime(2017, 2, 22).date(), datetime(2017, 3, 7).date(), datetime(2017, 8, 29).date(), datetime(2017, 8, 31).date(), datetime(2017, 11, 3).date(),            
                    datetime(2018, 2, 22).date(), datetime(2018, 3, 7).date(), datetime(2018, 4, 28).date(), datetime(2018, 5, 8).date(), datetime(2018, 6, 9).date(), datetime(2018, 6, 14).date(), datetime(2018, 7, 20).date(), datetime(2018, 7, 29).date(), datetime(2018, 12, 29).date(),
                    datetime(2019, 2, 22).date(), datetime(2019, 3, 7).date(), datetime(2019, 4, 30).date(), datetime(2019, 5, 8).date(), datetime(2019, 6, 3).date(), datetime(2019, 6, 11).date(), datetime(2019, 8, 29).date(), datetime(2019, 11, 5).date(), datetime(2019, 12, 31).date(),
                    datetime(2020, 4, 30).date(), datetime(2020, 5, 8).date(), datetime(2020, 6, 11).date(), datetime(2020, 7, 30).date(), datetime(2020, 11, 3).date(), datetime(2020, 11, 5).date(), datetime(2020, 12, 31).date(),
                    datetime(2021, 2, 20).date(), datetime(2021, 4, 30).date(), datetime(2021, 5, 12).date(), datetime(2021, 6, 11).date(), datetime(2021, 7, 19).date(), datetime(2021, 11, 3).date(),
                    datetime(2022, 2, 22).date(), datetime(2022, 3, 5).date(), datetime(2022, 7, 8).date(), datetime(2022, 8, 29).date(), datetime(2022, 11, 3).date(),
                    datetime(2023, 2, 22).date(), datetime(2023, 3, 7).date(), datetime(2023, 4, 20).date(),  datetime(2023, 6, 27).date(), datetime(2023, 8, 29).date(), datetime(2023, 11, 3).date(),
                    datetime(2024, 2, 22).date(), datetime(2024, 3, 7).date(), datetime(2024, 4, 9).date(), datetime(2024, 5, 8).date(), datetime(2024, 6, 11).date(), datetime(2024, 8, 29).date(), datetime(2024, 11, 2).date(), datetime(2024, 11, 5).date(),
                    datetime(2025, 3, 7).date(), datetime(2025, 4, 30).date(), datetime(2025, 6, 5).date(), datetime(2025, 6, 11).date(), datetime(2025, 8, 29).date(), datetime(2025, 11, 1).date(), datetime(2025, 11, 5).date(),
                    datetime(2026, 3, 19).date(), datetime(2026, 4, 30).date(), datetime(2026, 5, 8).date(), datetime(2026, 5, 26).date(), datetime(2026, 6, 11).date(), datetime(2026, 11, 3).date(), datetime(2026, 11, 5).date(),
                   ]
    
    workdays = [datetime(2024, 4, 27).date(), datetime(2024, 12, 28).date()]
    
    if df.Date.date() in workdays:
        TypeDay = 0
    elif df.Date.date() in pre_holidays:
        TypeDay = 1   
    elif df.Date.date() in weekend:
        TypeDay = 3 
    elif df.Date.date() in holidays:
        TypeDay = 2 
    elif (df.Weekday == 5) | (df.Weekday == 6):
        TypeDay = 3
    else:
        TypeDay = 0
    return TypeDay


def get_light(df):
    
    '''
    SYNOPSYS: Функция кодирования светового интервала на основании столбца df.Date формата DataTime. 
    Кодирование выполняется исходя из географического расположения города Казань
    Признак 'Light' кодируется по принципу label encoder:
    0 – темно (dark)
    1 – светло (hight)

    KEYWORD ARGUMENTS:
    df -- объект типа pandas.core.frame.DataFrame
    
    WARNING:
    Аргумент df должен обязательно содержать колонку 'Date' с данными типа datetime

    RETURNS:
    Literal[0, 1]
    
    EXAMPLES:
    >>> df['Light'] = df.apply(get_light, axis=1)
    '''
    
    # широта и долгота для Казани (источник: https://time-in.ru/coordinates/kazan)
    kazan = ephem.Observer()
    kazan.lat = '55.7887'
    kazan.lon = '49.1221'
    kazan.date = df.Date.date()
    
    # время восхода и заката солнца    
    sunrise = ephem.localtime(kazan.next_rising(ephem.Sun()))
    sunset = ephem.localtime(kazan.next_setting(ephem.Sun()))
    
    return int(sunrise < df.Date < sunset)


def get_season(df):

    '''
    SYNOPSYS: Функция кодирования сезонности на основании столбца df.Date формата DataTime.
    Признак 'Season' кодируется по принципу label encoder:
    0 – зима (winter)
    1 – весна (spring)
    2 – осень (autumn)
    3 – лето (summer)

    KEYWORD ARGUMENTS:
    df -- объект типа pandas.core.frame.DataFrame
    
    WARNING:
    Аргумент df должен обязательно содержать колонку 'Date' с данными типа datetime

    RETURNS:
    season : Literal[0, 1, 2, 3]
    
    EXAMPLES:
    >>> df['Season'] = df.apply(get_season, axis=1)
    '''
    
    winter, spring, summer, autumn = [1, 2, 12], [3, 4, 5], [6, 7, 8], [9, 10, 11]
    
    if df.Date.date().month in winter:
        season = 0
    elif df.Date.date().month in spring:
        season = 1
    elif df.Date.date().month in autumn:
        season = 2
    else:
        season = 3
    return season


def prepareData(df, lag_start=1, lag_end=7):

    '''
    SYNOPSYS: Функция препроцессинга данных. Препроцессинг включает:
    – добавление типа дня (0 - рабочий, 1 - предпраздничный, 2 - праздничный, 3 - выходной)
    – добавление светового периода (0 - темно, 1 - светло)
    – добавление сезонности (0 - зима, 1 - весна, 3 - лето, 2 - осень)
    - добавление суточного лага (по умолчанию lag-1...7)

    KEYWORD ARGUMENTS:
    df -- объект типа pandas.core.frame.DataFrame
    
    WARNING:
    - Аргумент df должен обязательно содержать колонку 'Date' с данными типа datetime
    - Суточный шифтинг колонки 'Volume' выполняется по индексу Date (после переиндексации), 
    из-за чего могут возникать ошибки при пропуске данных в оперативных сведениях.
    {Данная фича реализована намеренно, в качестве последнего предохранителя от возможных ошибок}
    - Первые 24*lag_end строк (168 записей для лага в 7 суток) удаляются из-за пропуска данных
    - Функция добавляет 'Light', 'Season' и 'TypeDay' в исходный датафрейм df
    ! Обязательно создавать поверхностную копию датафрейма: df.copy() !

    RETURNS:
    df : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> prepareData(df_general).info()

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 112560 entries, 0 to 112559
    Data columns (total 21 columns):
    #   Column       Non-Null Count   Dtype         
    ---  ------       --------------   -----         
    0   Date         112560 non-null  datetime64[ns]
    1   Year         112560 non-null  int64         
    2   Month        112560 non-null  int64         
    3   Day          112560 non-null  int64         
    4   Hour         112560 non-null  int64         
    5   Weekday      112560 non-null  int64         
    6   Volume       112560 non-null  float64       
    7   Temperature  112560 non-null  float64       
    8   ActCons      112560 non-null  int64         
    9   ActGen       112560 non-null  int64         
    10  Price        112560 non-null  int64         
    11  TypeDay      112560 non-null  int64         
    12  Light        112560 non-null  int64         
    13  Season       112560 non-null  int64         
    14  lag-1        112560 non-null  float64       
    15  lag-2        112560 non-null  float64       
    16  lag-3        112560 non-null  float64       
    17  lag-4        112560 non-null  float64       
    18  lag-5        112560 non-null  float64       
    19  lag-6        112560 non-null  float64       
    20  lag-7        112560 non-null  float64       
    dtypes: datetime64[ns](1), float64(9), int64(11)
    memory usage: 18.0 MB
    '''        
        
    # добавляем тип дня (0 - рабочий, 1 - выходной, 2 - предпраздничный)
    df['TypeDay'] = df.apply(get_type_day, axis=1)
    
    # определяем световой период (0 - темно, 1 - светло)
    df['Light'] = df.apply(get_light, axis=1)
    
    # добавляем фактор сезонности (0 - winter, 1 - spring, 3 - summer, 2 - autumn)
    df['Season'] = df.apply(get_season, axis=1)
    
    # превращаем столбец Date в индекс
    df = df.set_index('Date')
    
    # добавляем суточные лаги исходного ряда (по умолчанию 1 полная неделя)
    for i in range(lag_start, lag_end + 1):    
        df[f"lag-{i}"] = df.Volume.shift(freq=f"{i}D")  # делаем смещение на i-й день по индексу

    # удаляем первые 24*lag_end записей с пропусками данных (168 записей для лага в 7 суток)
    df = df.dropna(subset=['lag-1', 'lag-2', 'lag-3', 'lag-4', 'lag-5', 'lag-6', 'lag-7'])
    df.reset_index(inplace=True)

    return df