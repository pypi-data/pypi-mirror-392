import numpy as np

class LaplaceSolver2D:
    """
    Resuelve la Ecuación de Laplace en 2D en una región cuadrada
    utilizando el Método de Diferencias Finitas (MDF) con el
    algoritmo iterativo de Jacobi.

    Atributos:
        N (int): Número de puntos en cada dirección de la malla (N x N).
        V (np.ndarray): Matriz que representa el potencial eléctrico en la malla.
    """

    def __init__(self, N, V_top=0.0, V_bottom=0.0, V_left=0.0, V_right=0.0):
        """
        Inicializa el solver con las dimensiones de la malla y las condiciones de contorno.

        Args:
            N (int): Tamaño de la malla (N x N).
            V_top (float): Voltaje en la frontera superior.
            V_bottom (float): Voltaje en la frontera inferior.
            V_left (float): Voltaje en la frontera izquierda.
            V_right (float): Voltaje en la frontera derecha.
        """
        if N < 3:
            raise ValueError("N debe ser al menos 3 para tener puntos interiores.")
        self.N = N
        self.V = np.zeros((N, N))

        # Aplicamos las condiciones de contorno fijas (voltajes en los bordes)
        self.V[0, :] = V_top
        self.V[-1, :] = V_bottom
        self.V[:, 0] = V_left
        self.V[:, -1] = V_right

    def solve_jacobi(self, tol=1e-5, max_iter=20000):
        """
        Resuelve la Ecuación de Laplace iterativamente usando el método de Jacobi.

        El método se detiene cuando la diferencia máxima entre la matriz de potencial
        de dos iteraciones consecutivas es menor que la tolerancia `tol`.

        Args:
            tol (float): Criterio de convergencia.
            max_iter (int): Límite de iteraciones para evitar bucles infinitos.

        Returns:
            int: Número de iteraciones realizadas.
        """
        V_old = self.V.copy()
        for i in range(max_iter):
            self.V[1:-1, 1:-1] = 0.25 * (V_old[2:, 1:-1] + V_old[:-2, 1:-1] +
                                        V_old[1:-1, 2:] + V_old[1:-1, :-2])
            
            diff = np.max(np.abs(self.V - V_old))
            if diff < tol:
                return i + 1
            
            V_old = self.V.copy()
        
        return max_iter

    def calculate_electric_field(self):
        """
        Calcula el campo eléctrico E = -grad(V) usando diferenciación numérica.

        Returns:
            tuple[np.ndarray, np.ndarray]: Tupla con las componentes (Ex, Ey).
        """
        Ey, Ex = np.gradient(-self.V)
        return Ex, Ey
