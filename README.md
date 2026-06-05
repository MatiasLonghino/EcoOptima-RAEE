# Simulador de Gestión y Procesamiento de RAEE

Este proyecto consiste en el desarrollo de un simulador para representar el funcionamiento de un sistema de gestión y procesamiento de RAEE, específicamente monitores y pantallas en desuso.

El sistema permite analizar el comportamiento operativo de una planta de tratamiento a lo largo del tiempo, considerando variables como ingreso de residuos, capacidad de almacenamiento, clasificación, procesamiento, costos operativos y acumulación de inventario.

---

## Objetivo del proyecto

El objetivo principal del simulador es modelar el flujo de monitores y pantallas en desuso dentro de una planta de procesamiento, permitiendo evaluar el desempeño del sistema bajo distintos escenarios operativos.

A través de la simulación, se busca analizar:

- La evolución del inventario en depósito.
- La cantidad de unidades procesadas.
- La clasificación de residuos en CRT, LCD e irrecuperables.
- El impacto de la capacidad de procesamiento.
- El comportamiento de los costos operativos.
- La necesidad de horas extra ante situaciones de alta acumulación.

---

## Descripción general del sistema

El sistema simula el ingreso diario de monitores y pantallas en desuso a una planta de tratamiento.

Cada unidad que ingresa atraviesa una etapa de clasificación inicial, donde se determina si corresponde a:

- Monitor CRT.
- Monitor LCD.
- Unidad irrecuperable.

Luego, las unidades recuperables son derivadas a sus respectivas líneas de procesamiento. El sistema contempla recursos limitados, como servidores de clasificación y procesamiento, además de una capacidad máxima de almacenamiento.

Cuando el inventario alcanza cierto porcentaje de la capacidad total, el sistema puede activar horas extra para aumentar la capacidad operativa del día siguiente.

---

## Tecnologías utilizadas

El proyecto fue desarrollado utilizando las siguientes tecnologías:

- Python
- Streamlit
- NumPy
- Pandas
- Matplotlib / gráficos nativos de Streamlit
- Programación orientada a objetos
- Simulación de eventos discretos

---

## Estructura del proyecto

```text
aplicacion/
│
├── app.py
│
├── simulation/
│   ├── config.py
│   ├── simulator.py
│   ├── statistic.py
│   ├── entities.py
│   └── stores.py
|   └── model.py
│
├── ui/
│   ├── charts.py
│   ├── inputs.py
│   └── metrics.py
│   └── mresults.py
|   └── sidebar.py
|   └── styles.py
|
├── requirements.txt
└── README.md