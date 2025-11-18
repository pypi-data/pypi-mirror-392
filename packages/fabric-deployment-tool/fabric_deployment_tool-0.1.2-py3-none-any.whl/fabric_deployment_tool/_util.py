import shutil
import os
import sempy.fabric as fabric
import json
import uuid
from zipfile import ZipFile

class fdtUtils:
    def get_id_by_name(self, name):
        for it in self.deployment_order:
            if it.get("name") == name:
                    return it.get("id")
        return None

    def get_schedule_by_name(self, name):
        for it in self.deployment_order:
            if it.get("name") == name:
                    return it.get("schedule")
        return None

    def copy_to_tmp(self, name,child=None,type=None):
        child_path = "" if child is None else f".children/{child}/"
        type_path = "" if type is None else f"{type}/"
        shutil.rmtree("./builtin/tmp",  ignore_errors=True)
        path2zip = "./builtin/src/src.zip"
        with  ZipFile(path2zip) as archive:
            for file in archive.namelist():
                if file.startswith(f'src/{type_path}{name}/{child_path}'):
                    archive.extract(file, './builtin/tmp')
        return(f"./builtin/tmp/src/{type_path}{name}/{child_path}" )

    def get_mapping_table_new_from_type(self, type):
        result = ""
        filtered_data = list(filter(lambda item: item['Type'] == type, self.mapping_table))
        if len(filtered_data) > 0:
            result=filtered_data[0]["new"]
        return result

    def get_mapping_table_new_from_old(self, old):
        result = ""
        filtered_data = list(filter(lambda item: item['old'] == old, self.mapping_table))
        if len(filtered_data) > 0:
            result=filtered_data[0]["new"]
        return result

    def get_mapping_table_new_from_type_item(self, type,item):
        result = ""
        filtered_data = list(filter(lambda table: table["Type"] == type and table["Item"] == item, self.mapping_table))
        if len(filtered_data) > 0:
            result=filtered_data[0]["new"]
        return result

    def get_mapping_table_parent_type(self, type,item,parent_type):
        parent_item = self.get_mapping_table_new_from_type_item(type,item)
        result = self.get_mapping_table_new_from_type_item(parent_type,parent_item)
        return result

    def replace_ids_in_folder(self, folder_path, mapping_table):
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith(('.py', '.json', '.pbir', '.platform', '.ipynb', '.py', '.tmdl')) and not file_name.endswith('report.json'):
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        for mapping in mapping_table:  
                            content = content.replace(mapping["old"], mapping["new"])
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(content)
    
    def fab_update_environments_spark_monitor(self,evironments, eventstream_name):
        
        for environment in evironments:
            workspace = environment.get("workspace_id")            
            environment = environment.get("environment_id")
            print("################### UPDATING ENVIRONMENT")
            print("workspace: " + workspace)
            print("Environment: " + environment)
            connection_string = self.get_mapping_table_new_from_type_item("Connection String Eventstream",eventstream_name)
            StringSparkProperties = json.dumps(
                {
                    "sparkProperties":
                        {
                            "spark.synapse.diagnostic.emitters": "SparkEmitter",
                            "spark.synapse.diagnostic.emitter.SparkEmitter.type": "AzureEventHub",
                            "spark.synapse.diagnostic.emitter.SparkEmitter.secret": connection_string,
                            "spark.fabric.pools.skipStarterPools": "true"
                        }
                }
            )
            response = self.run_fab_command(f"api -X patch /workspaces/{workspace}/environments/{environment}/staging/sparkcompute -i  {StringSparkProperties}", silently_continue= True)
            response = self.run_fab_command(f"api -X post /workspaces/{workspace}/environments/{environment}/staging/publish ", silently_continue= True)
            print("################### FINISH UPDATING ENVIRONMENT")

    def update_capcity_events_eventstream(self,workspace, item_name = "CapacityEvents"):
        tmp_path = "./builtin/tmp/export/"

        shutil.rmtree(tmp_path,  ignore_errors=True)

        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)

        self.run_fab_command(f"export  /{workspace}.Workspace/{item_name}.Eventstream -o {tmp_path} -f ", silently_continue= True)

        property_file = f"{tmp_path}{item_name}.Eventstream/eventstream.json"

        new_sources = []
        new_input_nodes = []

        dfCapacities = fabric.list_capacities()
        dfCapacities = dfCapacities.query("Sku != 'PP3'")

        with open(property_file, "r", encoding="utf-8") as file:
            content = json.load(file)
            sources = content.get("sources",[])
            for index, row in dfCapacities.iterrows():
                capacity_id = row['Id']
                name = row['Display Name']
                sku = row['Sku']
                name = f"{name.replace(' ','')}-{sku}"
                filtered_data = list(filter(lambda table: table.get("properties",{}).get("capacityId") == capacity_id, sources))
                if len(filtered_data) > 0:
                    new_source = filtered_data.pop()
                    new_input_node = {"name":new_source.get("name")}
                else:
                    new_source = {
                        "id": str(uuid.uuid4()),
                        "name": name,
                        "type": "FabricCapacityUtilizationEvents",
                        "properties": {
                            "eventScope": "Capacity",
                            "capacityId": capacity_id,
                            "includedEventTypes": [
                            "Microsoft.Fabric.Capacity.State",
                            "Microsoft.Fabric.Capacity.Summary"
                            ],
                            "filters": []
                        }
                    }
                    new_input_node = {"name":name}
                new_sources.append(new_source)
                new_input_nodes.append(new_input_node)
            content['sources'] = new_sources

            for stream in content['streams']:
                if stream["type"] == "DefaultStream":
                    stream["inputNodes"] = new_input_nodes

        with open(property_file, 'w', encoding='utf-8') as file:
            json.dump(content,file,indent=4)

        self.run_fab_command(f"import  /{workspace}.Workspace/{item_name}.Eventstream -i {tmp_path}/{item_name}.Eventstream -f ", silently_continue= True)