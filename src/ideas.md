# Prioritarios
- [x] Quesito, calorias y distribucción
- [x] Archivo de configuración dónde se edite la dieta por cliente
- [x] Añadir el numero de calorias a cada comida. Probar con diferente distribucción por comida
- [x] Eliminar las columnas de macros, solo dejar las de nombre comida y gramos
- [x] Crear el histórico, con un gráfico de evolución
- [ ] Sobreescribir las dietas en vez de eliminar y crear.
- [ ] Crear la dieta en base a una plantilla.
- [ ] Crear un exe para distribuir
    1. `!pip install pyinstaller`
    2. `!pyinstaller DietExecutor.py --onefile`
    3. `pyinstaller DietExecutor.py --hidden-import openpyxl.cell._writer`
    4. [Video tutorial](https://www.youtube.com/watch?v=wp2pNVUl3lc&ab_channel=LeMasterTech)


- [ ] Crear un forms sobre preferencias de la dieta mostrando los alimentos disponibles actuales. Esto es con el objetivo de que sea el cliente el que elija sus propios alimentos.
  1. Esto requiere de hacer uso de GCP
- [ ] Crear una APP de tkinter. Esto no sé si merece la pena, sería una interfaz más bonita, pero yo creo que se podría hacer todo más rápido desde el excel
- [ ] Quizás podríamos hacer un excel para el cliente y que seleccione los alimentos según los disponibles en la BBDD.
- [ ] Que se añada la grafica de evolucion de calorias y peso a la dieta solo si ha ocurrido un cambio en el registro del historico
