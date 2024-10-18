#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""
Client to interact with databricks apis
"""
import json
import traceback

from requests import HTTPError

from metadata.ingestion.source.database.databricks.client import (
    API_TIMEOUT,
    DatabricksClient,
)
from metadata.ingestion.source.database.unitycatalog.models import (
    LineageColumnStreams,
    LineageTableStreams,
)
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()
TABLE_LINEAGE_PATH = "/lineage-tracking/table-lineage"
COLUMN_LINEAGE_PATH = "/lineage-tracking/column-lineage/get"
TABLES_PATH = "/unity-catalog/tables"
JOB_PATH = "/jobs/get"
WORKSPACE_PATH = "/workspace/list"


class UnityCatalogClient(DatabricksClient):
    """
    UnityCatalogClient creates a Databricks connection based on DatabricksCredentials.
    """
    def get_table_lineage(self, table_name: str) -> LineageTableStreams:
        """
        Method returns table lineage details
        """
        try:
            data = {
                "table_name": table_name,
                "include_entity_lineage": True
            }

            response = self.client.get(
                f"{self.base_url}{TABLE_LINEAGE_PATH}",
                headers=self.headers,
                data=json.dumps(data),
                timeout=API_TIMEOUT,
            ).json()
            if response:
                return LineageTableStreams(**response)

        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(exc)

        return LineageTableStreams()
    
    def get_unique_notebook_paths(job_details) -> list[str]:
        try:
            tasks = job_details.get("settings", {}).get("tasks", [])
            notebook_paths = {"/".join(task["notebook_task"]["notebook_path"].split("/")[:3])
                                for task in tasks if "notebook_task" in task and "notebook_path" in task["notebook_task"]}
            return list(notebook_paths)
        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(exc)
            return []

    def get_job_by_id(self, job_id) -> dict:
        """
        Method returns the job details by the specified job_id
        """
        try:
            params = {
                "job_id": job_id
            }
            response = self.client.get(
                self.job_url,
                params=params,
                headers=self.headers,
                timeout=API_TIMEOUT,
            )
            if response.status_code != 200:
                return None
            return response.json()

        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(exc)
    
    def get_workspace_objects_info(self, workspace_path) -> dict:
        """
        Method returns the job details by the specified job_id
        """
        try:
            params = {
                "path": workspace_path
            }
            response = self.client.get(
                self.workspace_url,
                params=params,
                headers=self.headers,
                timeout=API_TIMEOUT,
            )
            if response.status_code != 200:
                return None
            return response.json()

        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(exc)

    def get_jobs_names_and_notebooks_names(self, job_ids:list[int],notebook_ids:list[int]) -> dict:
        """
        Method returns the job details by the specified job_id
        """
        try:
            jobs = []
            filtered_notebooks = []
            work_space_paths = set()
            
            # Get unique notebook paths from jobs
            for job_id in job_ids:
                job = self.get_job_by_id(job_id)
                if job:
                    jobs.append(job.get("settings", {}).get("name"))
                    work_space_paths.update(self.get_unique_notebook_paths(job))
            
            # Filter notebook_ids based on workspace paths
            for path in work_space_paths:
                workspace_objects = self.get_workspace_objects_info(path)
                if workspace_objects:
                    objects = workspace_objects.get("objects", [])
                    for obj in objects:
                        if obj.get("object_id") in notebook_ids and obj.get("object_type") == "NOTEBOOK" and obj.get("path"):
                            filtered_notebooks.append(obj.get("path").split("/")[-1])
            
            return {"jobs": jobs, "notebooks": filtered_notebooks} if len(jobs) ==0 or len(filtered_notebooks)==0 else None

        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(exc)

    def get_column_lineage(
        self, table_name: str, column_name: str
    ) -> LineageColumnStreams:
        """
        Method returns table lineage details
        """
        try:
            data = {
                "table_name": table_name,
                "column_name": column_name,
            }

            response = self.client.get(
                f"{self.base_url}{COLUMN_LINEAGE_PATH}",
                headers=self.headers,
                data=json.dumps(data),
                timeout=API_TIMEOUT,
            ).json()

            if response:
                return LineageColumnStreams(**response)

        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(exc)

        return LineageColumnStreams()

    def get_owner_info(self, full_table_name: str) -> str:
        """
        get owner info from tables API
        """
        try:
            response = self.client.get(
                f"{self.base_url}{TABLES_PATH}/{full_table_name}",
                headers=self.headers,
                timeout=API_TIMEOUT,
            )
            if response.status_code != 200:
                raise HTTPError(response.text)
            return response.json().get("owner")
        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(exc)
        return
