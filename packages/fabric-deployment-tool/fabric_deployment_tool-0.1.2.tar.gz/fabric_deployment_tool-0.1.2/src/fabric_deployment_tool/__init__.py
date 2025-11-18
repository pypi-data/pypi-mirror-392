"""Fabric deployment tool template package."""

from __future__ import annotations

from importlib.metadata import version

import os
import json
from ._fab_cli import fdtCLU
from ._git import fdtGit
from ._util import fdtUtils
from ._fab_item_management import fdtItemManagement
import notebookutils

__all__ = [
    "__version__",
    "FabDeploymentTool",
]

try:
    __version__ = version("fabric-deployment-tool")
except Exception:  # pragma: no cover
    __version__ = "0.0.0"


class FabDeploymentTool(fdtCLU, fdtGit, fdtUtils, fdtItemManagement):
    src_workspace_id = ""
    src_workspace_name = ""
    trg_workspace_id = ""
    trg_workspace_name = ""
    deployment_order = []
    mapping_table =  []
    workspace_name = ""
    capacity_name = ""
    eventhouse_name = ""
    repo_owner = ""
    repo_name = ""
    branch = ""
    folder_prefix = ""
    github_token = ""
    pipeline_parameters = {}

    def __init__(self):        
        # Set environment parameters for Fabric CLI
        token = notebookutils.credentials.getToken('pbi')
        os.environ['FAB_TOKEN'] = token
        os.environ['FAB_TOKEN_ONELAKE'] = token

    def run(self, workspace_name, capacity_name= "", eventhouse_name = "", exclude = [], type_exclude = [], pipeline_parameters = {}):
        self.download_folder_as_zip(self.repo_owner, self.repo_name, output_zip = "./builtin/src/src.zip", branch = self.branch, folder_to_extract= f"{self.folder_prefix}/src", folder_prefix = f"{self.folder_prefix}", github_token=self.github_token)
        self.download_folder_as_zip(self.repo_owner, self.repo_name, output_zip = "./builtin/config/config.zip", branch = self.branch, folder_to_extract= f"{self.folder_prefix}/config" , folder_prefix = f"{self.folder_prefix}", github_token=self.github_token)
        self.uncompress_zip_to_folder(zip_path = "./builtin/config/config.zip", extract_to= "./builtin")
        base_path = './builtin/'

        self.eventhouse_name = eventhouse_name
        self.pipeline_parameters = pipeline_parameters
        deploy_order_path = os.path.join(base_path, 'config/deployment_order.json')
        with open(deploy_order_path, 'r') as file:
                self.deployment_order = json.load(file)

        #deploy workspace idempotent
        if "NotFound" in self.fab_workspace_exists(f"{workspace_name}.Workspace"):
            if capacity_name == "" or capacity_name is None:
                raise "Workspace doesn´t exist and capacity_name not provided"
            self.run_fab_command(f"mkdir {workspace_name}.Workspace -P capacityname={capacity_name}.Capacity")
            print(f"New Workspace Create")

        self.src_workspace_name = "Workspace.src"
        self.src_workspace_id = self.get_id_by_name(self.src_workspace_name)
        self.trg_workspace_id = self.fab_get_workspace_id(f"{workspace_name}.Workspace")
        self.trg_workspace_name = f"{workspace_name}.Workspace"

        print(f"Target Workspace Id: {self.trg_workspace_id}")
        print(f"Target Workspace Name: {self.trg_workspace_name}")

        self.mapping_table.append({"Type": "Workspace Id", "Item": self.trg_workspace_name, "old": self.get_id_by_name(self.src_workspace_name), "new": self.trg_workspace_id })
        self.mapping_table.append({"Type": "Workspace Blank Id", "Item": self.trg_workspace_name, "old": "00000000-0000-0000-0000-000000000000", "new": self.trg_workspace_id })
        self.mapping_table.append({"Type": "Workspace Name", "Item": self.trg_workspace_name, "old": self.src_workspace_name, "new": self.trg_workspace_name.replace(".Workspace", "") })
        exclude = exclude + [self.src_workspace_name]

        for it in self.deployment_order:
            new_id = None            
            name = it["name"]
            type = it.get("type")

            if name in exclude:
                continue    
            
            if type in type_exclude:
                continue

            self.__deploy_item(name,None,it)

            for child in it.get("children",[]):
                child_name = child["name"]
                self.__deploy_item(name,child_name,child)

    def __deploy_item(self, name,child=None,it=None):
        parent = ""
        cli_parameter = ""

        # Copy and replace IDs in the item
        tmp_path = self.copy_to_tmp(name,child,it.get("type"))
        
        if child is not None:
            parent = name
            name = child     

        if ".KQLDatabase" in name:
            if child is not None:
                parent = parent if self.eventhouse_name == "" or self.eventhouse_name is None else f"{self.eventhouse_name}.Eventhouse"
            if it["parent"] is not None:
                parent = it["parent"] if self.eventhouse_name == "" or self.eventhouse_name is None else f"{self.eventhouse_name}.Eventhouse"
            self.mapping_table.append({"Type": "KQL DB Eventhouse", "Item": name, "old": it["parent"], "new": parent })  
            self.replace_kqldb_parent_eventhouse(tmp_path,parent)
        elif ".Eventhouse" in name:
            name = name if self.eventhouse_name == "" or self.eventhouse_name is None else f"{self.eventhouse_name}.Eventhouse"
        elif ".Eventstream" in name:
            self.replace_eventstream_destination(tmp_path,it.get("destinations")) 
        elif ".Notebook" in name:
            cli_parameter = cli_parameter + " --format .py"
        elif ".DataPipeline" in name: 
            self.replace_pipeline_parameter(tmp_path,it.get("parameters",[]))
            self.replace_pipeline_activities(tmp_path,it.get("acitivities",[]))
        elif ".SemanticModel" in name:
            self.replace_ids_in_folder(tmp_path, self.mapping_table)
        elif ".KQLDashboard" in name:
            self.replace_kqldashboard_datasources(tmp_path, it.get("datasources"))
        elif ".KQLQueryset" in name:
            self.replace_kqlqueryset_datasources(tmp_path, it.get("datasources"))
        elif ".Report" in name:
            self.replace_pbi_report_definition(tmp_path,it.get("datasource"))
        elif ".VariableLibrary" in name:
            self.add_variable_library_default(tmp_path,it.get("variables"))

        print("", flush=True)
        print("#############################################", flush=True)
        print(f"Deploying {name}", flush=True)
        
        self.run_fab_command(f"import  /{self.trg_workspace_name}/{name} -i {tmp_path} -f {cli_parameter} ", silently_continue= True)

        new_id = self.fab_get_id(name)

        if ".KQLDatabase" in name:
            self.mapping_table.append({"Type": "KQL DB ID", "Item": name, "old": it["id"], "new": new_id })
        elif ".Eventhouse" in name:
            query_uri = self.fab_get_kusto_query_uri(name)
            ingest_uri = self.fab_get_kusto_ingest_uri(name)
            self.mapping_table.append({"Type": "Kusto Query Uri", "Item": name, "old": it["kustoQueryUri"], "new": query_uri })        
            self.mapping_table.append({"Type": "Kusto Ingest Uri", "Item": name, "old": it["kustoIngestUri"], "new": ingest_uri })
            self.mapping_table.append({"Type": "Eventhouse ID", "Item": name, "old": it["id"], "new": new_id })
        elif ".Eventstream" in name:
            for customEndpointName in it.get("customEndpointName",[]):
                self.mapping_table.append({"Type": "Connection String Eventstream", "Item": name, "old": customEndpointName, "new": self.fab_get_eventstream_connection_string(name,customEndpointName) })
            self.mapping_table.append({"Type": "Eventstream ID", "Item": name, "old": it["id"], "new": new_id })
        elif ".Notebook" in name:
            self.mapping_table.append({"Type": "Notebook ID", "Item": name, "old": it["id"], "new": new_id })
        elif ".DataPipeline" in name:
            self.mapping_table.append({"Type": "Pipeline ID", "Item": name, "old": it["id"], "new": new_id })
        elif ".Report" in name:
            self.mapping_table.append({"Type": "Report ID", "Item": name, "old": it["id"], "new": new_id })
        elif ".SemanticModel" in name:
            self.mapping_table.append({"Type": "Semantic Model ID", "Item": name, "old": it["id"], "new": new_id })
        elif ".KQLDashboard" in name:
            self.mapping_table.append({"Type": "KQLDashboard ID", "Item": name, "old": it["id"], "new": new_id })

        if it.get("folder") is not None:
            self.fab_update_item_folder(name,it.get("folder"))  
  