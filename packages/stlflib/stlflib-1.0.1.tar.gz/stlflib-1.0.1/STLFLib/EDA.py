from .dependency import *
from .validating import *

def draw_learning_curve(df_general, max_depth, model, fontsize=15):
    
    '''
    SYNOPSYS: Расчёт и построение кривой обучения

    KEYWORD ARGUMENTS:
    df_general -- валидируемая генеральная совокупность
    max_depth -- максимальная глубина решающего дерева регрессора
    model -- тип модели
    fontsize -- размер шрифта на графике

    RETURNS:
    None
    
    EXAMPLE:
    >>> draw_learning_curve(df_general, max_depth=6, model=model)
    '''
    
    def X_y_split(df_general, learn_period):
    
        '''
        SYNOPSYS: Разделение выборки на целевой и исходные признаки
        '''
        
        datetime=df_general.Date.iloc[-1]
        
        df_train = df_general[(df_general.Date > datetime - timedelta(days=round(365.25*learn_period), hours=0)) &
                              (df_general.Date <= datetime)]
        
        return df_train.drop(columns=['Date', 'Volume']), df_train.Volume
    
    if model == 'br3_act':  # c 30 ноября 2025 перейти на 8 лет для br3 и 13 лет для br2
        df_general = df_general.drop(columns=['PredCons', 'PredGen'])
        learn_period = 7
    elif model == 'br2_act':
        df_general = df_general.drop(columns=['PredCons', 'PredGen', 'Price'])
        learn_period = 12
    
    X, y = X_y_split(df_general, learn_period)

    engine = catboost.CatBoostRegressor(silent=True,
                                       n_estimators = 200,
                                       max_depth = max_depth)
    common_params = {
                     "X": X,
                     "y": y,
                     "train_sizes": np.linspace(1/learn_period, 1.0, learn_period),
                     "cv": TimeSeriesSplit(n_splits=5),
                     "scoring": 'neg_mean_absolute_percentage_error',
                     "n_jobs": -1,
                     "line_kw": {"marker": "o"},
                     "std_display_style": "fill_between",
                     "score_name": "neg MAPE",
                    }

    plt.figure(figsize=(10, 5))
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#1f77b4', '#8ec489']) 
    plt.rcParams['font.family'] = 'Palatino Linotype'
    plt.rcParams['font.size'] = fontsize    
    
    LCD = LearningCurveDisplay.from_estimator(engine, **common_params)
    train_sizes = LCD.train_sizes
    test_scores = LCD.test_scores
    mean_test_scores = [test_scores[i].mean() for i in range(len(test_scores))]    
    opt_y = max(mean_test_scores)
    opt_x = train_sizes[mean_test_scores.index(opt_y)]
    
    for i in range(len(mean_test_scores)):
        plt.text(train_sizes[i], mean_test_scores[i], f'{i+1}', ha='center', va='bottom')
    
    plt.annotate('Optimal period', xy=(opt_x, opt_y), 
                 xycoords='data', xytext=(opt_x-4000, opt_y-0.015), 
                 textcoords='data', fontsize=fontsize, 
                 arrowprops=dict(arrowstyle='-|>'))
    
    plt.title(f'Learning Curve for {model} (max_depth={max_depth})', fontsize=fontsize)
    plt.legend(['Training score', 'Test score'], loc='lower right')
    plt.tight_layout()
    #plt.savefig(f'pictures/br2_Learning_Curve(max_depth={max_depth}).png', dpi = 300, transparent = True)
    plt.show()