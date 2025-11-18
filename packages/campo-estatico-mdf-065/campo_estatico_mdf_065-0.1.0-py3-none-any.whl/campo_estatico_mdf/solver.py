import numpy as np

class LaplaceSolver2D:
    """
    Resuelve la Ecuacion de Laplace en 2D usando el Metodo de Diferencias Finitas (MDF)
    y un metodo iterativo de Jacobi.
    """
    def __init__(self, N, v_izquierda, v_derecha, v_arriba, v_abajo):
        """
        Inicializa la malla y aplica las condiciones de contorno.
        (Cumple RF1.1)
        """
        self.N = N
        # Inicializar la matriz V (potencial) con ceros
        self.V = np.zeros((N, N))

        # Aplicar condiciones de contorno fijas (RF1.1)
        self.V[0, :] = v_arriba     # Borde superior
        self.V[-1, :] = v_abajo    # Borde inferior
        self.V[:, 0] = v_izquierda  # Borde izquierdo
        self.V[:, -1] = v_derecha   # Borde derecho
        
        # Guardar las condiciones de contorno para usarlas en las iteraciones
        self.boundaries = (v_arriba, v_abajo, v_izquierda, v_derecha)

    def resolver_jacobi(self, tolerancia=1e-5, max_iteraciones=10000):
        """
        Resuelve el sistema usando el metodo iterativo de Jacobi.
        (Cumple RF1.2 y RF1.3)
        """
        V_old = self.V.copy()
        iteracion = 0
        
        for k in range(max_iteraciones):
            iteracion = k
            
            # Aplicar la formula de Jacobi (MDF)
            # Solo iteramos en los puntos interiores (1 a N-1)
            self.V[1:-1, 1:-1] = 0.25 * (
                V_old[2:, 1:-1] +   # V(i+1, j)
                V_old[:-2, 1:-1] +  # V(i-1, j)
                V_old[1:-1, 2:] +   # V(i, j+1)
                V_old[1:-1, :-2]    # V(i, j-1)
            )

            # Calcular la diferencia maxima para el criterio de convergencia (RF1.3)
            diferencia_max = np.max(np.abs(self.V - V_old))
            
            if diferencia_max < tolerancia:
                break # Convergencia alcanzada
                
            V_old = self.V.copy() # Actualizar V_old para la siguiente iteracion

        return iteracion + 1 # Retorna el numero de iteraciones (para RF2.4)

    def calcular_campo_e(self):
        """
        Calcula el Campo Electrico (E = -grad(V)) usando diferenciacion numerica.
        (Cumple RF1.4)
        """
        # numpy.gradient es ideal para esto (RF1.4)
        # Devuelve (Ey, Ex)
        Ey, Ex = np.gradient(-self.V)
        
        # Nota: Ajustar el signo y el orden segun la convencion E = -grad(V)
        return Ex, Ey
