# Short-Term Load Forecasting Based on CatBoost Model Library (STLFLib)

This is a Python STLF machine learning library designed for generating energy consumption bids for the DAM (day-ahead market). 
The library is distributed under the KSPEU license ([RU 2025688100](https://new.fips.ru/registers-doc-view/fips_servlet?DB=EVM&DocNumber=2025688100&TypeFile=html)). For commercial use, please contact the author: caapel@mail.ru.

----------

## How to install ##
To install, you can use the command:

    pip install stlflib

Or download the repository from [GitHub](https://github.com/caapel/ForecastPowerEnergy) (private access)

----------

## Using ##
The essence of this project and its library is described in detail in the study [***Short-Term Forecasting of Regional Electrical Load Based on XGBoost Model***](https://doi.org/10.3390/en18195144)
> In this file you will not find a detailed description and instructions on how to work with this library; 
> only a description of each of the basic library modules.

### Dependency ##
The **dependency** module (located in the `dependency.py` file) contains a complete list of dependencies.
The module has only one function:
- *print_dependency()* - prints the versions of installed dependencies and the current version of STLFLib

### ServiceDB ### 
The **serviceDB** module (located in the `serviceDB.py` file) contains a set of tools for working with the database:
<br>-------------------------------create---------------------------------<br>
- *generate_volume_df(path)* - generate a dataframe with archived energy consumption data from prepared .xls-files located at `path`
- *get_weather(date)* - generate a weather archive/forecast (outside air temperature) for the specified date with a sampling frequency of 1 hour
- *get_br_feature(date)* - load a BEM (Balancing energy Market) archive/forecast for the specified date
- *get_RSV_rate(date)* - load the unregulated DAM price for the specified date (per month)
- *updating_or_create_df(get_function, filename, start=datetime(2013, 1, 1).date())* - create a new (from the specified date) or replenish an existing database (filename.xlsx) with missing data up to the end of the previous month, returning the resulting dataframe.
- *merge_and_export_DB(total_volume_df, df_weather, df_br_feature, filename='DataBase.xlsx')* - merge dataframes total_volume_df (`Volume.xlsx`), df_weather (`Weather.xlsx`), and df_br_feature (`br_feature.xlsx`) by the 'Date' column into one common database (by default, `DataBase.xlsx`)
<br>-------------------------------service--------------------------------<br>
- *get_empty_daily_df(date)* - Creates an empty dataframe (25 rows: from 0:00 to 24:00) for the specified date (for full temperature interpolation)
- *add_date_scalar(df)* - Adds additional categorical features to the dataframe: Day, Month, Year, WeekDay
- *is_check_DataBase(df)* - Checks database integrity
- *act_pred_reverse(df_br_feature)* - Replaces missing actual (Act) consumption and BR generation values ​​with planned (Pred) values. This function is used to generate a forecast for the current day, when the actual values ​​of `ActCons` and `ActGen` are not available for the entire day.
- *get_files_from_path(path='_raw_Data_TatEnergosbyt')* - Retrieving operational data from the directory (by default, `/_raw_Data_TatEnergosbyt`)
- *update_DataBase(total_oper_df, filename='DataBase.xlsx')* - Updating the database by adding operational data from `total_oper_df`

### Preprocessing ###
The **preprocessing** module (located in the `preprocessing.py` file) contains data preprocessing tools for subsequent transfer of this data to the **core** functions (CatBoostRegressor):
- *get_type_day(df)* - encoding the day type (`TypeDay`) based on the `df.Date` column of the DataTime format. The encoding is performed based on the industrial calendar of the Republic of Tatarstan.
- *get_light(df)* - encoding the light interval (`Light`) based on the `df.Date` column of the DataTime format. The encoding is performed based on the geographic location of the city of Kazan.
- *get_season(df)* - encoding seasonality based on the `df.Date` column of the DataTime format.
- *prepareData(df, lag_start=1, lag_end=7)* - data preprocessing function. Preprocessing includes: adding day type, light interval, seasonality, and energy consumption lag (default 1...7 days)

### Core ###
The **core** module (located in the `core.py` file) is the main class in the library. It is based on `CatBoostRegressor` and has a number of functions:
- *predict_volume(df_general, df_predict, max_depth, learn_period)*
- *get_df_predicted(df_general, max_depth, learn_period, model, date_start, date_end)* - generates a data frame with the predicted energy consumption volume for the specified planning horizon
- *date_str_format(df_predicted)* - generates a date string for the exported xlsx file
- *get_DAM_order(df_general, max_depth, learn_period, model, date_start, date_end)* - a function that generates a DAM order and exports it to xlsx format

### Validating ###
The **validating** helper module (located in the `validating.py` file) is designed to validate the **core** functions:
- *get_df_val_predicted(df_general, df_general_date_index, max_depth, learn_period, model, date_start, date_end)* - function for generating a dataframe with predicted energy consumption volumes for the specified planning horizon, adapted for validation calculations (simulating the absence of 'ActCons' and 'ActGen' data after 7 AM, offline access to the weather forecast and BEM data)
- *get_df_validate(df_general, df_general_date_index, max_depth, learn_period, model, date_start, date_end, logging=True)* - function for validating the model for the specified time interval. Returns a validation dataframe with predicted values.
- *get_df_validate_with_loss(df_validate_result, df_RSV_vs_BR_rate)* - adds a 'loss' column with BEM losses to the resulting dataframe.
- *diff_predict_vs_fact(df_validate_result)* - outputs validation results in table and graph form (Matplotlib object).
- *Grid_Search(df_general, df_general_date_index, max_depth_grid, learn_period_grid, model, date_start, date_end)* - grid search for optimal training period and tree depth.
- *search_result_highlighting(df_search_result)* - highlights the search results of the Grid_Search() function.

### EDA ###
The **EDA** graphics module (located in the `EDA.py` file) is designed to display the results of exploratory data analysis. In developing.
- *draw_learning_curve(df_general, max_depth, model, fontsize=15)* - calculates and plots the learning curve.