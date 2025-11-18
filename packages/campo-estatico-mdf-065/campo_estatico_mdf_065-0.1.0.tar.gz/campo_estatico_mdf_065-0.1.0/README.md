# ⚡ Campo Estático 2D (MDF)

**`campo-estatico-mdf`** es una librería Python diseñada para resolver la **Ecuación de Laplace** ($\nabla^2 V = 0$) en dos dimensiones utilizando el **Método de Diferencias Finitas (MDF)** con el método iterativo de **Jacobi**.

Esta herramienta permite simular el potencial eléctrico ($V$) y el campo eléctrico ($\mathbf{E}$) resultante en una región rectangular con condiciones de contorno de Dirichlet (potenciales fijos).

---

## 📦 Instalación

Puedes instalar la librería directamente desde PyPI usando `pip`:

```bash
pip install campo-estatico-mdf
````

### Requisitos

Este paquete requiere:

  * Python 3.9 o superior
  * `numpy` (para las operaciones matriciales)

-----

## 🚀 Uso Básico (Modo Librería)

La clase principal es `LaplaceSolver2D`. Aquí tienes un ejemplo de cómo utilizarla para simular una región con una diferencia de potencial.


```
import numpy as np
from campo_estatico_mdf.solver import LaplaceSolver2D
import matplotlib.pyplot as plt

# 1. Parámetros
N = 50                 # Malla 50x50
V_IZQ = 10.0           # Voltaje Izquierdo (10V)
V_DER = 0.0            # Voltaje Derecho (0V)
V_ARR = 0.0            # Voltaje Superior (0V)
V_ABJ = 0.0            # Voltaje Inferior (0V)
TOLERANCIA = 1e-5

# 2. Inicializar y Resolver
solver = LaplaceSolver2D(
    N,
    v_izquierda=V_IZQ,
    v_derecha=V_DER,
    v_arriba=V_ARR,
    v_abajo=V_ABJ
)

iteraciones = solver.resolver_jacobi(tolerancia=TOLERANCIA)
print(f"Convergencia alcanzada en {iteraciones} iteraciones.")

# 3. Obtener resultados
Potencial_V = solver.V
Ex, Ey = solver.calcular_campo_e()

# 4. Visualización del Potencial
plt.figure(figsize=(8, 6))
plt.title("Potencial Eléctrico V(x, y)")
plt.imshow(Potencial_V, cmap='viridis', origin='lower')
plt.colorbar(label='Potencial (V)')
plt.show()
```

-----

## 💻 Aplicación Streamlit (Web App)

El proyecto incluye una interfaz web interactiva (`app.py`) construida con **Streamlit** que permite a los usuarios modificar las condiciones de contorno y visualizar los resultados del Potencial ($V$) y el Campo Eléctrico ($\mathbf{E}$) en tiempo real.

Para ejecutar la aplicación web:

1.  Instala las dependencias adicionales (si aún no lo has hecho):
    ```bash
    pip install streamlit matplotlib
    ```
2.  Ejecuta la aplicación desde el directorio que contiene `app.py`:
    ```bash
    streamlit run app.py
    ```

-----

## ⚙️ Características Técnicas

  * **Método de Diferencias Finitas (MDF)** para discretizar la Ecuación de Laplace.
  * **Método Iterativo de Jacobi** para resolver el sistema de ecuaciones.
  * Criterio de convergencia basado en la diferencia máxima entre iteraciones sucesivas ($\mathbf{E}$).
  * Cálculo del Campo Eléctrico ($\mathbf{E} = -\nabla V$) usando la función `numpy.gradient`.

-----

## 🤝 Contribución

¡Las contribuciones son bienvenidas\! Si deseas mejorar el rendimiento (por ejemplo, implementando Gauss-Seidel o SOR) o añadir nuevas características:

1.  Haz un *fork* del repositorio.
2.  Crea una nueva *branch* (`git checkout -b feature/nueva-caracteristica`).
3.  Realiza tus cambios y haz *commit* (`git commit -am 'feat: Añadir nueva característica'`).
4.  Haz *push* a la *branch* (`git push origin feature/nueva-caracteristica`).
5.  Abre un *Pull Request*.

-----

```
```
