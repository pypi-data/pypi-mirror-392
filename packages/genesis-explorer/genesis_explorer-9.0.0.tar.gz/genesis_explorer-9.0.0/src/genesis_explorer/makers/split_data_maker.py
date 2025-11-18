"""Módulo que define el patrón de diseño template para la task de separación de datos."""

# Librerías Externas.
from typing import Any, Dict, Tuple, Callable, Optional

import logging

import pandas as pd

# Librerías Internas.
from genesis_explorer.logger.logger import ExperimentLogger
from genesis_explorer.makers.generic_maker import GenericMaker

from genesis_explorer.artifacts.base import Artifact
from genesis_explorer.artifacts.context import ArtifactContextManager


logging.basicConfig(level = logging.INFO,
                    format = "%(asctime)s - %(levelname)s - %(message)s")


class SplitDataMaker(GenericMaker):
    """Clase que funciona como un Template para la task de separación de datos."""

    def __init__(self, cloud_provider: str, cloud_uri: str, project_id: str) -> None:
        """Método de instanciación de clase.
        
        Args:
        ----------
        cloud_provider: str.
            Proveedor de la nube con el que desea establecer conexión de archivos."""
    
        super().__init__(cloud_provider = cloud_provider,
                         cloud_uri = cloud_uri,
                         project_id = project_id)
    
    def split_data_task(self,
                        experiment_name: str,
                        experiment_version: str,
                        location: Optional[str] = "us-east1") -> None:
        """Método estático que define el decorador para la task de separación de datos.
        
        Args:
        ----------
        cloud_provider: str.
            Proveedor de la nube con el que desea establecer conexión de archivos.
        
        project_id: str.
            ID del proyecto de la nube.
        
        cloud_uri: str.
            URI de la nube que representa el folder donde quedarán los artefactos.
            
        experiment_name: str.
            Nombre del experimento.
        
        experiment_version: str.
            Versión del experimento. (Usar semver, eg 1.0.0-test.1)
        
        location: Optional[str].
            Región de la nube donde se ejecutará el experimento.
        
        Returns:
        ----------
        Callable[..., Any].
            Función decorada."""

        def decorator(func: Callable[..., Dict[str, Tuple[pd.DataFrame, ...]]]) -> Callable[..., Any]:
            """Método estático que representa un decorador
            
            Args:
            ----------
            func: Callable[..., Dict[str, Tuple[pd.DataFrame, ...]]].
                Función a decorar.
                
            Returns:
            ----------
            Callable[..., Any].
                Función decorada."""
            
            def wrapper(*args, **kwargs) -> Dict[str, Tuple[pd.DataFrame, ...]]:
                """Función definida por el usuario para representar su separación de datos."""

                exp_version = experiment_version.split(".")[-1]

                with ExperimentLogger(cloud = self.cloud_provider, project_id = self.project_id,
                                      location = location, experiment_name = experiment_name, version = exp_version) as logger:

                    logging.info("Iniciando el proceso de partición de datos...\n")

                    logging.info("Particionando los datos...")

                    artifacts = func(*args, **kwargs)

                    logging.info("Datos obtenidos correctamente.\n")

                    logging.info("Guardando los artefactos versionados...")

                    self.save_artifacts(artifacts = artifacts, experiment_version = experiment_version)

                    logging.info("Artefactos guardados correctamente.\n")

                    logger.experiment_run.log_params({"Step 1": "Datos particionados correctamente."})

                    logging.info("Proceso de partición de datos finalizado correctamente.")

                return artifacts
            
            return wrapper
        
        return decorator