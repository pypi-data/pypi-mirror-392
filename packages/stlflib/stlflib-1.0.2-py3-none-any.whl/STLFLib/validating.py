from .dependency import *
from .core import *

def get_df_val_predicted(df_general,
                         df_general_date_index,
                         max_depth, 
                         learn_period,
                         model = 'br3_act',
                         date_start = datetime.now().date(), 
                         date_end = datetime.now().date() + timedelta(days=1),
                         ):
    
    '''
    SYNOPSYS: Функция генерации датафрейма с прогнозными объёмами энергопотребления под указанный горизонт планирования,
    адаптированная под валидационные расчеты (имитация отсутствия данных 'ActCons' и 'ActGen' после 7 утра, 
    оффлайн доступ к прогнозу погоды и данным Balancing Market)

    KEYWORD ARGUMENTS:
    df_general -- актуальная генеральная совокупность ко дню прогноза
    df_general_date_index –– глобальная генеральная совокупность, индексированная по дате
    max_depth -- максимальная глубина решающего дерева регрессора
    learn_period -- период обучения модели (размер тренировочной выборки)
    model -- тип модели (по умолчанию br3_act: [ActCons, ActGen, Price])
    date_start -- дата от начала старта прогноза (по умолчанию – текущий день)
    date_end -- дата окончания прогноза (по умолчанию – сутки вперёд)

    WARNING:
    get_br_feature(date) и get_weather(date) переопределены внутри функции для работы в offline-режиме

    RETURNS:
    df_predict : pandas.core.frame.DataFrame
    
    EXAMPLE:
    # генерация прогнозных объемов потребления ЭЭ на сутки вперед
    >>> get_df_predicted(df_general, df_general_date_index, max_depth, learn_period, model)

    # генерация прогнозных объемов потребления ЭЭ от указанной даты на сутки вперед
    >>> get_df_predicted(df_general, df_general_date_index, max_depth, learn_period, model, date_start=datetime(2024, 5, 12).date())

    # генерация прогнозных объемов потребления ЭЭ от текущего дня до указанной даты
    >>> get_df_predicted(df_general, df_general_date_index, max_depth, learn_period, model, date_end=datetime(2024, 6, 15).date())

    # генерация прогнозных объемов потребления ЭЭ от одной до другой указанной даты
    >>> get_df_predicted(df_general, df_general_date_index, max_depth, learn_period, model, 
                         date_start=datetime(2024, 5, 14).date(), date_end=datetime(2024, 5, 16).date())

    # генерация прогнозных объемов потребления ЭЭ на двое суток вперед
    >>> get_df_predicted(df_general, df_general_date_index, max_depth, learn_period, model, 
                         date_end=datetime.now().date() + timedelta(days=2))
    '''
    
    def get_br_feature(date):
        return get_empty_daily_df(date).merge(df_general_date_index[['PredCons', 'ActCons', 'PredGen',  'ActGen', 'Price']], 
                                              how='left', on='Date')
    
    def get_weather(date):
        return get_empty_daily_df(date).merge(df_general_date_index.Temperature, how='left', on='Date').tail(24)
    
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
            
            # обнуляем весь факт с 8:00 в df_predicted_daily (ФИЧА ИСКЛЮЧИТЕЛЬНО ДЛЯ ВАЛИДАТОРА!)
            # чтобы сместить доступный час, поменяй параметр time(hour=8)
            df_predicted_daily.loc[df_predicted_daily.Date >= datetime.combine(date_start, time(hour=8)),
                                   ['ActCons', 'ActGen']] = 0
            
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


def get_df_validate(df_general, df_general_date_index, max_depth, learn_period, model, date_start, date_end, logging=True):

    '''
    SYNOPSYS: Функция валиации модели. Возвращает валидационный фрейм с прогнозными значениями

    KEYWORD ARGUMENTS:
    df_general -- валидируемая генеральная совокупность
    df_general_date_index –– глобальная генеральная совокупность, индексированная по дате
    max_depth -- максимальная глубина решающего дерева регрессора
    learn_period -- период обучения модели (размер тренировочной выборки)
    model -- тип модели (по умолчанию br3_act: [ActCons, ActGen, Price])
    date_start -- дата от начала старта валидации
    date_end -- дата окончания валидации

    RETURNS:
    df_validate_result : pandas.core.frame.DataFrame
    
    EXAMPLE:
    >>> get_df_validate(df_general, max_depth, learn_period, model='br3_act', 
                        date_start=datetime(2025, 1, 1),
                        date_end=datetime(2025, 11, 1))

    Валидация br3_act за период: 2025-01-01 01:00:00 – 2025-11-01 00:00:00
    '''
    
    # определяем размер валидационной выборки
    df_validate = df_general[(df_general.Date > datetime.combine(date_start, time(hour=0))) & 
                             (df_general.Date < datetime.combine(date_end, time(hour=1)))]
    
    df_validate.reset_index(drop=True, inplace=True)

    # оповещение о периоде валидации
    if logging:
        print(f'Валидация {model} за период: {df_validate.iloc[0, 0]} – {df_validate.iloc[-1, 0]}')
    
    # итоговый валидационный датафрейм с прогнозными значениями
    df_validate_result = pd.DataFrame()

    # посуточная валидация для выбранного интервала (с виджетом процесса)
    for i in trange(int((df_validate.shape[0]) / 24), desc=f"days progress (period: {learn_period}, max_depth: {max_depth})"):
        
        # формируем дату прогноза
        idate = df_validate.iloc[0].Date + timedelta(days=i)
        
        # ограничиваем размер генеральной совокупности (до -2 суток до даты прогноза)
        df_general_cut = df_general[df_general.Date < idate - timedelta(days=1)]
        
        # выполняем прогноз на указанную дату (с учетом -1 суток)
        df_predicted = get_df_val_predicted(df_general_cut,
                                            df_general_date_index,
                                            max_depth,
                                            learn_period,
                                            model, 
                                            date_start=idate.date()-timedelta(days=1), 
                                            date_end=idate.date())
            
        # пополняем валидационный фрейм прогнозными значениями
        df_validate_result = pd.concat([df_validate_result, df_validate.merge(df_predicted, how='left', on='Date')])
        df_validate_result.dropna(inplace=True)

    # для визуального контроля модели
    if model == 'br3_act':
        df_validate_result = df_validate_result.drop(columns=['PredCons', 'PredGen'])
    elif model == 'br2_act':
        df_validate_result = df_validate_result.drop(columns=['PredCons', 'PredGen', 'Price'])
    
    return df_validate_result


def get_df_validate_with_loss(df_validate_result, df_RSV_vs_BR_rate):   
    
    '''
    SYNOPSYS: Добавление столбца `loss` с потерями на БР в результирующий датафрейм

    KEYWORD ARGUMENTS:
    df_validate_result -- датафрейм с результатами валидации
    df_RSV_vs_BR_rate -- датафрейм с ценами трансляции

    WARNING:
    Перед передачей аргумента df_validate_result обязательно сделать поверхностную копию датафрейма!
    
    RETURNS:
    df_validate_result : pandas.core.frame.DataFrame
    
    EXAMPLE:
    # Валидация
    >>> get_df_validate_with_loss(df_validate_result.copy(), df_RSV_vs_BR_rate).tail(6)

    Date	            Month	Volume	    Predicted	    Temp    A_gr_P	P_gr_A	diff_cons	loss
    2025-10-31 19:00:00	10	    3048.447	3111.348001	    5.3	    81.71	0.03	-62.901001	1.887030
    2025-10-31 20:00:00	10	    2990.510	3076.723773	    4.6	    0.00	126.69	-86.213773	10922.422939
    2025-10-31 21:00:00	10	    2934.933	3026.825067	    4.0	    0.00	520.23	-91.892067	47805.010082
    2025-10-31 22:00:00	10	    2880.025	2925.862016	    3.6	    0.00	712.90	-45.837016	32677.209003
    2025-10-31 23:00:00	10	    2755.676	2812.551380	    3.6	    0.00	545.83	-56.875380	31044.288899
    2025-11-01 00:00:00	11	    2636.455	2698.748793	    4.0	    0.00	832.01	-62.293793	51829.058486

    '''
    
    # добавляем в итоговую таблицу штрафные тарифы БР
    df_validate_result = df_validate_result.merge(df_RSV_vs_BR_rate, how='left', on='Date')
    df_validate_result = df_validate_result[['Date', 'Month', 'Volume', 'Predicted', 'Temperature', 'A_gr_P', 'P_gr_A']]

    # оцениваем размер "потерь" от работы на БР
    df_validate_result['diff_cons'] = df_validate_result.Volume - df_validate_result.Predicted
    df_validate_result['loss'] = np.where(df_validate_result.diff_cons > 0, 
                                          df_validate_result.diff_cons * df_validate_result.A_gr_P, 
                                          abs(df_validate_result.diff_cons) * df_validate_result.P_gr_A)
    return df_validate_result


def draw_diff_predict_vs_fact(df_validate_result):
    
    '''
    SYNOPSYS: Вывод результатов валидации в форме таблицы и графика

    KEYWORD ARGUMENTS:
    df_validate_result -- датафрейм с результатами валидации
    
    WARNING:
    - df_validate_result должен обязательно содержать столбцы Volume и Predict!
    - наличие столбцов 'loss' и 'Month' опционально

    RETURNS:
    None
    
    EXAMPLES:
    >>> diff_predict_vs_fact(df_validate_result)

    MAE: 35.979 [MW]
    MAPE: 1.357%

    Среднесуточные потери: 4758.01 RUR 
    Медианные суточные потери: 337.53 RUR 
    Суммарные потери за период: [2025-01-01 ÷ 2025-11-01]: 34714422.04 RUR

    January 2025	MAPE: 1.481%	Mean loss: 4074.31 RUR	    Sum loss: 3027211.12 RUR
    February 2025	MAPE: 1.084%	Mean loss: 2412.89 RUR	    Sum loss: 1621460.47 RUR
    March 2025	    MAPE: 1.092%	Mean loss: 1387.58 RUR	    Sum loss: 1032358.74 RUR
    April 2025	    MAPE: 1.445%	Mean loss: 2832.92 RUR	    Sum loss: 2039703.89 RUR
    May 2025	    MAPE: 1.489%	Mean loss: 9442.58 RUR	    Sum loss: 7025280.43 RUR
    June 2025	    MAPE: 1.415%	Mean loss: 4662.75 RUR	    Sum loss: 3357178.89 RUR
    July 2025	    MAPE: 1.484%	Mean loss: 4094.05 RUR	    Sum loss: 3045976.76 RUR
    August 2025	    MAPE: 1.632%	Mean loss: 4819.43 RUR	    Sum loss: 3585654.93 RUR
    September 2025	MAPE: 1.351%	Mean loss: 10712.94 RUR	    Sum loss: 7713318.61 RUR
    October 2025	MAPE: 1.071%	Mean loss: 2980.95 RUR	    Sum loss: 2217826.76 RUR
    '''  
    
    df_validate = df_validate_result.copy()
    
    # добавление новых столбцов (для расчёта усреднённой погрешности)
    df_validate.insert(df_validate.shape[1], 'MAPE', 
                       MAPE(df_validate.Predicted, df_validate.Volume)*100)

    df_validate['Error'] = abs((df_validate.Volume - df_validate.Predicted)*100 / df_validate.Volume)

    df_validate.reset_index(drop=True, inplace=True)

    fig, df_volume = plt.subplots(figsize=(16,5))
    df_error = df_volume.twinx()

    df_volume.plot(df_validate.Volume, label='Actual value')
    df_volume.plot(df_validate.Predicted, label='Predicted value')
    df_error.plot(df_validate.Error, label='Error, %', color='#2ca02c')
    df_error.plot(df_validate.MAPE, '-.b')

    plt.rcParams['font.size'] = '12'

    df_volume.legend(loc='upper right')
    df_volume.set_xlim(0, df_validate.shape[0])
    df_volume.set_ylim(df_validate.Volume.min() - 100, df_validate.Volume.max() + 100)
    df_volume.set_ylabel('Volume, MWt·h', fontsize = 14)
    df_volume.set_xlabel('Counts of records', fontsize = 14)

    df_error.set_ylim(0, 10)
    df_error.set_ylabel('Absolute percentage error, %', fontsize = 14, color='g')

    title = 'The segment of the model testing process'
    plt.title(f'{title} ({df_validate.iloc[0].Date.date()} – {df_validate.iloc[-1].Date.date()})', fontsize = 16)
    
    print(f'MAE: {MAE(df_validate.Predicted, df_validate.Volume):.3f} [MW]',
          f'MAPE: {MAPE(df_validate.Predicted, df_validate.Volume):.3%}', sep='\n')

    if 'loss' in df_validate.columns:    
        print(f'\nСреднесуточные потери: {round(df_validate.loss.mean(), 2)} RUR',          
              f'\nМедианные суточные потери: {round(df_validate.loss.median(), 2)} RUR',
              f'\nСуммарные потери за период: [{df_validate.iloc[0].Date.date()} ÷ {df_validate.iloc[-1].Date.date()}]:', 
              f'{round(df_validate.loss.sum(), 2)} RUR', end='\n\n')
    
    if 'Month' in df_validate.columns:      
        df_validate.Month = df_validate.Date.apply(lambda x: f"{x.month_name()} {x.year}")
        list_months = list(df_validate.Month.unique())[:-1]  # исключаем месяц с одним "нулевым" часом

        for month in list_months:

            df_month = df_validate[df_validate.Month == month]

            mean_loss_message, sum_loss_message = '', ''
            if 'loss' in df_validate.columns: 
                mean_loss_message = f'Mean loss: {round(df_month.loss.mean(), 2)} RUR'
                sum_loss_message = f'Sum loss: {round(df_month.loss.sum(), 2)} RUR'

            print(f'{month}',
                  f'MAPE: {MAPE(df_month.Predicted, df_month.Volume):.3%}',
                  mean_loss_message,
                  sum_loss_message,
                  sep='\t')
            

def Grid_Search(df_general,
                df_general_date_index,
                max_depth_grid,  # tuple type
                learn_period_grid,   # tuple type
                model, 
                date_start, 
                date_end):
    
    '''
    SYNOPSYS: Сеточный поиск оптимальных периода обучения и глубины дерева

    KEYWORD ARGUMENTS:
    df_general -- валидируемая генеральная совокупность
    df_general_date_index –– глобальная генеральная совокупность, индексированная по дате
    max_depth_grid -- диапазон поиска максимальной глубины решающего дерева регрессора
    learn_period_grid -- диапазон поиска периода обучения модели (размер тренировочной выборки)
    model -- тип модели
    date_start -- дата от начала старта валидации
    date_end -- дата окончания валидации

    RETURNS:
    df_search_result : pandas.core.frame.DataFrame
    
    EXAMPLE:
    >>> Grid_Search(df_general,
                    df_general_date_index,
                    max_depth_grid=(5, 7),
                    learn_period_grid=(4, 7),
                    model='br3',
                    date_start=datetime(2025, 1, 1), 
                    date_end=datetime(2025, 11, 1))

    Валидация br3_act за период: 2025-01-01 01:00:00 – 2025-11-01 00:00:00
    
    period	max_depth	MAPE
    4	    5	        0.014033
    4	    6	        0.013729
    4	    7	        0.013998
    5	    5	        0.013865
    5	    6	        0.013620
    5	    7	        0.013783
    6	    5	        0.013730
    6	    6	        0.013719
    6	    7	        0.013917
    7	    5	        0.013757
    7	    6	        0.013695
    7	    7	        0.013869
    '''
    
    print(f'GridSearch {model} for period: {date_start} – {date_end}')

    # Create an empty dataframe for the search results
    df_search_result = pd.DataFrame(columns=['period', 'max_depth', 'MAPE'])

    # grid node index of the resulting dataframe
    index = 0  

    # form a grid of hyperparameters
    for learn_period in trange(learn_period_grid[0], learn_period_grid[1]+1, desc=f"total progress"):
        for max_depth in range(max_depth_grid[0], max_depth_grid[1]+1):

            df_validate_result = get_df_validate(df_general, df_general_date_index,
                                                 max_depth, learn_period, model, 
                                                 date_start,
                                                 date_end,
                                                 logging=False)  # год, месяц, день

            # fill the resulting dataframe with metrics and model parameters
            df_search_result.loc[index] = (learn_period,
                                           max_depth,
                                           MAPE(df_validate_result.Predicted, df_validate_result.Volume))
            index += 1

    return df_search_result


def search_result_highlighting(df_search_result):

    '''
    SYNOPSYS: Подсветка результатов поиска датафрейма 'df_search_result'
    '''
    
    search_result = df_search_result.copy()    
    search_result = search_result.style.format({'MAPE': '{:.3%}',
                                                }).background_gradient(cmap=sns.color_palette("vlag", as_cmap=True))

    n = df_search_result.MAPE.idxmin()
    print(f'Best results (MAPE: {df_search_result.loc[n].MAPE:.3%}) obtained for the parameters: ',
          f'Period: {df_search_result.loc[n].period}',
          f'max_depth: {df_search_result.loc[n].max_depth}', sep='\n')

    return search_result