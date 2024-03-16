import pandas as pd
import os
import matplotlib.pyplot as plt


class DietEvolutionPlotter():

    def __init__(self, directorio_registros: str):
        self.directorio_registros = directorio_registros

    def cargar_totales_excel(self, directorios):
        df_totales_entrenamiento = []
        df_totales_descanso = []


        for directorio in directorios:
            # Obtener los nombres de archivo para los DataFrames dentro del directorio de registro
            archivo_entrenamiento = os.path.join(directorio, 'dieta_entrenamiento.xlsx')
            archivo_descanso = os.path.join(directorio, 'dieta_descanso.xlsx')

            # Leer los DataFrames desde los archivos Excel
            df_entrenamiento = pd.read_excel(archivo_entrenamiento)
            df_descanso = pd.read_excel(archivo_descanso)

            # Extraer las filas totales y agregarlas al DataFrame de totales
            total_entrenamiento = df_entrenamiento[df_entrenamiento['Alimento'] == 'Total'].copy(deep=True)
            total_descanso = df_descanso[df_descanso['Alimento'] == 'Total'].copy(deep=True)
            # Obtener la fecha del directorio
            fecha_registro = directorio.split('_')[-1]  
            total_entrenamiento['Dia'] = fecha_registro
            total_descanso['Dia'] = fecha_registro

            if isinstance(df_totales_entrenamiento, list):
                df_totales_entrenamiento = total_entrenamiento
                df_totales_descanso = total_descanso
            else:
                df_totales_entrenamiento = pd.concat([df_totales_entrenamiento, total_entrenamiento], ignore_index=True)
                df_totales_descanso = pd.concat([df_totales_descanso, total_descanso], ignore_index=True)

        # Eliminamos la columna totales
        df_totales_entrenamiento.drop("Alimento", axis=1, inplace=True)
        df_totales_descanso.drop("Alimento", axis=1, inplace=True)


        return df_totales_entrenamiento, df_totales_descanso
    

    def graficar_df(self, df, nombre_df):
        # Convertir la columna 'Dia' a tipo datetime
        df['Dia'] = pd.to_datetime(df['Dia'])

        # Crear el plot
        plt.figure(figsize=(12, 6))  # Ajustar el tamaño horizontal del gráfico

        offset_factor = 0.5  # Factor de desplazamiento para valores cercanos

        # Iterar sobre las columnas (excepto 'Dia') y graficar una línea para cada columna
        for columna in df.columns:
            if columna != 'Dia':
                line, = plt.semilogy(df['Dia'], df[columna], label=columna)  # Usar semilogy para escala logarítmica

                # Encontrar el índice del máximo y mínimo de la columna actual
                idx_max = df[columna].idxmax()
                idx_min = df[columna].idxmin()

                max_value = df[columna][idx_max]
                min_value = df[columna][idx_min]

                # Marcar el máximo y mínimo con puntos del mismo color que la línea
                plt.plot(df['Dia'][idx_max], max_value, marker='o', markersize=8, color=line.get_color())
                plt.plot(df['Dia'][idx_min], min_value, marker='o', markersize=8, color=line.get_color())

                # Mostrar el valor del máximo y mínimo cerca de los puntos
                # Desplazar los valores si están cerca uno del otro
                if abs(max_value - min_value) < 1000:
                    plt.text(df['Dia'][idx_max], max_value + offset_factor, f' Max: {max_value:.2f}', fontsize=10, verticalalignment='bottom')
                    plt.text(df['Dia'][idx_min], min_value - offset_factor, f' Min: {min_value:.2f}', fontsize=10, verticalalignment='top', ha='center')
                else:
                    plt.text(df['Dia'][idx_max], max_value, f' Max: {max_value:.2f}', fontsize=10, verticalalignment='bottom')
                    plt.text(df['Dia'][idx_min], min_value, f' Min: {min_value:.2f}', fontsize=10, verticalalignment='top', ha='center')

        plt.xlabel("Día")
        plt.ylabel("Valor (log scale)")  # Cambiar la etiqueta del eje y
        plt.title(f"Evolución de dieta de {nombre_df}")
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Mover la leyenda a la esquina superior derecha
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()  # Ajustar el diseño del gráfico
        plt.show()

    def graficar_evolucion_totales(self):
        # Obtener una lista de los directorios de registro dentro del directorio raíz
        directorios_registros = [os.path.join(self.directorio_registros, d) for d in os.listdir(self.directorio_registros) 
                                 if os.path.isdir(os.path.join(self.directorio_registros, d))]

        # Cargar las filas totales desde los archivos Excel dentro de los directorios de registro
        df_totales_entrenamiento, df_totales_descanso = self.cargar_totales_excel(directorios_registros)

        self.graficar_df(df_totales_entrenamiento, "entrenamiento")
        self.graficar_df(df_totales_descanso, "descanso")