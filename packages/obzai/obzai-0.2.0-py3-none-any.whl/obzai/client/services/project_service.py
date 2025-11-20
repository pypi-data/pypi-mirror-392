# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional, Dict, Literal, List
from dataclasses import asdict
import httpx

# API Config
from obzai.client.configs.api_config import APIConfig

# Custom exceptions
from obzai.client.schemas.exceptions import ProjectInitError

# Custom dataclasses & types
from obzai.data_inspection.schemas.dataclasses import DataInspectorMeta
from obzai.client.schemas.dataclasses import ProjectMeta
from obzai.client.schemas.types import MLTask


class _ProjectService:
    """
    The service handles project initilization
    and project-related credentials storage.
    """
    def __init__(self, session: httpx.Client):
        """
        Constructs an instance of the ProjectService class.

        Args:
            session: A session object from the ObzClient.
        """
        self.session = session
        
        self._project_ready: bool = False
        self._project_id: Optional[int] = None
        self._data_inspector_local2remote_id = None
        self._ml_task: Optional[MLTask] = None

    @property
    def project_ready(self) -> bool:
        """
        Returns bool flag indicating whether project
        is ready or not.
        """
        return self._project_ready

    @property
    def project_meta(self) -> ProjectMeta:
        """
        Returns a project ID and ML Task.
        """
        if (
            self._project_id is None
            or
            self._ml_task is None
            ):
            raise RuntimeError("Project is not initialized yet.")
        else:
            return ProjectMeta(
                project_id=self._project_id,
                ml_task=self._ml_task,
                data_inspector_local2remote_id = self._data_inspector_local2remote_id
                )

    def init_project(
            self, 
            api_key: str, 
            project_name: str, 
            ml_task: MLTask,
            index2name: Optional[Dict[int, str]] = None,
            inspectors_metadata: Optional[List[DataInspectorMeta]] = None
            ) -> None:
        """
        The method attempts to initialize a project by sending appropriate request to the backend.

        Args:
            api_key: (string) User's API key to Obz.ai API.
            project_name: (string) Desired project name.
            ml_task: (Enum Type) Desired ML Task.
            index2name: (dict) Optional mapping of prediction indices to corresponding names, e.g. class names.
            inspectors_metadata: (list[DataInspectorMeta]) Optional list containing metadata objects from data inspectors.
        """
        # (1) Construct a request payload
        if inspectors_metadata is not None:
            metadata_dicts = [asdict(meta) for meta in inspectors_metadata]
        else:
            metadata_dicts = None
        
        payload = {
            "project_name": project_name,
            "ml_task": ml_task.value,
            "index2name": index2name,
            "inspectors_metadata": metadata_dicts
        }

        # (2) Construct a request header with API token
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        # (3) Try to send a project initialization request
        try:
            response = self.session.post(
                APIConfig.get_url("init_project"), json=payload, headers=headers, timeout=100
                )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ProjectInitError(f"The project initialization failed with status code: {e.response.status_code}.")
        except Exception as e:
            raise ProjectInitError(f"The project initialization failed: {e}") from e

        # (4) Convert response to a dictionary
        data = response.json()
        if data.get("status") == "success":
            self._project_ready = True
            self._project_id = data.get("project_id")
            self._data_inspector_local2remote_id = data.get("data_inspector_local2remote_id")
            self._ml_task = ml_task
            return
        elif data.get("status") == "failed":
            self._project_ready = False
            self._project_id = None
            self._data_inspector_local2remote_id = None
            self._ml_task = None
            raise ProjectInitError("The project wasn't initialized, since it already exists! Try different name.")
        else:
            self._project_ready = False
            self._project_id = None
            self._data_inspector_local2remote_id = None
            self._ml_task = None
            raise KeyError("A response from the backend should contain a 'status' field.")