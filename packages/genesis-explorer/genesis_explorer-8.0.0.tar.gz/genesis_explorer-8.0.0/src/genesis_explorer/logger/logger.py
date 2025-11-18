"""Módulo que se usa para la gestión de experimentos."""

# Librerías Externas.
from __future__ import annotations
from typing import Dict, Any

from genesis_explorer.clients.factory.abstract_factory import CloudFactory


class ExperimentLogger:
    """Clase que se encarga de gestionar los experimentos."""

    def __init__(self, cloud: str, project_id: str, location: str,
                 experiment_name: str, version: int) -> None:
        """Método de instanciación de clase.
        
        Args:
        ----------
        cloud: str.
            Proveedor de la nube con el que desea establecer conexión de archivos.
        
        project_id: str.
            ID del proyecto de la nube.
        
        location: str.
            Región de la nube donde se ejecutará el experimento.
        
        experiment_name: str.
            Nombre del experimento.
        
        version: int.
            Versión del experimento."""

        self.version = version
        self.experiment_name = experiment_name

        self.aiplatform_client = CloudFactory.create_aiplatform_service(cloud_provider = cloud,
                                                                        project_id = project_id,
                                                                        location = location)

    def __enter__(self) -> ExperimentLogger:
        """Método dunder que define la entrada al Context Manager.
        
        Returns:
        ----------
        Logger.
            Instancia de la clase."""

        experiment = self.aiplatform_client.create_experiment(experiment_name = self.experiment_name)
        self.experiment_run = self.aiplatform_client.create_run(run_name = f"experimento-v{self.version}", experiment = experiment)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Método dunder que define la salida al Context Manager.
        
        Args:
        ----------
        exc_type: Any.
            Tipo de excepción.
        
        exc_value: Any.
            Valor de la excepción.
        
        traceback: Any.
            Traza de la excepción."""

        self.aiplatform_client.end_run(experiment_run = self.experiment_run)

    def log_params(self, params: Dict[str, Any]) -> None:
        """Método que se encarga de registrar los parámetros del experimento.

        Args:
        ----------
        params: Dict[str, Any].
            Parámetros del experimento."""

        self.experiment_run.log_params(params)
    
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Método que se encarga de registrar las métricas del experimento.
        
        Args:
        ----------
        metrics: Dict[str, Any].
            Métricas del experimento."""

        self.experiment_run.log_metrics(metrics)
