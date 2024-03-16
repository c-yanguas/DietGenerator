import pandas as pd
import numpy as np
from pandas import DataFrame
import os
import shutil
import time
from HistoricHandler import *
from ExcelHandler import *
import constants as ct
from graphics import *


def recreate_clients_dirs():
    dir_to_clear = ct.CLIENTS_PATH
    # Borrar el directorio si existe
    if os.path.exists(dir_to_clear):
        shutil.rmtree(dir_to_clear)
        # Esperar hasta que el directorio se haya eliminado completamente
        while os.path.exists(dir_to_clear):
            time.sleep(0.01)

    # Crear el directorio nuevamente
    os.makedirs(ct.ClientDiet.PATH, exist_ok=True)
    os.makedirs(ct.ClientHistory.PATH, exist_ok=True)


def database_reader(path_database: str, sheet: str=None):
    if sheet:
        df = pd.read_excel(path_database, sheet_name=sheet)
    else:
        df = pd.read_excel(path_database)
    return df


def print_message_error(metadata: pd.Series, message: str):
    raise ValueError(f"Error en la configuracion del cliente {metadata[ct.ClientConfiguration.Column.CLIENT]}. {message}")


def get_food_database_by_category() -> DataFrame:
    """
    Lee todas las hojas de la 'base de datos', se crea una nueva columna llamada type
    y se concatenan all dataframes en uno solo

    Se devuelve el dataframe concatenado
    """
    path_database = ct.FoodDatabase.PATH
    sheets_to_read = [getattr(ct.FoodDatabase.Sheet, attr) for attr in dir(ct.FoodDatabase.Sheet) if not callable(getattr(ct.FoodDatabase.Sheet, attr)) and not attr.startswith("__")]
    final_df = None
    for sheet_to_read in sheets_to_read:
        df = pd.read_excel(path_database, sheet_name=sheet_to_read)
        df[ct.ClientDiet.Columns.MACRONUTRIENT] = sheet_to_read

        if final_df is None:
            final_df = df
        else:
            final_df = pd.concat([final_df, df], ignore_index=True)

    return final_df


def check_macronutrients_percentage(client_config: pd.Series, columns_to_check:list):
    """
    Se comprueba si la suma entre all macronutrientes es 1 y si cada uno de ellos es positivo.
    """
    sum_result = np.round(client_config[columns_to_check].sum(), 0)

    if any(client_config[columns_to_check] < 0):
        raise ValueError(f"Error, incorrect configuration, negative percentage values found for the row:\n {client_config}")

    if sum_result != 1:
        raise ValueError(f"Error, configuracion erronea, la suma de los porcentages es diferente a 1 ({sum_result}) para la fila:\n {client_config}")

    negative_columns = client_config[columns_to_check][client_config[columns_to_check] < 0].index.to_list()
    if len(negative_columns) > 0:
        raise ValueError(f"Error, configuracion erronea, valores porcentuales negativos encontrados en la(s) columna(s): {', '.join(negative_columns)} for the row:\n {client_config}")

    return True


def get_macronutrients_distribution(client_config: pd.Series):
    columns_to_check = ct.get_attr_values_list_from_class(ct.FoodDatabase.Sheet)
    check_macronutrients_percentage(client_config, columns_to_check)
    macronutrients_distribution = {column: client_config[column] for column in columns_to_check}
    return macronutrients_distribution


def get_cuantity_in_grams(df_food: DataFrame, desired_calories: float, macronutrients_distribution: dict):
    """
    Se obtiene un nuevo dataframe de toda la BBDD con la columnas Gramos
    que indica la cantidad de gramos para cada alimento de la base de datos
    que corresponde a desired_calories
    """

    df = df_food.copy(deep=True)
    final_df = pd.DataFrame()
    for macronutrient in macronutrients_distribution.keys():
        # Filtramos los alimentos correspondientes al macronutriente
        df_macronutrient = df[df[ct.ClientDiet.Columns.MACRONUTRIENT] == macronutrient].copy(deep=True)
        # Obtenemos las desired_calories correspondientes al macronutriente
        desired_carlories_macronutrient = macronutrients_distribution[macronutrient] * desired_calories
        # Obtenemos los alimentos y cantidades correspondientes a esos alimentos
        df_macronutrient["Gramos"] = np.round((desired_carlories_macronutrient / df_food[ct.FoodDatabase.Column.CALORIES] * 100), 2).astype(np.int32)
        final_df = pd.concat([final_df, df_macronutrient])
    return final_df


def get_calories_per_meal(row: pd.Series):
    """
    Obtener el numero de calorias por comidas.
    Si estan definidas las columnas comida i hasta las N comidas pedidas
    entonces se coge dicha distribucion.
    Si solo esta definida alguna pero no todas, se lanza un error.
    Si no esta definida ninguna se hace num_calorias/num_comidas y eso es el numero
    de calorias por comida.
    """
    num_meals = row[ct.ClientConfiguration.Column.NUM_MEALS]
    # Get how the meals are distributed
    distribution_food_calories_names = [f"{ct.ClientConfiguration.Column.NUM_COMIDA} {i}" for i in range(1, num_meals + 1)]

    # Check if all names exist in the row
    all_foods_exist = all(comida in row.index for comida in distribution_food_calories_names)
        
    # si existen todas las columnas
    if all_foods_exist:
        all_food_are_undefined = all(pd.isna(row[comida]) for comida in distribution_food_calories_names)
        any_food_is_undefined = any(pd.isna(row[comida]) for comida in distribution_food_calories_names)
        # 1-Comprobar si ninguna comida esta definida, en cuyo caso se hace una dist uniforme
        if all_food_are_undefined:
            calories_per_meal = [row[ct.ClientConfiguration.Column.CALORIES] / num_meals] * num_meals
        # 2-Comprobar si solo algunas comidas estan definidas, en cuyo caso pedimos que se completen o se borren
        elif any_food_is_undefined:
            message_error = f"""Has definido calorias para alguna comida, pero no para las {num_meals} indicadas.
            Si quieres una distribucion uniforme de {row[ct.ClientConfiguration.Column.CALORIES]} / {num_meals}, es decir, de: ({row[ct.ClientConfiguration.Column.CALORIES] / num_meals})
            no rellenes ninguna columna de {distribution_food_calories_names}.
            """
            print_message_error(row, message_error)
        # 3-Comprobar si la suma de las comidas definidas suma la cantidad de calorias indicada
        else:
            calories_per_meal = row[distribution_food_calories_names].to_list()
            sum_calories = sum(calories_per_meal)
            calorias_en_dieta = row[ct.ClientConfiguration.Column.CALORIES]
            if not (sum_calories == calorias_en_dieta):
                print_message_error(row, f"La suma de las columnas {distribution_food_calories_names} suman {sum_calories} pero has definido una dieta de {calorias_en_dieta}")

    calories_per_meal = [int(meal_calories) for meal_calories in calories_per_meal]
    return calories_per_meal


def filter_food(client_config: pd.Series, df_food: pd.DataFrame):
    # Filtrar las columnas que contienen la palabra "Visibles"
    alimentos_visibles_por_macro = client_config.filter(like='Visibles')
    # Inicializar una lista para almacenar los nombres
    filtered_food = []

    # Agregar los nombres de cada columna a la lista
    for alimentos_visibles_macro in alimentos_visibles_por_macro:
        filtered_food = filtered_food + alimentos_visibles_macro.split(",")
    # Eliminar los espacios en blanco de izquierda o derecha de los alimentos
    filtered_food = [food.strip() for food in filtered_food]
    # Comprobar que todos los alimentos definidos estan en la BBDD
    # Encontrar los elementos ausentes en la columna
    alimentos_inexistentes = [food for food in filtered_food if food not in df_food[ct.FoodDatabase.Column.FOOD_NAME].tolist()]

    if len(alimentos_inexistentes) > 0:
        print_message_error(client_config, f"Los alimentos {alimentos_inexistentes}, no estan definidos en la base de datos")
    else:
        client_df_food = df_food.copy(deep=True)
        client_df_food = client_df_food[client_df_food[ct.FoodDatabase.Column.FOOD_NAME].isin(filtered_food)]
    return client_df_food


def generate_excel_diet(df_meal: pd.DataFrame, client_configuration: pd.Series):
    # Get relevant client data
    client_name =  client_configuration[ct.ClientConfiguration.Column.CLIENT]
    current_date = datetime.now().date().strftime(ct.ClientHistory.DATE_FORMAT)
    total_calories = client_configuration[ct.ClientConfiguration.Column.CALORIES]
    num_meals = client_configuration[ct.ClientConfiguration.Column.NUM_MEALS]
    # Obtenemos las comidas por nombre y calorias
    unique_meals = sorted(df_meal['Comida'].unique())
    # 1-Crear una copia de la plantilla excel
    client_fname = f"{ct.ClientDiet.PATH}/{client_name.replace(' ', '_')}_diet.xlsx"
    copiar_archivo(ct.ClientDiet.TEMPLATE, client_fname)
    # 2-Generar el minimo número de filas posibles
    min_num_rows_per_meal = df_meal[df_meal['Comida']==unique_meals[0]].groupby(ct.ClientDiet.Columns.MACRONUTRIENT).size().max()
    copiar_fila_n_veces(client_fname, ct.ClientDiet.EXCEL_CELLS.FIRST_MEAL_FIRST_ROW, ct.ClientDiet.EXCEL_CELLS.FIRST_MEAL_FIRST_ROW + 1, min_num_rows_per_meal - 1)
    # 3-Generar el numero de comidas
    # el + 2 es por las cabeceras
    # el -1 es porque si por ejemplo ocupa 12 cada comida, de la 24 a la 35 incluidas, son 12
    size_per_meal = 2 + min_num_rows_per_meal
    # empezamos en 1 porque la primera comida ya esta
    for num_meal in range(num_meals - 1):
        # el -2 es porque queremos copiar la cabecera de comida y las cabeceras de fuentes de macros
        first_row_to_copy = (ct.ClientDiet.EXCEL_CELLS.FIRST_MEAL_FIRST_ROW - 2) + size_per_meal * num_meal
        # el -1 es porque queremos copiar hasta la ultima fila pero si sumasemos size_per_meal se iria a la primera de la siguiente comida
        last_row_to_copy = first_row_to_copy + size_per_meal - 1
        copy_rows_below(client_fname, first_row_to_copy, last_row_to_copy)
    # 4-Rellenar datos
    # por celdas
    escribir_en_celda(client_fname, ct.ClientDiet.EXCEL_CELLS.NAME,           client_name)
    escribir_en_celda(client_fname, ct.ClientDiet.EXCEL_CELLS.LAST_UPDATE,    current_date)
    escribir_en_celda(client_fname, ct.ClientDiet.EXCEL_CELLS.TOTAL_CALORIES, total_calories)
    escribir_en_celda(client_fname, ct.ClientDiet.EXCEL_CELLS.CARBS,          client_configuration[ct.ClientConfiguration.Column.CALORIES] * client_configuration[ct.ClientConfiguration.Column.CARBOHYDRATES])
    escribir_en_celda(client_fname, ct.ClientDiet.EXCEL_CELLS.FATS,           client_configuration[ct.ClientConfiguration.Column.CALORIES] * client_configuration[ct.ClientConfiguration.Column.FATS])
    escribir_en_celda(client_fname, ct.ClientDiet.EXCEL_CELLS.PROTEINS,       client_configuration[ct.ClientConfiguration.Column.CALORIES] * client_configuration[ct.ClientConfiguration.Column.PROTEINS])
    # por columnas
    for num_meal, meal_name in enumerate(unique_meals):
        shift_cell = 1 + size_per_meal * num_meal
        # 1-Escribimos la comida junto con las calorias asociadas
        escribir_en_celda(
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.FIRST_MEAL_HEADER, shift_cell - 1),
            meal_name
        )
        # 2-filtramos los datos para dicha comida
        meal_n = df_meal[df_meal[ct.ClientDiet.Columns.FOOD_NUM] == meal_name]
        # 3-Rellenamos el resto de datos para esa comida en el excel
        # def write_column_to_excel(dataframe, column_name, excel_file_path, start_cell):
        # Filtramos los datos para cada macronutriente
        # el + 1 es porque las cells son el valor de la cabecera, por lo que + 1 es el primer valor de la celda
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.CARBOHYDRATES],
            ct.FoodDatabase.Column.FOOD_NAME,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.FUENTE_CARBOS, shift_cell)
        )
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.FATS],
            ct.FoodDatabase.Column.FOOD_NAME,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.FUENTE_GRASAS, shift_cell)
        )
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.PROTEINS],
            ct.FoodDatabase.Column.FOOD_NAME,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.FUENTE_PROTEINAS, shift_cell)
        )
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.VEGETABLES],
            ct.FoodDatabase.Column.FOOD_NAME,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.FUENTE_VERDURA, shift_cell)
        )
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.FRUITS],
            ct.FoodDatabase.Column.FOOD_NAME,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.FUENTE_FRUTA, shift_cell)
        )
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.CARBOHYDRATES],
            ct.ClientDiet.Columns.GRAMS,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.CANTIDAD_CARBOS, shift_cell)
        )
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.FATS],
            ct.ClientDiet.Columns.GRAMS,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.CANTIDAD_GRASAS, shift_cell)
        )
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.PROTEINS],
            ct.ClientDiet.Columns.GRAMS,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.CANTIDAD_PROTEINAS, shift_cell)
        )
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.VEGETABLES],
            ct.ClientDiet.Columns.GRAMS,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.CANTIDAD_VERDURA, shift_cell)
        )
        write_column_to_excel(
            meal_n[meal_n[ct.ClientDiet.Columns.MACRONUTRIENT] ==  ct.ClientConfiguration.Column.FRUITS],
            ct.ClientDiet.Columns.GRAMS,
            client_fname,
            suma_celda_y_entero(ct.ClientDiet.EXCEL_CELLS.HEADERS.CANTIDAD_FRUTA, shift_cell)
        )

    return client_fname




def generate_diet_from_updates(diet_config_df: pd.DataFrame, recreate_client_dirs=True) -> pd.DataFrame:
    # 1-Read the food database
    df_food = get_food_database_by_category()

    # 2-Generate diet for each client based on the configuration
    for i, row in diet_config_df.iterrows():
        client_name = row[ct.ClientConfiguration.Column.CLIENT]
        print(f"Generating diet for client {client_name}")
        meal_dataframe = pd.DataFrame()
        # 1-check macronutrients_distribution and get it (just to generate the pie)
        macronutrients_distribution = get_macronutrients_distribution(row)

        # 2-Obtain the calories for each meal
        calories_per_meal = get_calories_per_meal(row)

        # 3-Filter the food that these cliente can see
        client_df_food = filter_food(row, df_food)

        # 4-Generates the diet for the client
        for i, calories_in_meal in enumerate(calories_per_meal):
            df_meal = get_cuantity_in_grams(client_df_food, calories_in_meal, macronutrients_distribution)

            # Add the meal number as a new column
            df_meal[ct.ClientDiet.Columns.FOOD_NUM] = f"{i + 1} - {int(calories_in_meal)} Calorías"
            meal_dataframe = pd.concat([meal_dataframe, df_meal])

        # 3-Crear una copia de la plantilla excel
        client_fname = generate_excel_diet(meal_dataframe, row)
        # 4-Crear el quesito y guardarlo en el excel
        path_pie_image = generar_grafico(macronutrients_distribution)
        insertar_imagen_en_excel(client_fname, path_pie_image, celda="N2")
        # 5-Registrar la actualizacion, si es que la hubo para ese cliente
        path_historic_client_data = register_update_in_historic(row)
        # 6-Actualizar la grafica de evolucion
        graphic_client_evolution = graficar_evolucion_dieta(path_historic_client_data)
        # 7-Insertar imagen de evolucion en la dieta
        insertar_imagen_en_excel(client_fname, graphic_client_evolution, celda="N22")





def generate_diets(recreate_client_dirs=False):
    # 1-get dataframe config updates
    df_config = detect_updates()
    # 2-Reset client folder
    if recreate_client_dirs:
        recreate_clients_dirs()
    # 3-Generate diets only for those clients that have updates
    generate_diet_from_updates(df_config)
    # 4-Generamos un backup para la proxima vez que sea modificado el excel
    origen = ct.ClientConfiguration.PATH
    destino = ct.ClientConfiguration.PATH_BACKUP
    copiar_archivo(origen, destino)
    print(f"Datos procesados exitosamente")

