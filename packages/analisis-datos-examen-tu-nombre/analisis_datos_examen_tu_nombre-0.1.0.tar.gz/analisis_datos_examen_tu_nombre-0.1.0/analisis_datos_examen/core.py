import pandas as pd
import numpy as np

class AnalizadorDatos:
    def __init__(self, ruta_csv):
        self.df = pd.read_csv(ruta_csv)

    def limpiar_datos(self):
        """
        Realiza la imputación de valores nulos según la lógica del ejercicio.
        """
        # 1. Imputar Edad con la mediana
        if 'Edad' in self.df.columns:
            self.df['Edad'] = self.df['Edad'].fillna(self.df['Edad'].median())

        # 2. Imputar Ciudad con probabilidad proporcional
        if 'Ciudad' in self.df.columns:
            city_probs = self.df['Ciudad'].value_counts(normalize=True)
            self.df['Ciudad'] = self.df['Ciudad'].apply(
                lambda x: np.random.choice(city_probs.index, p=city_probs.values) if pd.isnull(x) else x
            )

        # 3. Imputar Género con probabilidad proporcional
        if 'Género' in self.df.columns:
            genero_probs = self.df['Género'].value_counts(normalize=True)
            self.df['Género'] = self.df['Género'].apply(
                lambda x: np.random.choice(genero_probs.index, p=genero_probs.values) if pd.isnull(x) else x
            )

        # 4. Corregir Nombres nulos
        if 'Nombre' in self.df.columns:
            self.df['Nombre'] = self.df['Nombre'].fillna('Desconocido')

        # 5. Imputar Ingresos y Gastos con la mediana
        if 'Ingresos Mensuales' in self.df.columns:
            self.df['Ingresos Mensuales'] = self.df['Ingresos Mensuales'].fillna(self.df['Ingresos Mensuales'].median())
        
        if 'Gastos Mensuales' in self.df.columns:
            self.df['Gastos Mensuales'] = self.df['Gastos Mensuales'].fillna(self.df['Gastos Mensuales'].median())

        return self.df

    def calcular_promedios_agrupados(self):
        """Calcula ingreso y gasto promedio por ciudad y género."""
        resultados = []
        for ciudad in self.df['Ciudad'].unique():
            datos_ciudad = self.df[self.df['Ciudad'] == ciudad]
            ing_prom = datos_ciudad['Ingresos Mensuales'].mean()
            gas_prom = datos_ciudad['Gastos Mensuales'].mean()
            resultados.append(f"Ciudad: {ciudad} - Ingreso Prom: {ing_prom:.2f} - Gasto Prom: {gas_prom:.2f}")
        
        return resultados

    def obtener_totales(self):
        ingresos = self.df['Ingresos Mensuales'].sum()
        gastos = self.df['Gastos Mensuales'].sum()
        return ingresos, gastos

    def obtener_extremos_ingresos(self):
        idx_max = self.df['Ingresos Mensuales'].idxmax()
        idx_min = self.df['Ingresos Mensuales'].idxmin()
        return self.df.loc[idx_max], self.df.loc[idx_min]

    def calcular_saldo(self):
        self.df['Saldo Mensual'] = self.df['Ingresos Mensuales'] - self.df['Gastos Mensuales']
        # Corrección de saldo negativo a positivo (absolute) como hiciste en el notebook
        self.df['Saldo Mensual'] = self.df['Saldo Mensual'].apply(lambda x: x + abs(x) if x < 0 else x)
        return self.df['Saldo Mensual'].mean()