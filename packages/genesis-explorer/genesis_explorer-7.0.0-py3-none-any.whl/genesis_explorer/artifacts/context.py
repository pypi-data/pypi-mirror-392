"""Módulo que contiene la implementación del Context Manager de los artefactos."""

# Librerías Externas.
from __future__ import annotations
from typing import Any, Tuple

import shutil
import pickle
import tempfile

# Librerías Internas.
from genesis_explorer.artifacts.base import Artifact
from genesis_explorer.clients.factory.abstract_factory import CloudFactory


class ArtifactContextManager:
    """Clase que define el contexto de comunicación con la nube."""

    def __init__(self, cloud_provider: str, project_id: str, cloud_uri: str) -> None:
        """Método de instanciación de clase.
        
        Args:
        ----------
        cloud_provider: str.
            Proveedor de la nube con el que desea establecer conexión de archivos.

        project_id: str.
            ID del proyecto de la nube.
            
        cloud_uri: str.
            URI de la nube que representa el folder donde quedarán los artefactos."""

        self.uri = cloud_uri
        self.storage_client = CloudFactory.create_storage_service(cloud_provider = cloud_provider,
                                                                  project_id = project_id)

    def __enter__(self) -> ArtifactContextManager:
        """Método dunder que permite ingresar al Context Manager."""
        
        self.tmp_dir = tempfile.mkdtemp(prefix = "genesis_temp_dir")
        self.bucket_name, self.base_blob = self.__process_uri(self.uri)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Método dunder que permite salir del Context Manager.
        
        Args:
        ----------
        exc_type: Any.
            Tipo de excepción.
            
        exc_value: Any.
            Valor de excepción.
            
        traceback: Any.
            Traza de excepción."""
        
        shutil.rmtree(self.tmp_dir)

    def upload(self, artifact: Artifact) -> None:
        """Método que implementa la subida de un artefacto a la nube.
        
        Args:
        ----------
        artifact: BaseArtifact.
            Artefacto a subir."""
        
        artifact.write(tmp_dir = self.tmp_dir)
        self.storage_client.upload_file(bucket_name = self.bucket_name,
                                        file_path = f"{self.tmp_dir}/{artifact.name}.pickle",
                                        destination_path = f"{self.base_blob}/{artifact.name}.pickle")
        
    def download(self, file_name: str) -> Artifact:
        """Método que implementa la descarga de un artefacto de la nube.

        Args:
        ----------
        file_name: str.
            Nombre del archivo a descargar (Debe ser el archivo en el blob dado).
        
        Returns:
        ----------
        artifact: BaseArtifact.
            Artefacto descargado."""
        
        self.storage_client.download_file(bucket_name = self.bucket_name,
                                          file_path = f"{self.base_blob}/{file_name}",
                                          destination_path = f"{self.tmp_dir}/{file_name}")

        with open(f"{self.tmp_dir}/{file_name}", "rb") as f:
            return pickle.load(f)       
    
    @staticmethod
    def __process_uri(uri: str) -> Tuple[str, str]:
        """Método que obtiene el bucket y base blob de la URI de la nube.
        
        Returns:
        ----------
        bucket_name: str.
            Nombre del bucket.
        
        base_blob: str.
            Base blob."""
        
        if uri.endswith("/"):
            uri = uri[: -1]

        bucket_name, base_blob = uri.replace("gs://", "").split("/", 1)
        return bucket_name, base_blob
