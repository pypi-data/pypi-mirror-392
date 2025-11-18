""""""


from typing import List, Dict, Any

from genesis_explorer.artifacts.base import Artifact
from genesis_explorer.artifacts.context import ArtifactContextManager


class GenericMaker:
    """Clase que se encarga de gestionar los artefactos."""

    def __init__(self, cloud_provider: str, cloud_uri: str, project_id: str) -> None:
        """Método de instanciación de clase.
        
        Args:
        ----------
        cloud_provider: str.
            Proveedor de la nube con el que desea establecer conexión de archivos."""
        
        self.cloud_uri = cloud_uri
        self.project_id = project_id
        self.cloud_provider = cloud_provider

        self.artifact_context_manager = ArtifactContextManager(cloud_provider = cloud_provider,
                                                               cloud_uri = cloud_uri,
                                                               project_id = project_id)

    def load_artifacts(self, artifacts: Dict[str, str]) -> Dict[str, Any]:
        """Método que se encarga de cargar los artefactos.
        
        Args:
        ----------
        artifact_names: List[str].
            Nombres de los artefactos a cargar."""
                
        loaded_artifacts = {}
        with self.artifact_context_manager as manager:
            for artifact_name, artifact_filename in artifacts.items():
                artifact = manager.download(file_name = f"{artifact_filename}.pickle")
                loaded_artifacts[artifact_name] = artifact.content

        return loaded_artifacts
    
    def save_artifacts(self, artifacts: Dict[str, Any], experiment_version: str) -> None:
        """Método que se encarga de guardar los artefactos.
        
        Args:
        ----------
        artifacts: Dict[str, Any].
            Diccionario con los artefactos a guardar."""
        
        with self.artifact_context_manager as manager:
            for artifact_name, artifact_content in artifacts.items():

                artifact = Artifact(name = artifact_name,
                                    version = experiment_version,
                                    content = artifact_content)

                artifact.write(tmp_dir = manager.tmp_dir)
                manager.upload(artifact = artifact)
