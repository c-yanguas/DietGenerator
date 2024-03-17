import pandas as pd
from datetime import datetime, timedelta
import constants as ct
import os
import sys

def detect_updates():
    """
    Esta func lo que hace es leer dos dataframes, el primero sera el nuevo con los cambios
    y el segundo sera la copia de seguridad, de tal forma que, se comparen los dos y por tanto
    solo se obtengan las filas sobre las cuales se han aplicado cambios.
    Luego simplemente se generaran actualizaciones en base a dichas configuraciones
    Sobre los cambios, no reprocesando innecesariamente.
    """
    # Si no existe el principal, error
    if not os.path.exists(ct.ClientConfiguration.PATH):
        raise FileNotFoundError(f"No se ha detectado el archivo de configuracion de clientes en {ct.ClientConfiguration.PATH}")
    # Si existe el principal, pero no el backup, devolvemos el principal al completo
    elif not os.path.exists(ct.ClientConfiguration.PATH_BACKUP):
        df = pd.read_excel(ct.ClientConfiguration.PATH)
    # Si existen ambos, entonces obtenemos las diferencias entre elk principal
    # y el backup para obtener que filas debemos reprocesar
    else:
        df1 = pd.read_excel(ct.ClientConfiguration.PATH)
        df2 = pd.read_excel(ct.ClientConfiguration.PATH_BACKUP)
        df = pd.concat([df1, df2]).drop_duplicates(keep=False)
        # nos quedamos con el first porque hace referencia a las entradas de la configuraicon mas reciente
        df = df.drop_duplicates(subset=[ct.ClientConfiguration.Column.CLIENT], keep="first")
    
    if len(df) == 0:
        print(f"No existen actualizaciones desde la ultima ejecucion en el fichero {ct.ClientConfiguration.PATH}")
        sys.exit(0)
    return df




def register_update_in_historic(row: pd.Series):
    path_client_historic_data = f"{ct.ClientHistory.PATH}/{row[ct.ClientConfiguration.Column.CLIENT].replace(' ', '_')}.xlsx"
    os.makedirs(os.path.dirname(path_client_historic_data), exist_ok=True)
    # Creamos la nueva fila
    new_row = row.copy(deep=True)
    # Obtener la fecha actual
    current_date = datetime.now().date().strftime(ct.ClientHistory.DATE_FORMAT)
    # current_date = (datetime.now().date() + timedelta(days=1)).strftime('%d/%m/%Y')
    new_row[ct.ClientHistory.Columns.DATE] = current_date
    # Si el cliente ya tenia historico
    if os.path.exists(path_client_historic_data):
        df = pd.read_excel(path_client_historic_data)
        # Generamos nuevas columnas para que si evoluciona el numero de columnas a anotar en el excel, se quede registrado
        for new_col in (set(new_row.index.to_list()) - set(df.columns)):
            df[new_col] = new_row[new_col]
        # Ordenamos los datos para que se puedan concatenar correctamente
        columns_order = ct.get_attr_values_list_from_class(ct.ClientHistory.Columns)
        # Esto es para annadir las columnas Claorias comida ...
        columns_order = columns_order + [col for col in new_row.index if col not in columns_order]
        new_row = new_row[columns_order]
        df = df[columns_order]
        # Obtenemos la ultima actualizacion
        last_update = df.iloc[-1]
        # Si es una actualizacion en un dia nuevo.
        if (not df[ct.ClientHistory.Columns.DATE].isin([current_date]).any()) and (not new_row.equals(last_update)):
            df.loc[len(df)] = new_row
        # Si ya existia un registro para dicho dia se sobreescribe
        else:
            index_to_replace = df[df[ct.ClientHistory.Columns.DATE] == current_date].index
            df.iloc[index_to_replace] = new_row
    # Si el cliente no tenia historico, lo comenzamos con la primera actualizacion
    else:
        df = pd.DataFrame([new_row.values], columns=new_row.index)

    
    # Ordenamos y guardamos
    ordered_columns = [ct.ClientHistory.Columns.DATE] + [col for col in df.columns if col != ct.ClientHistory.Columns.DATE]
    df = df[ordered_columns]
    df.to_excel(path_client_historic_data, index=False)
    return path_client_historic_data
