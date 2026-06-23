# test_simulation.py

import unittest
from unittest.mock import patch

import numpy as np

from simulation.config import SimulationConfig
from simulation.simulator import Simulator


class PlantModelWithoutProcessing:
    """
    Modelo ficticio usado solo en pruebas.

    Reemplaza temporalmente PlantModel para evitar que triage,
    CRT o LCD retiren equipos del depósito durante la prueba.
    Así se garantiza que el procesamiento sea igual a 0.
    """

    def __init__(self, *args, **kwargs):
        pass


class TestStorageCapacity(unittest.TestCase):
    """
    Pruebas automáticas de la capacidad física del depósito.
    """

    def test_full_storage_blocks_all_arrivals(self):
        """
        Prueba controlada de aceptación:

        - Capacidad: 300
        - Stock inicial: 300
        - Llegadas totales: 45
          (25 urbanas + 20 por convenios)
        - Procesamiento: 0

        Resultado esperado:
        - Inventario posterior: 300
        - Admitidos: 0
        - Bloqueados: 45
        - Sin violaciones de capacidad
        """

        config = SimulationConfig(
            days=1,
            inventory_capacity=300,
            initial_inventory=300,
            arrival_lambda=45,
            triage_servers=1,
            crt_servers=1,
            lcd_servers=1,
            workday_minutes=480,
            overtime_minutes=0
        )

        # Se reemplaza PlantModel para impedir procesamiento.
        # También se fuerza Poisson a devolver exactamente 45.
        with patch(
            "simulation.simulator.PlantModel",
            PlantModelWithoutProcessing
        ), patch(
            "simulation.simulator.np.random.poisson",
            return_value=45
        ) as mock_poisson:

            results = Simulator(config).run()

        # Verifica que la llegada total simulada haya sido 45.
        mock_poisson.assert_called_once_with(45)

        # Inventario físico luego de llegadas y sin procesamiento.
        self.assertEqual(
            results["FINAL_STORAGE_INVENTORY"],
            300
        )

        # Ningún equipo puede ser admitido porque ya no hay espacio.
        self.assertEqual(
            results["TOTAL_ADMITTED"],
            0
        )

        # Los 45 equipos llegados quedan registrados como bloqueados.
        self.assertEqual(
            results["TOTAL_REJECTED"],
            45
        )

        # El máximo físico registrado debe ser exactamente 300.
        self.assertEqual(
            results["MAX_STORAGE_INVENTORY"],
            300
        )

        # No debe detectarse ninguna violación.
        self.assertEqual(
            results["CAPACITY_VIOLATIONS"],
            0
        )

        self.assertTrue(
            results["CAPACITY_OK"]
        )

    def test_capacity_is_respected_in_multiple_replications(self):
        """
        Ejecuta varias réplicas y verifica que, en ningún día,
        el inventario físico del depósito supere su capacidad.
        """

        replicas = 20

        config = SimulationConfig(
            days=30,
            inventory_capacity=300,
            initial_inventory=100,
            arrival_lambda=45,
            triage_servers=1,
            crt_servers=2,
            lcd_servers=1,
            workday_minutes=480,
            overtime_minutes=120
        )

        for replica in range(replicas):

            # Hace reproducible cada réplica.
            np.random.seed(replica)

            # Se evita el procesamiento para probar el peor caso:
            # los equipos se acumulan y el depósito puede llenarse.
            with patch(
                "simulation.simulator.PlantModel",
                PlantModelWithoutProcessing
            ):
                results = Simulator(config).run()

            with self.subTest(replica=replica):

                self.assertLessEqual(
                    results["MAX_STORAGE_INVENTORY"],
                    config.inventory_capacity
                )

                self.assertEqual(
                    results["CAPACITY_VIOLATIONS"],
                    0
                )

                self.assertTrue(
                    results["CAPACITY_OK"]
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
