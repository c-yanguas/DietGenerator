import os
from enum import Enum

DATA_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/../Datos"
CLIENTS_PATH = f"{DATA_PATH}/clientes"
IMAGES_PATH_TMP = f"{DATA_PATH}/tmp.png"

class FoodDatabase():
    # PATH = f"{DATA_PATH}/database_prueba.xlsx"
    PATH = f"{DATA_PATH}/database.xlsx"
    class Sheet():
        CARBOHYDRATES = 'Carbohidratos'
        FATS = 'Grasas'
        PROTEINS = 'Proteinas'
        FRUITS = 'Frutas'
        VEGETABLES = 'Verduras'

    class Column():
        FOOD_NAME = 'Nombre de alimento'
        CARBOHYDRATES = 'carbohidratos'
        PROTEIN = 'proteinas'
        FATS = 'grasas'
        CALORIES = 'calorias'


class ClientConfiguration():
    PATH = f"{DATA_PATH}/Usuarios_General.xlsx"
    PATH_BACKUP = f"{DATA_PATH}/Usuarios_General_backup.xlsx"

    class Column():
        CLIENT = "Cliente"
        CALORIES = "Calorias"
        CARBOHYDRATES = "Carbohidratos"
        FATS = "Grasas"
        PROTEINS = "Proteinas"
        FRUITS = "Frutas"
        VEGETABLES = "Verduras"
        NUM_MEALS = "Numero de comidas"
        VISIBLE_CARBS = "Carbohidratos Visibles"
        VISIBLE_FATS = "Grasas Visibles"
        VISIBLE_PROTEINS = "Proteinas Visibles"
        VISIBLE_FRUITS = "Frutas Visibles"
        VISIBLE_VEGETABLES = "Verduras Visibles"
        WEIGHT = "Peso (KG)"
        Comments = "Comentarios"
        NUM_COMIDA = "Calorías comida"



class ClientDiet():
    PATH = f"{DATA_PATH}/clientes/dietas"
    TEMPLATE = f"{DATA_PATH}/template.xlsx"
    
    class EXCEL_CELLS():
        FIRST_MEAL_FIRST_ROW = 26
        NAME = "C8"
        LAST_UPDATE = "C9"
        TOTAL_CALORIES = "C10"
        CARBS = "C15"
        PROTEINS = "C16"
        FATS = "C17"
        FIRST_MEAL_HEADER = "F24"
        class HEADERS():
            FUENTE_CARBOS = "B25"
            CANTIDAD_CARBOS = "C25"
            FUENTE_PROTEINAS = "D25"
            CANTIDAD_PROTEINAS = "E25"
            FUENTE_GRASAS = "F25"
            CANTIDAD_GRASAS = "G25"
            FUENTE_FRUTA = "H25"
            CANTIDAD_FRUTA = "I25"
            FUENTE_VERDURA = "J25"
            CANTIDAD_VERDURA = "K25"


        


    class Columns:
        FOOD_NUM = "Comida"
        GRAMS = "Gramos"
        MACRONUTRIENT = "Macronutriente"
    
    # Definir las condiciones para pintar cada celda
    COLORS_CRITERIA =  [
        {'color': '008000', 'columna_filtro': Columns.MACRONUTRIENT, 'valor_filtro': FoodDatabase.Sheet.CARBOHYDRATES},
        {'color': 'FFD700', 'columna_filtro': Columns.MACRONUTRIENT, 'valor_filtro': FoodDatabase.Sheet.FATS},
        {'color': 'FFA500', 'columna_filtro': Columns.MACRONUTRIENT, 'valor_filtro': FoodDatabase.Sheet.FRUITS},
        {'color': '00FF00', 'columna_filtro': Columns.MACRONUTRIENT, 'valor_filtro': FoodDatabase.Sheet.VEGETABLES},
        {'color': '8A2BE2', 'columna_filtro': Columns.MACRONUTRIENT, 'valor_filtro': FoodDatabase.Sheet.PROTEINS}
    ]

    # Columnas visibles
    VISIBLE_COLUMNS = [Columns.GRAMS]

    # Columnas para crear index
    INDEX = [Columns.FOOD_NUM, Columns.MACRONUTRIENT, FoodDatabase.Column.FOOD_NAME]




class ClientHistory():
    PATH = f"{DATA_PATH}/clientes/registros"
    DATE_FORMAT = "%d/%m/%Y"

    class Columns():
        DATE = "Fecha"
        CLIENT = ClientConfiguration.Column.CLIENT
        CALORIES = ClientConfiguration.Column.CALORIES  
        CARBOHYDRATES = FoodDatabase.Sheet.CARBOHYDRATES
        FATS = FoodDatabase.Sheet.FATS
        PROTEINS = FoodDatabase.Sheet.PROTEINS
        FRUITS = FoodDatabase.Sheet.FRUITS
        VEGETABLES = FoodDatabase.Sheet.VEGETABLES
        NUM_MEALS = ClientConfiguration.Column.NUM_MEALS
        VISIBLE_CARBS = ClientConfiguration.Column.VISIBLE_CARBS
        VISIBLE_FATS = ClientConfiguration.Column.VISIBLE_FATS
        VISIBLE_PROTEINS = ClientConfiguration.Column.VISIBLE_PROTEINS
        VISIBLE_FRUITS = ClientConfiguration.Column.VISIBLE_FRUITS
        VISIBLE_VEGETABLES = ClientConfiguration.Column.VISIBLE_VEGETABLES
        WEIGHT = ClientConfiguration.Column.WEIGHT
        Comments = ClientConfiguration.Column.Comments


    class ColumnsToPlot():
        # CARBOHYDRATES = FoodDatabase.Sheet.CARBOHYDRATES
        # FATS = ClientConfiguration.Column.FATS
        # PROTEINS = ClientConfiguration.Column.PROTEINS
        # FRUITS = ClientConfiguration.Column.FRUITS
        # VEGETABLES = ClientConfiguration.Column.VEGETABLES
        CALORIES = ClientConfiguration.Column.CALORIES
        WEIGHT = ClientConfiguration.Column.WEIGHT



    class ColumnsMandatoryToPlot():
        WEIGHT = ClientConfiguration.Column.WEIGHT
        DATE = "Fecha"
        CALORIES = ClientConfiguration.Column.CALORIES 
        CLIENT = ClientConfiguration.Column.CLIENT
        CARBOHYDRATES = FoodDatabase.Sheet.CARBOHYDRATES
        FATS = ClientConfiguration.Column.FATS
        PROTEINS = ClientConfiguration.Column.PROTEINS
        FRUITS = ClientConfiguration.Column.FRUITS
        VEGETABLES = ClientConfiguration.Column.VEGETABLES





def get_attr_values_list_from_class(class_object):
    attr_values_list =  [valor for nombre, valor in class_object.__dict__.items() if not nombre.startswith('__') and not callable(valor)]
    return attr_values_list