"""Módulo que contiene la implementación del contrato nominal de los artefactos."""

# Librerías Externas.
from typing import Any

import pickle


class Artifact:
    """Clase que representa el contrato nominal de los artefactos."""

    def __init__(self,
                 name: str,
                 version: str,
                 content: Any) -> None:
        """Método de instanciación de clase.
        
        Args:
        ----------
        name: str.
            Nombre del archivo.

        version: str.
            Versión del artefacto.

        content: Any.
            Contenido del artefacto."""
        
        self.name = name
        self.version = version
        self.content = content

    def write(self, tmp_dir: str) -> None:
        """Método que implementa el contrato de escritura local del artefacto.
        
        Args:
        ----------
        tmp_dir: str.
            Directorio temporal que dictamina el Context Manager."""

        with open(f"{tmp_dir}/{self.name}.pickle", "wb") as f:
            pickle.dump(self, f)
    
    def read(self, tmp_dir: str) -> Any:
        """Método que implementa el contrato de lectura del artefacto.
        
        Args:
        ----------
        tmp_dir: str.
            Directorio temporal que dictamina el Context Manager.
        
        Returns:
        ----------
        artifact: Any.
            Artefacto de un tipo específico."""

        with open(f"{tmp_dir}/{self.name}.pickle", "rb") as f:
            return pickle.load(f)
        
    def __repr__(self) -> str:
        """Método que implementa el contrato de representación del artefacto.
        
        Returns:
        ----------
        str.
            Representación del artefacto."""

        return f"Artifact(name = {self.name}, version = {self.version})"
