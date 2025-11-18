# campo_estatico_mdf/solver.py
import numpy as np

class LaplaceSolver2D:
    """
    Resuelve la ecuación de Laplace en 2D usando el Método de Diferencias Finitas.
    """
    def __init__(self, N, V_izq, V_der, V_sup, V_inf, tolerancia=1e-5):
        """
        Inicializa el solver.

        Args:
            N (int): Tamaño de la malla (NxN).
            V_izq (float): Voltaje en la frontera izquierda.
            V_der (float): Voltaje en la frontera derecha.
            V_sup (float): Voltaje en la frontera superior.
            V_inf (float): Voltaje en la frontera inferior.
            tolerancia (float): Criterio de convergencia.
        """
        self.N = N
        self.V_izq = V_izq
        self.V_der = V_der
        self.V_sup = V_sup
        self.V_inf = V_inf
        self.tolerancia = tolerancia

        self.V = np.zeros((N, N))
        self.iteraciones = 0

    def aplicar_condiciones_contorno(self):
        """
        Aplica los voltajes de contorno a la malla de potencial.
        La fila 0 corresponde a y=0 (inferior) debido a origin='lower' en imshow.
        """
        self.V[0, :] = self.V_inf
        self.V[-1, :] = self.V_sup
        self.V[:, 0] = self.V_izq
        self.V[:, -1] = self.V_der

    def resolver_gauss_seidel(self):
        """
        Resuelve la ecuación de Laplace usando el método iterativo de Gauss-Seidel.

        Returns:
            tuple: El potencial V (numpy.ndarray) y el número de iteraciones.
        """
        V_anterior = self.V.copy()
        error = self.tolerancia + 1

        self.historial_error = []

        while error > self.tolerancia:
            for i in range(1, self.N - 1):
                for j in range(1, self.N - 1):
                    self.V[i, j] = 0.25 * (self.V[i+1, j] + self.V[i-1, j] + self.V[i, j+1] + self.V[i, j-1])

            error = np.max(np.abs(self.V - V_anterior))
            self.historial_error.append(error)

            V_anterior = self.V.copy()
            self.iteraciones += 1

            if self.iteraciones > 5000:
                print("Advertencia: Se alcanzó el número máximo de iteraciones.")
                break

        return self.V, self.iteraciones, self.historial_error

    def calcular_campo_e(self):
        """
        Calcula el campo eléctrico E a partir del potencial.

        Returns:
            tuple: Componentes Ex y Ey del campo eléctrico (numpy.ndarray).
        """
        Ey, Ex = np.gradient(-self.V)
        return Ex, Ey
