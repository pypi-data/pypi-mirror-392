import json

class fdtItemManagement:
    def replace_kqldb_parent_eventhouse(self, folder_path,parent_eventhouse):
        property_file = f"{folder_path}/DatabaseProperties.json"
        with open(property_file, 'r', encoding='utf-8') as file:
            content = json.load(file)
            content["parentEventhouseItemId"] = self.fab_get_id(parent_eventhouse)
        with open(property_file, 'w', encoding='utf-8') as file:
            json.dump(content,file,indent=4)

    def replace_eventstream_destination(self, folder_path,it_destinations):
        property_file = f"{folder_path}/eventstream.json"
        with open(property_file, "r", encoding="utf-8") as file:
            content = json.load(file)
            destinations = content.get("destinations",[])
            for destination in destinations:
                if destination.get("type") != "CustomEndpoint":
                    filtered_data = list(filter(lambda table: table["name"] == destination.get("name") and table["type"] == destination.get("type"), it_destinations))
                    if len(filtered_data) > 0:        
                        destination["properties"]["workspaceId"] = self.get_mapping_table_new_from_type_item("Workspace Id",self.trg_workspace_name)
                        destination["properties"]["itemId"] = self.get_mapping_table_new_from_type_item("KQL DB ID",filtered_data[0].get("itemName"))
                        if destination.get("properties",{}).get("databaseName") is not None:
                            destination["properties"]["databaseName"] = self.get_mapping_table_new_from_type_item("KQL DB Name",filtered_data[0].get("itemName"))
        with open(property_file, 'w', encoding='utf-8') as file:
            json.dump(content,file,indent=4)

    def replace_kqldashboard_datasources(self, folder_path,it_datasources):
        property_file = f"{folder_path}/RealTimeDashboard.json"
        with open(property_file, "r", encoding="utf-8") as file:
            content = json.load(file)
            datasources = content.get("dataSources",[])
            for datasource in datasources:
                filtered_data = list(filter(lambda table: table["name"] == datasource.get("name"), it_datasources))
                if len(filtered_data) > 0:        
                    datasource["workspace"] = self.get_mapping_table_new_from_type_item("Workspace Id",self.trg_workspace_name)
                    datasource["database"] = self.get_mapping_table_new_from_type_item("KQL DB ID",filtered_data[0].get("itemName"))
                    datasource["clusterUri"] = self.get_mapping_table_parent_type("KQL DB Eventhouse",filtered_data[0].get("itemName"),"Kusto Query Uri")
        with open(property_file, 'w', encoding='utf-8') as file:
            json.dump(content,file,indent=4)

    def replace_kqlqueryset_datasources(self, folder_path,it_datasources):
        property_file = f"{folder_path}/RealTimeQueryset.json"
        with open(property_file, "r", encoding="utf-8") as file:
            content = json.load(file)
            datasources = content.get("queryset",{}).get("dataSources",[])
            for datasource in datasources:
                filtered_data = list(filter(lambda table: str(table["itemName"]).replace(".KQLDatabase","") == datasource.get("databaseItemName"), it_datasources))
                if len(filtered_data) > 0:        
                    datasource["databaseItemId"] = self.get_mapping_table_new_from_type_item("KQL DB ID",filtered_data[0].get("itemName"))
                    datasource["clusterUri"] = self.get_mapping_table_parent_type("KQL DB Eventhouse",filtered_data[0].get("itemName"),"Kusto Query Uri")
        with open(property_file, 'w', encoding='utf-8') as file:
            json.dump(content,file,indent=4)

    def replace_pbi_report_definition(self, folder_path,datasource):
        property_file = f"{folder_path}/definition.pbir"
        sm_name = datasource.replace(".SemanticModel","")
        ws_id = self.get_mapping_table_new_from_type("Workspace Id")
        sm_id = self.get_mapping_table_new_from_type_item("Semantic Model ID",datasource)
        pbir_definition = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {
                "byPath": None,
                "byConnection": {
                "connectionString": f"Data Source=powerbi://api.powerbi.com/v1.0/myorg/{ws_id};Initial Catalog={sm_name};Integrated Security=ClaimsToken",
                "pbiServiceModelId": None,
                "pbiModelVirtualServerName": "sobe_wowvirtualserver",
                "pbiModelDatabaseName": sm_id,
                "connectionType": "pbiServiceXmlaStyleLive",
                "name": "EntityDataSource"
                }
            }
        }
        with open(property_file, 'w', encoding='utf-8') as file:
            json.dump(pbir_definition,file,indent=4)

    def replace_pipeline_parameter(self, folder_path, it_parameters):
        property_file = f"{folder_path}/pipeline-content.json"
        with open(property_file, "r", encoding="utf-8") as file:
            content = json.load(file)
            properties = content.get("properties",{}).get("parameters",{})
            for parameter in it_parameters:
                if parameter["type"] == "kusto_query_uri":
                    pipeline_parameter = properties.get(parameter["name"],{})
                    if ".KQLDatabase" in parameter["source"]:
                        pipeline_parameter["defaultValue"] = self.get_mapping_table_parent_type("KQL DB Eventhouse",parameter["source"],"Kusto Query Uri")
                    elif ".Eventhouse" in parameter["source"]:
                        pipeline_parameter["defaultValue"] = self.get_mapping_table_new_from_type_item("kustoQueryUri",parameter["source"])
                elif parameter["type"] == "kusto_ingest_uri":
                    pipeline_parameter = properties.get(parameter["name"],{})
                    if ".KQLDatabase" in parameter["source"]:
                        pipeline_parameter["defaultValue"] = self.get_mapping_table_parent_type("KQL DB Eventhouse",parameter["source"],"Kusto Ingest Uri")
                    elif ".Eventhouse" in parameter["source"]:
                        pipeline_parameter["defaultValue"] = self.get_mapping_table_new_from_type_item("kustoIngestUri",parameter["source"])
                elif parameter["type"] == "kusto_database":
                    pipeline_parameter = properties.get(parameter["name"],{})
                    pipeline_parameter["defaultValue"] = str(parameter["source"]).replace(".KQLDatabase","")
                elif parameter["type"] == "variable":
                    pipeline_parameter = properties.get(parameter["name"],{})
                    pipeline_parameter["defaultValue"] = self.pipeline_parameters[parameter["source"]]
        with open(property_file, 'w', encoding='utf-8') as file:
            json.dump(content,file,indent=4)    

    def add_variable_library_default(self, folder_path, it_parameters):
        property_file = f"{folder_path}/variables.json"
        
        new_variables = []

        for it_parameter in it_parameters:
            if it_parameter["type"] == "kusto_query_uri":
                if ".KQLDatabase" in it_parameter["source"]:
                    new_variable = self.get_mapping_table_parent_type("KQL DB Eventhouse",it_parameter["source"],"Kusto Query Uri")
                elif ".Eventhouse" in it_parameter["source"]:
                    eventhouse_name = it_parameter["source"] if self.eventhouse_name == "" or self.eventhouse_name is None else f"{self.eventhouse_name}.Eventhouse"
                    new_variable = self.get_mapping_table_new_from_type_item("Kusto Query Uri",eventhouse_name)
            elif it_parameter["type"] == "kusto_ingest_uri":
                if ".KQLDatabase" in it_parameter["source"]:
                    new_variable = self.get_mapping_table_parent_type("KQL DB Eventhouse",it_parameter["source"],"Kusto Ingest Uri")
                elif ".Eventhouse" in it_parameter["source"]:
                    eventhouse_name = it_parameter["source"] if self.eventhouse_name == "" or self.eventhouse_name is None else f"{self.eventhouse_name}.Eventhouse"
                    new_variable = self.get_mapping_table_new_from_type_item("Kusto Ingest Uri",eventhouse_name)
            elif it_parameter["type"] == "kusto_database":
                new_variable = str(it_parameter["source"]).replace(".KQLDatabase","")
            elif it_parameter["type"] == "variable":
                new_variable = self.pipeline_parameters[it_parameter["source"]]
            new_variables.append(
                {
                    "name": it_parameter.get("name"),
                    "note":  it_parameter.get("name"),
                    "type": "String",
                    "value": new_variable
                }
            )

        with open(property_file, "r", encoding="utf-8") as file:
            content = json.load(file)
        
        content["variables"] = new_variables
        
        with open(property_file, 'w', encoding='utf-8') as file:
            json.dump(content,file,indent=4)    

    def replace_pipeline_activities(self, folder_path, it_acitivities):
        property_file = f"{folder_path}/pipeline-content.json"
        with open(property_file, "r", encoding="utf-8") as file:
            content = json.load(file)
            activities = content.get("properties",{}).get("activities",[])
            for activity in activities:
                if activity["type"] == "TridentNotebook":
                    filtered_data = list(filter(lambda act: act["name"] == activity.get("name"), it_acitivities))
                    if len(filtered_data) > 0:
                        activity["typeProperties"]["workspaceId"] = self.get_mapping_table_new_from_type_item("Workspace Id",self.trg_workspace_name)
                        activity["typeProperties"]["notebookId"] = self.get_mapping_table_new_from_type_item("Notebook ID",filtered_data[0].get("itemName"))
        with open(property_file, 'w', encoding='utf-8') as file:
            json.dump(content,file,indent=4)       