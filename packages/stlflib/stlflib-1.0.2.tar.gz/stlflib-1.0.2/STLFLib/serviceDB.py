from .dependency import *

#-------------------------------create DB--------------------------------- 

def generate_volume_df(path):
    
    '''
    SYNOPSYS: Функция генерации датафрейма с архивными данными энергопотребления 
    из предварительно подготовленных xls-файлов, расположенных в директории path

    KEYWORD ARGUMENTS:
    path -- директория с архивными данными энергопотребления
    
    WARNING:
    Директория 'path' должна содержать подкаталоги вида '{год}г' (например '2025г') с файлами вида '{месяц}.xls' 
    (например 'январь.xls')

    RETURNS:
    total_volume_df : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> generate_volume_df(path='_raw_Data_TatEnergosbyt').info()
    
    <class 'pandas.core.frame.DataFrame'>
    Index: 112488 entries, 0 to 743
    Data columns (total 7 columns):
     #   Column   Non-Null Count   Dtype         
    ---  ------   --------------   -----         
     0   Date     112488 non-null  datetime64[ns]
     1   Year     112488 non-null  int32         
     2   Month    112488 non-null  int32         
     3   Day      112488 non-null  int32         
     4   Hour     112488 non-null  int32         
     5   Weekday  112488 non-null  int32         
     6   Volume   112488 non-null  float64       
    dtypes: datetime64[ns](1), float64(1), int32(5)
    memory usage: 4.7 MB
    None
    '''
    
    # получаем перечень всех папок из директории path
    folders = list(folder for folder in os.listdir(path))

    # получаем список месяцев на русском языке
    locale.setlocale(locale.LC_TIME, 'ru_RU')
    months = list(name.lower() for name in calendar.month_name if name != '')

    # создаём датафрейм с данными об энергопотреблении
    total_volume_df = pd.DataFrame()

    # выгружаем данные из директории path
    for folder in folders:
        for month in months:

            try:
                # получаем данные из единичного *.xls файла
                volume_df_raw = pd.read_excel(f'{path}/{folder}/{month}.xls', index_col=0)

                # соединяем (горизонтально) две половины таблицы (верхнюю и нижнюю)
                volume_df_raw = pd.concat([volume_df_raw[6:6+24], volume_df_raw[-3-24:-3]], sort=False, axis=1)

                # удаляем "пустые" столбцы (заполненные NaN-ами)
                volume_df_raw.dropna(axis='columns', how='all', inplace=True)

                # в качестве имени столбцов назначаем порядковый номер дня месяца 
                volume_df_raw.columns = list(i for i in range(1, volume_df_raw.shape[1]+1))

                # сбрасываем индекс
                volume_df_raw.reset_index(drop=True, inplace=True)

                # создаём и заполняем фрагмент итоговой таблицы
                volume_df = pd.DataFrame(columns=['Date', 'Year', 'Month', 'Day', 'Hour', 'Weekday', 'Volume'])     

                volume_df.Volume = np.array([value for name, value in volume_df_raw.items()]).ravel()
                volume_df.Volume = volume_df.Volume.astype(float)
                volume_df.Day = pd.Series(list(i for i in range(1, volume_df_raw.shape[1] + 1) for _ in range(24)))
                volume_df.Hour = pd.Series(list(i for i in range(1, 25)) * volume_df_raw.shape[1])        
                volume_df.Month = months.index(month) + 1
                volume_df.Year = int(folder[:-1])

                # добавляем категориальный признак "день недели"
                volume_df.Date = pd.to_datetime(volume_df[['Year', 'Month', 'Day', 'Hour']])
                volume_df.Hour = volume_df.Date.dt.hour  # унифицируем 24-й час под DataTime-объект
                volume_df.Day = volume_df.Date.dt.day  # устраняем ошибку, при которой 0-й час перебрасывается_
                volume_df.Month = volume_df.Date.dt.month  # в предыдущие сутки
                volume_df.Year = volume_df.Date.dt.year
                volume_df.Weekday = volume_df.Date.dt.weekday

                # сшиваем полученный фрагмент с итоговой таблицей
                total_volume_df = pd.concat([total_volume_df, volume_df])

            except FileNotFoundError:  # отрабатываем ситуацию неполного года
                continue
    return total_volume_df


def get_weather(date):
    
    '''
    SYNOPSYS: Функция генерации архива/прогноза погоды (температуры наружного воздуха) на указанную дату
    с частотой дискретизации в 1 ч

    KEYWORD ARGUMENTS:
    date -- дата запроса в формате datetime
    
    WARNING:
    Аргумент date должен соответствовать формату: datetime(year,month,day)
    При использовании готовых конструкций datetime провести преобразование типа: datetime.date()

    RETURNS:
    day_weather_df : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> get_weather(datetime.now().date() - timedelta(days=1)).head(5)
    
        Date	                Temperature
    1	2025-11-10 01:00:00	    1.9
    2	2025-11-10 02:00:00	    2.3
    3	2025-11-10 03:00:00	    3.0
    4	2025-11-10 04:00:00	    3.8
    5	2025-11-10 05:00:00	    4.5
    
    >>> get_weather(datetime(2015,5,3)).info()
    
    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 24 entries, 1 to 24
    Data columns (total 2 columns):
    #   Column       Non-Null Count  Dtype         
    ---  ------       --------------  -----         
    0   Date         24 non-null     datetime64[ns]
    1   Temperature  24 non-null     float64       
    dtypes: datetime64[ns](1), float64(1)
    memory usage: 516.0 bytes
    '''
    
    months = ['', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']  # названия месяцев в родительном падеже
            
    while True:  # повторяем запрос до тех пор, пока не получим положительный HTTP-ответ от сервера
        try:
            # выгружаем содержимое страницы https://kazan.nuipogoda.ru/ в переменную
            page = requests.get(url=f'https://kazan.nuipogoda.ru/{date.day}-{months[date.month]}#{date.year}', timeout=10)
            page.raise_for_status()  # Проверяем на HTTP ошибки
            break
        except requests.exceptions.RequestException as error:  # Ловим все ошибки requests
            print(f'{error} for {date}')
            
    # сохраняем html-код страницы в переменную
    soup = BeautifulSoup(page.text, 'html.parser')

    # фильтруем теги с температурой
    trs = soup.find_all('tr', time=re.compile(r'[0-9]'))

    # получаем "сырые" данные
    day_weather_df = list()

    for tr in trs:
        day_weather_df.append((list(tr.attrs.values())[0], tr.find('span', class_='ht').text[:-1]))

    # формируем интерпретируемый датафрейм
    day_weather_df = pd.DataFrame(day_weather_df, columns=['Date', 'Temperature']).astype('int64')
    day_weather_df.Date = pd.to_datetime(day_weather_df.Date, unit='ms')
    
    if (date.day == 31 and date.month == 12):  # кастыль для перехода на следующий год
        day_weather_df = day_weather_df[((day_weather_df.Date.dt.year == date.year) &
                                        (day_weather_df.Date.dt.month == date.month)) | 
                                        (day_weather_df.Date == datetime.combine(date + timedelta(days=1), time(hour=0)))]
    else:
        day_weather_df = day_weather_df[day_weather_df.Date.dt.year == date.year]
    
    # интерполируем пропуски температуры (полиноминальная 3 порядка) между 0, 3, 6, 9, 12, 15, 18, 21 и 24 часами
    day_weather_df = get_empty_daily_df(date).merge(day_weather_df, how='left', on='Date')
    day_weather_df.Temperature = day_weather_df.Temperature.interpolate(method='polynomial', order=3).round(1)  
    
    return day_weather_df.tail(24)  # возвращаем погодный датафрейм с 1:00 до 24:00


def get_br_feature(date):  # версия функции до проблем с сайтом br.so-ups.ru

    '''
    SYNOPSYS: Загрузка архива/прогноза БР на указанную дату

    KEYWORD ARGUMENTS:
    date -- дата запроса в формате datetime
    
    WARNING:
    Аргумент date должен соответствовать формату: datetime(year,month,day)
    При использовании готовых конструкций datetime провести преобразование типа: datetime.date()

    RETURNS:
    df_br_feature : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> get_br_feature(datetime.now().date()).tail(3)
    
    Date					PredCons	ActCons		PredGen	ActGen	Price
    2025-11-10 22:00:00		4346		0			3645	0		2229
    2025-11-10 23:00:00		4213		0			3374	0		1832
    2025-11-11 00:00:00		4086		0			3204	0		1655

    
    >>> get_br_feature(datetime(2025, 1, 1)).tail(3)
    
    Date					PredCons	ActCons	PredGen	ActGen	Price
    2025-01-01 22:00:00		4050		4017	3407	3395	1641
    2025-01-01 23:00:00		3964		3917	3299	3286	1554
    2025-01-02 00:00:00		3842		3877	3293	3284	1393
    
    >>> len(get_br_feature(datetime(2024, 12, 31)))
    24
    '''
    
    warnings.filterwarnings('ignore')  # супрессим предупреждения https
    
    df_br_feature = pd.DataFrame(columns=['Date', 'PredCons', 'ActCons', 'PredGen', 'ActGen', 'Price'])

    index = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0'}

    for hour in range(24):

        params = {'MapType': '0',  
                    'Date': f'{date}',
                    'Hour': f'{hour}',
                    'PowerSystemId': '600000',
                    'SubjectId': '92'}  # код субъекта (92 для Татарстана)

        while(True):  # повторяем запрос до тех пор, пока не получим положительный HTTP-ответ от сервера 
        
            response = requests.get('https://br.so-ups.ru/webapi/api/map/MapPartial',
                                    params=params,
                                    headers=headers,
                                    verify=False)

            if response.status_code == 200:
                break
            else:
                print(f'HTTP response error: {response.status_code} for {date}. Download resumed automatically')
            
            
        response_data = response.json()
        target_data = response_data['MainArea']

        def parce_to_int(string):
            if string == '-':  #  обрабатываем пустые значения
                return 0
            else:  # кастуем к int распарсенное значение
                return int(re.search(r'\d?\ \d+\b', string)[0].replace(' ', ''))
                
        # добавляем +1 час, так как на сайте БР некорректное название интервала. Например, для 0-1: hour = 0 ↓
        df_br_feature.loc[index] = (datetime.combine(pd.to_datetime(date), time(hour=hour)) + timedelta(hours=1),
                                    parce_to_int(target_data['IBR_PlannedConsumption']),
                                    parce_to_int(target_data['IBR_ActualConsumption']),
                                    parce_to_int(target_data['IBR_PlannedGeneration']),
                                    parce_to_int(target_data['IBR_ActualGeneration']),
                                    parce_to_int(target_data['IBR_AveragePrice']))
        index += 1
                 
    warnings.filterwarnings("default")  # возвращаем предупреждения к дефолтным настройкам
    
    return df_br_feature


def get_RSV_rate(date):
    
    '''
    SYNOPSYS: Загрузка нерегулируемой цены РСВ на указанную дату (за месяц)

    KEYWORD ARGUMENTS:
    date -- дата запроса в формате datetime
    
    WARNING:
    Аргумент date должен соответствовать формату: datetime(year,month,day)
    При использовании готовых конструкций datetime провести преобразование типа: datetime.date()

    RETURNS:
    df_RSV_rate : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> get_RSV_rate(datetime.now().date() - timedelta(days=30)).head()
    
    Date	            A_gr_P	P_gr_A
    2025-10-01 01:00:00	0.29	33.89
    2025-10-01 02:00:00	0.32	11.19
    2025-10-01 03:00:00	12.99	565.32
    2025-10-01 04:00:00	27.15	529.12
    2025-10-01 05:00:00	23.26	325.46
    '''

    warnings.filterwarnings('ignore') # супрессим предупреждения https
    
    str_date = f'{date.year}{date.month if date.month > 9 else f"0{date.month}"}01'
    date_load = date + timedelta(days=31)
    str_date1 = f'{date_load.year}{date_load.month if date_load.month > 9 else f"0{date_load.month}"}10'
    str_date2 = f'{date.month if date.month > 9 else f"0{date.month}"}{date.year}'
    
    # выгружаем данные с сайта atsenergo.ru в форме xls-файла
    url = f"https://www.atsenergo.ru/dload/retail/{str_date}/{str_date1}_TATENERG_PTATENER_{str_date2}_gtp_1st_stage.xls"
    response = requests.get(url=url, verify=False)
        
    if response.status_code == 404:
        print(f'Error url .xls in {date}')

    try:
        with open(f'./TATENERG_PTATENER_{str_date2}_gtp_1st_stage.xls', 'wb') as file:
            file.write(response.content)
    except Exception as ex:
        print(ex)

    # считываем содержимое xls-файла в объект DataFrame
    df = pd.read_excel(f'./TATENERG_PTATENER_{str_date2}_gtp_1st_stage.xls')
    df = df.rename(columns={'Unnamed: 0': 'Date', 
                            'Unnamed: 1': 'Hour', 
                            'Unnamed: 3': 'A_gr_P',   # тариф на превышение фактического потребления над плановым
                            'Unnamed: 4': 'P_gr_A'})  # тариф на превышение планового потребления над фактическим
        
    idx = df[df.Date == 'дата'].index[0]  # определяем номер строки, с которой стартуют нужные нам данные
    df = df.iloc[idx+1:-6,:5]

    df.Date = pd.to_datetime(df.Date, dayfirst=True)
    df.Hour = df.Hour.astype('int')
    df.A_gr_P = df.A_gr_P.astype('float')
    df.P_gr_A = df.P_gr_A.astype('float')

    # добавляем +1 час для унификации с основным скриптом
    df.Date = df.apply(lambda x: datetime.combine(x.Date, time(hour=x.Hour)) + timedelta(hours=1), axis=1)
    df = df.drop(columns=['Hour', 'Unnamed: 2'])
    df.reset_index(inplace=True, drop=True)

    if df.shape[0]%24 != 0:
        print(f'Error parse .xls in {date}')

        # удаляем прочтённый xls-файл
    os.remove(f'./TATENERG_PTATENER_{str_date2}_gtp_1st_stage.xls')

    warnings.filterwarnings("default") # возвращаем предупреждения к дефолтным настройкам
    
    return df


def updating_or_create_df(get_function, filename, start=datetime(2013, 1, 1).date()):
    
    '''
    SYNOPSYS: Создание новой или пополнение существующей БД (filename.xlsx) недостающими сведениями 
    до конца предшествующего месяца с возвратом полученного датафрейма. 
    Например, если актуализация БД выполняется 7 ноября, данные будут выгружены до 2025-11-01 00:00:00 включительно
    
    KEYWORD ARGUMENTS:
    get_function –– функция, с помощью которой подразумевается пополнение БД
    filename -- база данных в формате 'filename.xlsx'
    start –– дефолтная дата старта для новой БД в DateTime-формате
    
    WARNING:
    Аргумент filename должен соответствовать формату: 'filename.xlsx'
    !При отсутствии 'filename.xlsx' по указанной директории запустится процесс генерации новой БД!
    !!Функция перезаписывает исходный filename.xlsx файл!!
    !!!Ресурс kazan.nuipogoda.ru возвращает НЕКОРРЕКТНЫЙ ФОРМАТ ДАННЫХ c 2013.01.01 по 2014.10.27!!!

    RETURNS:
    df : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> updating_or_create_df(get_weather, 'Weather.xlsx').tail(5)  # актуализация на 7 ноября 2025 г
    
    Date				Temperature
    2025-10-31 12:00:00	6
    2025-10-31 15:00:00	7
    2025-10-31 18:00:00	6
    2025-10-31 21:00:00	4
    2025-11-01 00:00:00	4

    >>> updating_or_create_df(get_br_feature, 'br_feature.xlsx').tail(5)  # актуализация на 7 ноября 2025 г
    
            Date					PredCons	ActCons		PredGen		ActGen	Price
    112483	2025-10-31 20:00:00		4485		448	3		572			3606	2377
    112484	2025-10-31 21:00:00		4414		4385		3419		3377	1895
    112485	2025-10-31 22:00:00		4293		4309		3282		3268	1618
    112486	2025-10-31 23:00:00		4140		4156		3082		3121	1480
    112487	2025-11-01 00:00:00		4008		4034		3076		3140	895
    '''
    
    try:  # актуализируем существующую БД
        df = pd.read_excel(filename)  # выгружаем старую базу
        start = df.iloc[-1, 0].date()  # последний день старой базы filename.xlsx
        
    except FileNotFoundError:  # создаем новую БД
        df = pd.DataFrame()  # создаём новый датафрейм под погодную БД

    end = datetime.now().date() - timedelta(days=datetime.now().day)  # последний день предшествующего месяца
    
    if ((end - start).days + 1) == 0:  # покидаем функцию если БД актуальна
        return df
    
    print(f'Пополнение базы данных {filename} за период: {start} – {end}')
    
    if get_function == get_RSV_rate:
        # делаем выгрузку недостающих месяцев
        for i in trange(-1, 12*(end.year - start.year) + (end.month - start.month), desc=f"month progress"):
            date = datetime(start.year + (start.month + i)//12, 1 + (start.month + i)%12, 1)
            df = pd.concat([df, get_function(date)])
    else:
        # делаем выгрузку недостающих дней до конца предшествующего месяца
        for day in trange((end - start).days + 1, desc=f"days progress"):    
            df = pd.concat([df, get_function(start + timedelta(days=day))])

    # исключаем случайное добавление дублирующих данных
    df = df.drop_duplicates(keep='first', subset=['Date'])
    df = df.sort_values(by=['Date'])
    
    # экспортируем БД/обновляем старый xlsx-файл
    df.to_excel(filename, index=False)
    
    return df


def merge_and_export_DB(total_volume_df, df_weather, df_br_feature, filename='DataBase.xlsx'):

    '''
    SYNOPSYS: Функция выполняет объединение датафреймов total_volume_df, df_weather и df_br_feature по столбцу 'Date' 
    в одну общую базу данных (по умолчанию DataBase.xlsx)
    
    KEYWORD ARGUMENTS:
    total_volume_df -- датафрейм с данными о потреблении ЭЭ до конца предшествующего месяца
    df_weather -- датафрейм с погодными данными до конца предшествующего месяца
    df_br_feature -- датафрейм с данными БР до конца предшествующего месяца
    filename -- название экспортируемой БД в формате 'filename.xlsx' (по умолчанию 'DataBase.xlsx')
    
    WARNING:
    Аргумент filename должен соответствовать формату: 'filename.xlsx'

    RETURNS:
    df : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> merge_and_export_DB(total_volume_df, df_weather, df_br_feature, filename='DataBase_test.xlsx').info()
    
    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 112488 entries, 0 to 112487
    Data columns (total 13 columns):
     #   Column       Non-Null Count   Dtype         
    ---  ------       --------------   -----         
     0   Date         112488 non-null  datetime64[ns]
     1   Year         112488 non-null  int64         
     2   Month        112488 non-null  int64         
     3   Day          112488 non-null  int64         
     4   Hour         112488 non-null  int64         
     5   Weekday      112488 non-null  int64         
     6   Volume       112488 non-null  float64       
     7   Temperature  112488 non-null  float64       
     8   PredCons     112488 non-null  int64         
     9   ActCons      112488 non-null  int64         
     10  PredGen      112488 non-null  int64         
     11  ActGen       112488 non-null  int64         
     12  Price        112488 non-null  int64         
    dtypes: datetime64[ns](1), float64(2), int64(10)
    memory usage: 11.2 MB
    '''
    
    # объединяем полученные датафреймы по дате
    df = total_volume_df.merge(df_weather, how='left', on = 'Date')
    df = df.merge(df_br_feature, on = 'Date')

    # запись backup-a старой базы
    df_old = pd.read_excel(filename)  # загрузка старой базы до санации
    end_full_month = datetime.now().date() - timedelta(days=datetime.now().day)  # последний день санируемого месяца
    # строка с именем backup-a: в скобках последний полный месяц, по которому выполняется санация; в конце дата записи backup-a
    name_backup = f"backup_{filename[:-5]}({end_full_month.strftime('%B')} {end_full_month.year})_{datetime.now().date()}.xlsx"
    df_old.to_excel(name_backup, index=False)
    print(f'Резервная копия старой базы сохранена в файле {name_backup}', end='\n\n')

    # обновляем данные в старой базе, сохраняя при этом оперативные данные за текущий месяц
    df_old.update(df)

    # сохраняем обновленную базу данных в xlsx-файл
    df_old.to_excel(filename, index=False)
    print(f'База данных {filename} обновлена', end='\n\n')
    
    return df_old

#-------------------------------service DB--------------------------------

def get_empty_daily_df(date):

    '''
    SYNOPSYS: Cоздание пустого датафрейма (25 строк: с 0:00 до 24:00) на указанную дату 
    (для полноценной интерполяции температуры)

    KEYWORD ARGUMENTS:
    date -- дата запроса в формате datetime
    
    WARNING:
    Аргумент date должен соответствовать формату: datetime(year,month,day)
    При использовании готовых конструкций datetime провести преобразование типа: datetime.date()

    RETURNS:
    pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> get_empty_daily_df(datetime(2024,6,5)).tail(5)

    	Date
    20	2024-06-05 20:00:00
    21	2024-06-05 21:00:00
    22	2024-06-05 22:00:00
    23	2024-06-05 23:00:00
    24	2024-06-06 00:00:00
    '''

    return pd.DataFrame(pd.date_range(date, periods=25, freq='h'), columns=['Date'])


def add_date_scalar(df):

    '''
    SYNOPSYS: Пополнение датафрейма дополнительными (временнЫми) категориальными признаками
    Признак 'Weeekday' (день недели) кодируется по принципу label encoder (0 - понедельник, 1 - вторник и т.д.)

    KEYWORD ARGUMENTS:
    df -- объект типа pandas.core.frame.DataFrame

    WARNING:
    Аргумент df должен обязательно содержать колонку 'Date' с данными типа datetime

    RETURNS:
    pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> add_date_scalar(test_df).tail(5)

        Date	            Year	Month	Day	Hour	Weekday
    20	2024-06-05 20:00:00	2024	6	    5	20	    2
    21	2024-06-05 21:00:00	2024	6	    5	21	    2
    22	2024-06-05 22:00:00	2024	6	    5	22	    2
    23	2024-06-05 23:00:00	2024	6	    5	23	    2
    24	2024-06-06 00:00:00	2024	6	    6	0	    3
    '''

    df['Year'] = df.Date.dt.year
    df['Month'] = df.Date.dt.month
    df['Day'] =  df.Date.dt.day
    df['Hour'] = df.Date.dt.hour
    df['Hour'] = df['Hour']
    df['Weekday'] = df.Date.dt.weekday
    return df


def is_check_DataBase(df):

    '''
    SYNOPSYS: Проверка целостности БД

    KEYWORD ARGUMENTS:
    df -- объект типа pandas.core.frame.DataFrame с проверяемой БД

    WARNING:
    Аргумент df должен обязательно содержать колонку 'Date' с данными типа datetime

    RETURNS:
    status : bool
    
    EXAMPLES:
    >>> is_check_DataBase(df)  # проверка БД с отсутствующей строкой данных на 2023-03-26 05:00:00
    WARNING: no data on date 2023-03-26 05:00:00
    False

    >>> is_check_DataBase(df)  # проверка БД с отсутствующими значениями БР в разные даты
    WARNING: The database contains NULL:
    19722   2015-04-02 19:00:00
    89614   2023-03-23 23:00:00
    89676   2023-03-26 13:00:00
    Name: Date, dtype: datetime64[ns]
    False

    >>> is_check_DataBase(df)  # проверка целостной БД
    The database is complete
    True
    '''
    
    i, date, status = 0, df.iloc[0].Date, True
    
    while (date != df.iloc[-1].Date):
        if df.iloc[i].Date != date:
            status = False
            print("\033[1;31m{}".format(f'WARNING: no data on date {date}'))
        else:
            i += 1
        date += timedelta(hours=1)
    
    if df.isnull().any().any():
        status = False
        print('\033[1;31m{}'.format(f'WARNING: The database contains NULL:\n{df[df.isnull().any(axis=1)].Date}'))
        
    if status:
        print("\033[1;32m{}".format(f'The database is complete'))
        
    return status


def act_pred_reverse(df_br_feature):
    
    '''
    SYNOPSYS: Замена пропусков фактических (Act) значений потребления и генерации БР плановыми (Pred)
    Функция используется при формировании прогноза на текущие сутки, когда фактические значения 
    ActCons и ActGen доступны не на весь день

    KEYWORD ARGUMENTS:
    df_br_feature -- суточный датафрейм с данными БР

    RETURNS:
    df_br_feature : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> act_pred_reverse(get_br_feature(datetime.now().date()))
    '''
    
    df_br_feature.ActCons = np.where(df_br_feature.ActCons == 0, df_br_feature.PredCons, df_br_feature.ActCons)
    df_br_feature.ActGen = np.where(df_br_feature.ActGen == 0, df_br_feature.PredGen, df_br_feature.ActGen)
    
    # удаляем лишние (для дальнейшего прогноза) признаки
    df_br_feature = df_br_feature.drop(columns=['PredCons', 'PredGen'])
    
    return df_br_feature


def get_files_from_path(path='_raw_Data_TatEnergosbyt'):

    '''
    SYNOPSYS: Получение оперативных данных из директории (по умолчанию '/_raw_Data_TatEnergosbyt')

    KEYWORD ARGUMENTS:
    directory -- путь, по которому располагаются оперативные данные в формате .xlsx
    
    WARNING:
    Функция разработана под ежесуточные данные формата xlsx
    !после прочтения xlsx файл удаляется!

    RETURNS:
    total_oper_df : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> get_files_from_path()
    '''
    
    files = list(file for file in os.listdir(path) if 'xlsx' in file)

    # формируем датафрейм из этих файлов
    total_oper_df = pd.DataFrame()

    for i in trange(len(files), desc='files progress'):
        # получаем данные из единичного xlsx-файла
        oper_df = pd.read_excel(f'{path}/{files[i]}')
        oper_df.drop(oper_df.columns[[0, 3, 4, 5]], axis=1, inplace=True)
        oper_df.columns = ['Date', 'Volume']
        oper_df = oper_df[5:]
        oper_df.Volume = oper_df.Volume.astype(float)
        oper_df.Date = oper_df.Date.astype('datetime64[ns]')
        oper_df.Date = oper_df.Date.dt.floor('h')  # убираем "мусорные" микросекунды

        # пополняем датафрейм погодными условиями
        oper_df = oper_df.merge(get_weather(oper_df.iloc[0].Date.floor('d')), how='left', on='Date')

        # пополняем датафрейм дополнительными категориальными признаками
        oper_df = add_date_scalar(oper_df)

        # пополняем датафрейм данными с балансирующего рынка
        oper_df = oper_df.merge(get_br_feature(oper_df.iloc[0].Date.floor('d')), how='left', on='Date')

        # сшиваем данные из единичных xlsx-файлов
        total_oper_df = pd.concat([total_oper_df, oper_df])
        total_oper_df.drop_duplicates(keep='last', subset=['Date'], inplace=True)
        total_oper_df.reset_index(drop=True, inplace=True)

        # удаляем прочтённый xlsx-файл (во избежание дублирования строк в БД)
        os.remove(f'{path}/{files[i]}')
    
    #print(total_oper_df.info())   # проверка целостности выгруженных данных
    
    return total_oper_df


def update_DataBase(total_oper_df, filename='DataBase.xlsx'):

    '''
    SYNOPSYS: Актуализация БД путём добавления оперативных данных из 'total_oper_df'
    
    KEYWORD ARGUMENTS:
    total_oper_df -- датафрейм с оперативными данными
    filename -- база данных в формате 'filename.xlsx'
    
    WARNING:
    Аргумент filename должен соответствовать формату: 'filename.xlsx'
    !При отсутствии данных в датафрейме 'total_oper_df' функция не выполнит перезапись БД!
    !!После добавления оперативных сведений, перед записью БД, выполняется проверка целостности!!

    RETURNS:
    df : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> update_DataBase(total_oper_df)
    
    The database is complete
    '''
    df = pd.read_excel('DataBase.xlsx')
    if total_oper_df.shape[0]:    

        # добавляем полученные данные к общей базе
        df = pd.concat([df, total_oper_df])

        df = df.drop_duplicates(keep='last', subset=['Date'])  # исключаем случайное добавление дублирующих данных
        df = df.sort_values(by=['Date'])  # сортируем данные по времени на случай неравномерного заполнения фрейма

        # проверяем целостность БД
        if is_check_DataBase(df):
            df.to_excel('DataBase.xlsx', index=False)  # обновляем xlsx-файл с БД

    return df