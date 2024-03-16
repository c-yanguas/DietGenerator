from DietHandler import *
import sys


if __name__ == "__main__":

    # El valor por defecto para recreate_client_dirs es False
    recreate_client_dirs = False

    # Si se proporciona un argumento en la línea de comandos, lo utilizamos como valor de recreate_client_dirs
    if len(sys.argv) > 1:
        recreate_client_dirs = sys.argv[1].lower() == "true"

    # Llamamos a la función con el valor correspondiente
    generate_diets(recreate_client_dirs)
