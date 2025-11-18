import subprocess
import json

class fdtCLU:
    def run_fab_command(self, command, capture_output: bool = False, silently_continue: bool = False, raw_output: bool = False):
        result = subprocess.run(["fab", "-c", command], capture_output=capture_output, text=True)
        if (not(silently_continue) and (result.returncode > 0 or result.stderr)):
            raise Exception(f"Error running fab command. exit_code: '{result.returncode}'; stderr: '{result}'")    
        if (capture_output and not raw_output): 
            output = result.stdout.strip()
            return output
        elif (capture_output and raw_output):
            return result

    def fab_get_workspace_id(self, name):
        result = self.run_fab_command(f"get /{name} -q id" , capture_output = True, silently_continue= True)
        return result

    def fab_workspace_exists(self, name):
        id = self.run_fab_command(f"get /{name} -q id" , capture_output = True, silently_continue= True)
        return(id)

    def fab_get_id(self, name):
        id = self.run_fab_command(f"get /{self.trg_workspace_name}/{name} -q id" , capture_output = True, silently_continue= True)
        return(id)

    def fab_get_item(self, name):
        item = self.run_fab_command(f"get /{self.trg_workspace_name}/{name}" , capture_output = True, silently_continue= True)
        return(item)

    def fab_get_eventstream_connection_string(self, name, connection_name):
        connection_id = ""
        item_id = self.fab_get_id(name)

        item = self.run_fab_command(f"api -X get /workspaces/{self.trg_workspace_id}/eventstreams/{item_id}/topology" , capture_output = True, silently_continue= True)
        topology = json.loads(item)

        sources = topology.get("text",{}).get("sources",[])
        source_id = list(filter(lambda source: source["name"] == connection_name, sources))
        if len(source_id):
            connection_id = source_id[0].get("id")

        destinations = topology.get("text",{}).get("destinations",[])
        destination_id = list(filter(lambda destination: destination["name"] == connection_name, destinations))
        if len(destination_id):
            connection_id = destination_id[0].get("id")

        connection = self.run_fab_command(f"api -X get /workspaces/{self.trg_workspace_id}/eventstreams/{item_id}/sources/{connection_id}/connection" , capture_output = True, silently_continue= True)
        connection = json.loads(connection)
        connection = connection.get("text",{}).get("accessKeys",{}).get("primaryConnectionString")
        return(connection)

    def fab_get_display_name(self, name):
        display_name = self.run_fab_command(f"get /{self.trg_workspace_name}/{name} -q displayName" , capture_output = True, silently_continue= True)
        return(display_name)

    def fab_get_kusto_query_uri(self, name):
        connection = self.run_fab_command(f"get /{self.trg_workspace_name}/{name} -q properties.queryServiceUri -f", capture_output = True, silently_continue= True)
        return(connection)

    def fab_get_kusto_ingest_uri(self, name):
        connection = self.run_fab_command(f"get /{self.trg_workspace_name}/{name} -q properties.ingestionServiceUri -f", capture_output = True, silently_continue= True)
        return(connection)

    def fab_create_folder(self, display_name):
        folder = {
            "displayName": display_name
        }

        workspace_id = self.fab_get_workspace_id(self.trg_workspace_name)
        folderResponse = self.run_fab_command(f"api -X post /workspaces/{workspace_id}/folders/ -i {json.dumps(folder)}" , capture_output = True, silently_continue= True)
        folder_id = self.fab_get_folder_id(display_name)

        return folder_id

    def fab_update_item_folder(self,item,display_name):
        
        workspace_id = self.fab_get_workspace_id(self.trg_workspace_name)
        item_id = self.fab_get_id(item)
        folder_id = self.fab_create_folder(display_name)
        
        folder = {
            "targetFolderId": folder_id
        }

        updateFolderResponse = self.run_fab_command(f"api -X post /workspaces/{workspace_id}/items/{item_id}/move -i {json.dumps(folder)}" , capture_output = True, silently_continue= True)

    def fab_get_folders(self):
        workspace_id = self.fab_get_workspace_id(self.trg_workspace_name)
        response = self.run_fab_command(f"api workspaces/{workspace_id}/folders", capture_output = True, silently_continue= True)
        return(json.loads(response).get('text',{}).get('value',[]))

    def fab_get_folder_id(self,display_name):
        folders = self.fab_get_folders()

        return list(filter(lambda x: x["displayName"] == display_name, folders)).pop().get("id")