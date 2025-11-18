from .dependency import *
from .preprocessing import *
from .serviceDB import *

def predict_volume(df_general, df_predict, max_depth, learn_period):

    '''
    SYNOPSYS: Функция обучения модели и прогнозирования объемов энергопотребления

    KEYWORD ARGUMENTS:
    df_general -- датафрейм с генеральной совокупностью данных (X_train, y_train)
    df_predict -- суточный датафрейм с исходными данными для прогноза (x_pred)
    max_depth -- максимальная глубина решающего дерева регрессора
    learn_period -- период обучения модели (размер тренировочной выборки)

    RETURNS:
    df_predict : pandas.core.frame.DataFrame
    
    EXAMPLES:
    >>> predict_volume(df_general, df_predict, datetime(2025, 8, 30, 1), max_depth, learn_period).info()
    
    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 24 entries, 0 to 23
    Data columns (total 21 columns):
    #   Column       Non-Null Count  Dtype         
    ---  ------       --------------  -----         
    0   Date         24 non-null     datetime64[ns]
    1   Year         24 non-null     int64         
    2   Month        24 non-null     int64         
    3   Day          24 non-null     int64         
    4   Hour         24 non-null     int64         
    5   Weekday      24 non-null     int64         
    6   Volume       24 non-null     float64       
    7   Temperature  24 non-null     float64       
    8   ActCons      24 non-null     int64         
    9   ActGen       24 non-null     int64         
    10  Price        24 non-null     int64         
    11  TypeDay      24 non-null     int64         
    12  Light        24 non-null     int64         
    13  Season       24 non-null     int64         
    14  lag-1        24 non-null     float64       
    15  lag-2        24 non-null     float64       
    16  lag-3        24 non-null     float64       
    17  lag-4        24 non-null     float64       
    18  lag-5        24 non-null     float64       
    19  lag-6        24 non-null     float64       
    20  lag-7        24 non-null     float64       
    dtypes: datetime64[ns](1), float64(9), int64(11)
    memory usage: 4.1 KB
    '''
    
    # формируем оптимальную обучающую выборку
    df_train = df_general[df_general.Date > df_predict.iloc[0].Date - timedelta(days=365*learn_period+1, hours=1)]

    # обучаем модель
    model = catboost.CatBoostRegressor(silent=True,
                                       n_estimators = 200,
                                       max_depth = max_depth)

    model.fit(df_train.drop(columns=['Date', 'Volume']), df_train.Volume)

    # прогнозируем объёмы потребления на ближайшие сутки
    df_predict.Volume = model.predict(df_predict.drop(columns=['Date', 'Volume']))
   
    return df_predict


def get_df_predicted(df_general,
                     max_depth, 
                     learn_period,
                     model,
                     date_start = datetime.now().date(), 
                     date_end = datetime.now().date() + timedelta(days=1),
                     ):
    
    '''
    SYNOPSYS: Функция генерации датафрейма с прогнозными объёмами энергопотребления под указанный горизонт планирования

    KEYWORD ARGUMENTS:
    df_general -- актуальная генеральная совокупность ко дню прогноза
    max_depth -- максимальная глубина решающего дерева регрессора
    learn_period -- период обучения модели (размер тренировочной выборки)
    model -- тип модели (по умолчанию br3_act: [ActCons, ActGen, Price])
    date_start -- дата от начала старта прогноза (по умолчанию – текущий день)
    date_end -- дата окончания прогноза (по умолчанию – сутки вперёд)

    RETURNS:
    df_predict : pandas.core.frame.DataFrame
    
    EXAMPLE:
    # генерация прогнозных объемов потребления ЭЭ на сутки вперед
    >>> get_df_predicted(df_general, max_depth, learn_period, model)

    # генерация прогнозных объемов потребления ЭЭ от указанной даты на сутки вперед
    >>> get_df_predicted(df_general, max_depth, learn_period, model, date_start=datetime(2024, 5, 12).date())

    # генерация прогнозных объемов потребления ЭЭ от текущего дня до указанной даты
    >>> get_df_predicted(df_general, max_depth, learn_period, model, date_end=datetime(2024, 6, 15).date())

    # генерация прогнозных объемов потребления ЭЭ от одной до другой указанной даты
    >>> get_df_predicted(df_general, max_depth, learn_period, model, date_start=datetime(2024, 5, 14).date(), 
                                                        date_end=datetime(2024, 5, 16).date())

    # генерация прогнозных объемов потребления ЭЭ на двое суток вперед
    >>> get_df_predicted(df_general, max_depth, learn_period, model, date_end=datetime.now().date() + timedelta(days=2))
    '''
    
    # генерируем пустой датафрейм под итоговый результат
    df_predicted = pd.DataFrame()
    
    #for date in trange((date_end - date_start).days + 1, desc=f"days progress"):  # виджет процесса расчёта по суткам
    for date in range((date_end - date_start).days + 1):
    
        # генерируем пустой суточный датафрейм с погодными и календарными признаками
        df_predicted_daily = add_date_scalar(get_weather(date_start + timedelta(days=date)))
        
        # разделяем логику обучения (текущие сутки с учётом БР, последующие - без учёта БР)
        if date == 0:
            
            if model == 'br3_act':
                # удаляем столбцы с прогнозными значениями генерации и потребления БР СО ЕЭС
                df_general = df_general.drop(columns=['PredCons', 'PredGen'])
                 # выгружаем данные (прогнозные и часть актуальных) с балансирующего рынка на текущие сутки
                df_predicted_daily = df_predicted_daily.merge(get_br_feature(date_start), on='Date')
            elif model == 'br2_act':
                # удаляем столбцы с прогнозными значениями генерации и потребления БР СО ЕЭС и 1 признак: `Price`
                df_general = df_general.drop(columns=['PredCons', 'PredGen', 'Price'])
                 # выгружаем данные (прогнозные и часть актуальных) с балансирующего рынка на текущие сутки
                df_predicted_daily = df_predicted_daily.merge(get_br_feature(date_start).drop(columns='Price'), on='Date')
            
            # восстанавливаем пропуски ActCons и ActGen данными из столбцов PredCons и PredGen
            df_predicted_daily = act_pred_reverse(df_predicted_daily)
            
        elif date == 1:

            if model == 'br3_act':
                df_general = df_general.drop(columns=['ActCons', 'ActGen', 'Price'])
            elif model == 'br2_act':
                df_general = df_general.drop(columns=['ActCons', 'ActGen'])

        # добавляем последние 168 (24 · 7) строк от df_general для генерации временного лага
        df_predicted_daily = pd.concat([df_general.tail(168), df_predicted_daily])

        # генерируем временной лаг (1 полная неделя)
        df_predicted_daily = prepareData(df_predicted_daily)

        # получаем прогнозные значения на текущие сутки
        df_predicted_daily = predict_volume(df_general, 
                                            df_predicted_daily, 
                                            max_depth, 
                                            learn_period)

        # добавляем полученные прогнозные значения в итоговый прогнозный фрейм
        df_predicted = pd.concat([df_predicted, df_predicted_daily])

        # пополняем генеральную совокупность текущими сутками (+24 строки) для планирования следующего дня
        df_general = pd.concat([df_general, df_predicted_daily])

    df_predicted.rename(columns = {'Volume':'Predicted'}, inplace = True)

    # убрать .tail(24) если необходимо получить прогноз на несколько дней
    return df_predicted[['Date', 'Predicted']].tail(24*(date_end - date_start).days)


def date_str_format(df_predicted):
    
    '''
    SYNOPSYS: генерация строки с датой для экспортируемого xlsx-файла

    KEYWORD ARGUMENTS:
    date -- дата, на которую генерируется прогноз

    RETURNS: str
    
    EXAMPLE:
    >>> date_str_format(df_predicted)
    '12.11.2025'

    >>> date_str_format(df_predicted)
    '12-13.11.2025'

    >>> date_str_format(df_predicted)
    '30.11.2025-01.12.2025'
    '''
    
    def single_date_str_format(date):    
        return f'{0 if date.day < 10 else ""}{date.day}.{0 if date.month < 10 else ""}{date.month}.{date.year}'
    
    date_start = df_predicted.iloc[1].Date.date()
    date_end = df_predicted.iloc[-2].Date.date()
    
    if df_predicted.shape[0] == 24:
        return single_date_str_format(date_start)
    else:
        if date_start.month != date_end.month: # даты начала и конца выходят за пределы текущего месяца
            return f'{single_date_str_format(date_start)}-{single_date_str_format(date_end)}'
        else: # даты начала и конца не выходят за пределы текущего месяца
            str_day = f'{0 if date_start.day < 10 else ""}{date_start.day}-{0 if date_end.day < 10 else ""}{date_end.day}'
            str_month = f'{0 if date_start.month < 10 else ""}{date_start.month}'
            return f'{str_day}.{str_month}.{date_start.year}'
          

def get_DAM_order(df_general, 
                  max_depth, 
                  learn_period, 
                  model = 'br3_act',
                  date_start = datetime.now().date(), 
                  date_end = datetime.now().date() + timedelta(days=1),
                  ):
    
    '''
    SYNOPSYS: функция, генерирующая заявку на РСВ с экспортом в xlsx-форму

    KEYWORD ARGUMENTS:
    df_general -- актуальная генеральная совокупность ко дню прогноза
    max_depth -- максимальная глубина решающего дерева регрессора
    learn_period -- период обучения модели (размер тренировочной выборки)
    model -- тип модели (по умолчанию br3_act: [ActCons, ActGen, Price])
    date_start -- дата от начала старта прогноза (по умолчанию – текущий день)
    date_end -- дата окончания прогноза (по умолчанию – сутки вперёд)

    RETURNS: *.xlsx
    
    EXAMPLE:
    >>> get_DAM_order(df_general, max_depth, learn_period)

    >>> get_DAM_order(
                      df_general, max_depth, learn_period, model,
                      date_start=datetime.now().date(), date_end=datetime.now().date() + timedelta(days=2))
                     )
    '''    
    
    df_predicted = get_df_predicted(df_general, max_depth, learn_period, model, date_start, date_end)
    return_days = (date_end - date_start).days
    
    if df_predicted.shape[0] == 24*return_days:
        df_predicted.to_excel(f'Predicted({date_str_format(df_predicted)}).xlsx', index=False)
        print(f'Результаты прогноза сохранены в файле Predicted({date_str_format(df_predicted)}).xlsx')
    else:
        print("\033[1;31m{}".format('WARNING: No data in exported dataframe'))

    return df_predicted