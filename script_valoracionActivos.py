# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 13:49:50 2022

@author: Sebastian
"""

#LECTURA DE PROCESOS BPMN ASOCIADOS A SERVICIOS DE TI, AUTOMATIZACION DE

# Modulos necesarios
import json
import xmltodict
import requests
import pandas as pd

###################################################################################################
#######################################INPUT RUTAS DE ENTRADA######################################
###################################################################################################
# Ruta donde estan archivos a leer
path = input("Ingresar ruta de la carpeta : ")
# Nombre archivo XPDL a leer
diagrama = input("Ingresar nombre del archivo del diagrama puede ser en los formatos:(diagrama.xml / diagrama.xpdl) : ")
# Nombre archivo de configuration items a leer
ruta_ci = input("Ingresar nombre del archivo del archivo de CI´s (archivo_ci.xlsx) : ")
# Nombre archivo pesos de procesos a leer
ruta_impacto_bi = input("Ingresar nombre del archivo con pesos de procesos (archivo_procesos.xlsx) : ")
# Ruta del archivo XPDL a leer
ruta_diagrama = path+"/"+diagrama


#####################################################################################################
######################################## LECTURA DE ARCHIVOS ########################################
#####################################################################################################
print("Leyendo archivos...")
config_items= pd.read_excel(ruta_ci)
impacto= pd.read_excel(ruta_impacto_bi)

# Lectura de archivo XPDL conteniendo el BPMN 2.0
# Crea un diccionario que contiene todos los datos del paquete
with open(ruta_diagrama) as xml_file:
     
    data_dict = xmltodict.parse(xml_file.read())
    xml_file.close()

####################################################################################################
###################################### PROCESAMIENTO DE BPMN #######################################
####################################################################################################
print("Procesando BPMN...")
# Transforacion de datos del diccionario con el paquete de entrada
# Genera listas de objetos segun los tipos de interes (pools,message flows, artifacts, workflow process)
paquete = data_dict["Package"] 
pools_list = paquete["Pools"]["Pool"]
message_flows = paquete["MessageFlows"]["MessageFlow"]
artifacts = paquete["Artifacts"]["Artifact"]
workflow_processes = paquete["WorkflowProcesses"]["WorkflowProcess"]

# Creacion de dataframes para almacenar informacion relevante de cada lista de objetos
#Seleccion de columnas necesarias para cada tipo de objeto
column_names_transitions = ["id-wf", "name-wf", "transition-id","transition-from","transition-to"]
df_wf_transitions = pd.DataFrame(columns = column_names_transitions)

column_names_activities = ["id-wf", "name-wf", "activity-id","activity-name","activity-width","activity-height","activity-x","activity-y"]
df_wf_activities = pd.DataFrame(columns = column_names_activities)

column_names_artifacts = ["id-artifact", "name-artifact", "type-artifact","artifact-width","artifact-height","artifact-x","artifact-y"]
df_artifacts = pd.DataFrame(columns = column_names_artifacts)

column_names_messages = ["id-message", "source-message", "target-message"]
df_messages = pd.DataFrame(columns = column_names_messages)

# Extraccion de transiciones a listas 
for workflow in workflow_processes:    
    
    if "Transitions" in workflow.keys():
        lista = workflow["Transitions"]["Transition"]
        is_list = isinstance(lista, list)
        #print(is_list)
        
        if is_list:
            try:
                for transition in lista:
                    #print(transition["@Id"])
                    new_row = {"id-wf":workflow["@Id"], "name-wf":workflow["@Name"], "transition-id":transition["@Id"],"transition-from":transition["@From"],"transition-to":transition["@To"]}
                    df_wf_transitions = df_wf_transitions.append(new_row, ignore_index=True)
            except:
                pass
                #print(workflow["@Name"])
        else:
            new_row = {"id-wf":workflow["@Id"], "name-wf":workflow["@Name"], "transition-id":lista["@Id"],"transition-from":lista["@From"],"transition-to":lista["@To"]}
            df_wf_transitions = df_wf_transitions.append(new_row, ignore_index=True)
    #else:
        #print("No hay transiciones")
        
        
# Extraccion de actividades a listas         
for workflow in workflow_processes:    
    
    if "Activities" in workflow.keys():
        lista = workflow["Activities"]["Activity"]
        is_list = isinstance(lista, list)
        #print(is_list)
        
        if is_list:
            try:
                for activity in lista:
                    #print(transition["@Id"])
                    new_row = {"id-wf":workflow["@Id"], "name-wf":workflow["@Name"], "activity-id":activity["@Id"],"activity-name":activity["@Name"],"activity-width":activity["NodeGraphicsInfos"]["NodeGraphicsInfo"]["@Width"],"activity-height":activity["NodeGraphicsInfos"]["NodeGraphicsInfo"]["@Height"],"activity-x":activity["NodeGraphicsInfos"]["NodeGraphicsInfo"]["Coordinates"]["@XCoordinate"],"activity-y":activity["NodeGraphicsInfos"]["NodeGraphicsInfo"]["Coordinates"]["@YCoordinate"]}
                    df_wf_activities = df_wf_activities.append(new_row, ignore_index=True)
            except:
                pass
                #print(workflow["@Name"])
        else:
            new_row = {"id-wf":workflow["@Id"], "name-wf":workflow["@Name"], "activity-id":lista["@Id"],"activity-name":lista["@Name"],"activity-width":lista["NodeGraphicsInfos"]["NodeGraphicsInfo"]["@Width"],"activity-height":lista["NodeGraphicsInfos"]["NodeGraphicsInfo"]["@Height"],"activity-x":lista["NodeGraphicsInfos"]["NodeGraphicsInfo"]["Coordinates"]["@XCoordinate"],"activity-y":lista["NodeGraphicsInfos"]["NodeGraphicsInfo"]["Coordinates"]["@YCoordinate"]}
            df_wf_activities = df_wf_activities.append(new_row, ignore_index=True)
    #else:
        #print("No hay actividades")
        
# Extraccion de artefactos a listas 
for artifact in artifacts:    
    
    new_row = {"id-artifact":artifact["@Id"], "name-artifact":artifact["@Name"], "type-artifact":artifact["@ArtifactType"],"artifact-width":artifact["NodeGraphicsInfos"]["NodeGraphicsInfo"]["@Width"],"artifact-height":artifact["NodeGraphicsInfos"]["NodeGraphicsInfo"]["@Height"],"artifact-x":artifact["NodeGraphicsInfos"]["NodeGraphicsInfo"]["Coordinates"]["@XCoordinate"],"artifact-y":artifact["NodeGraphicsInfos"]["NodeGraphicsInfo"]["Coordinates"]["@YCoordinate"]}
    df_artifacts = df_artifacts.append(new_row, ignore_index=True)
 
# Extraccion de mensajes a listas 
for message in message_flows:    
    
    new_row = {"id-message":message["@Id"], "source-message":message["@Source"], "target-message":message["@Target"]}
    df_messages = df_messages.append(new_row, ignore_index=True)

# Calculo de coordenadas(x,y) de ubicacion en el bpmn de cada actividad
df_wf_activities = df_wf_activities.astype({"activity-width":"int","activity-height":"int","activity-x":"int","activity-y":"int"})
df_wf_activities["x2"]=df_wf_activities["activity-width"]+df_wf_activities["activity-x"]
df_wf_activities["y2"]=df_wf_activities["activity-height"]+df_wf_activities["activity-y"]


# Calculo de coordenadas(x,y) de ubicacion en el bpmn de cada artefacto
df_artifacts = df_artifacts.astype({"artifact-width":"int","artifact-height":"int","artifact-x":"int","artifact-y":"int"})
df_artifacts["x2"]=df_artifacts["artifact-width"]+df_artifacts["artifact-x"]
df_artifacts["y2"]=df_artifacts["artifact-height"]+df_artifacts["artifact-y"]


# Funcion que valida si unas coordenadas estan contenidas en otras
def contiene(a_x,a_y,a_x2,a_y2,e_x,e_y,e_x2,e_y2):
    if(e_x>=a_x and e_x2<=a_x2 and e_y>=a_y and e_y2<=a_y2):
        return True
    else:
        return False
 
# Funcion validadora del contenedor al que pertenece el elemento
# Revisa de acuerdo a las coordenadas dadas por parametro si estan contenidas en uno de los contedores de la lista de artefactos
def contenedor(element_x,element_y,element_x2,element_y2):
    contenedor=""
    
    for index, row in df_artifacts.iterrows():
        if(contiene(row['artifact-x'],row['artifact-y'],row['x2'],row['y2'],element_x,element_y,element_x2,element_y2)):
            contenedor = row['name-artifact']
            break
    
    return contenedor
  
# Iteracion sobre lista de actividades para determinar su contenedor
for index, row in df_wf_activities.iterrows():

  df_wf_activities.at[index, 'Grupo'] = contenedor(row['activity-x'],row['activity-y'],row['x2'],row['y2'])


#Agrupacion por procesos / Conteo de actividades
procesos=df_wf_activities[df_wf_activities['name-wf'] == "Business"].groupby(['Grupo'],as_index=True).agg({'name-wf':"count"})
procesos.reset_index(inplace=True)

#Cruce actividades con elementos de tipo mensaje los cuales determinan conexion entre actividades y servicios de TI
df_messages = pd.merge(df_messages, df_wf_activities, left_on="source-message",right_on="activity-id", how ='left')

#Filtro de actividades que pertenecen al negocio
activities2=df_wf_activities[df_wf_activities['name-wf'] == "Business"]
activities2 = activities2[["activity-id","activity-name","Grupo"]]

#Union entre mensajes y actividades
df_messages2 = pd.merge(df_messages, df_wf_activities, left_on="target-message",right_on="activity-id", how ='left')
df_messages2 = df_messages2[["activity-name_x","activity-name_y","Grupo_x"]]

#Agrupacion por servicios / Conteo de actividades
#pivot = df_messages2.groupby(['activity-name_y'],as_index=False)["activity-name_x"].count()
pivot = pd.pivot_table(df_messages2, values='activity-name_y', index='activity-name_y', columns='activity-name_x',
               aggfunc='count')
pivot.reset_index(inplace=True)
pivot=pivot.fillna(0)

# Generar lista de actividades de procesos
lista_tareas = pivot[pivot.columns.difference(['activity-name_y'])].columns.values.tolist()

# Dataframe con informacion de tareas de negocio
tareas = df_wf_activities[df_wf_activities['name-wf'] == "Business"]
# Filtrar tareas y servicios
tareas = tareas[["activity-name","Grupo"]]

#Cruce para determinar a que proceso pertenece cada tarea
tareas = pd.merge(tareas, procesos, on="Grupo", how ='left')

# Calcular peso de tarea sobre el proceso al que pertenece
tareas["peso_tarea_proceso"]=1/tareas["name-wf"]

# Union con pesos de procesos dados en la entrada
tareas = pd.merge(tareas, impacto, left_on="Grupo",right_on="process", how ='left')

# Impacto de entrada sobre 10
tareas["business_impact"]=tareas["business_impact"]/10

# Calcular score de tarea segun peso de entrada y peso de tarea en el proceso
tareas["score"]=tareas["business_impact"]*tareas["peso_tarea_proceso"]
tareas = tareas.set_index('activity-name')

# Calcular impacto por servicio
pivot["business_impact"]=0.0
for index, row in pivot.iterrows():
    acumulado=0.0
    actual=0.0
    for tarea in lista_tareas:
        actual = pivot.at[index,tarea]*tareas.at[tarea,"score"]
        acumulado =acumulado +actual
        pivot.at[index,tarea]=actual
    pivot.at[index,"business_impact"]=acumulado

# Generar etiquetas de impacto segun cuartiles del score total calculado en el business_impact
pivot['impact'] = pd.qcut(pivot['business_impact'], 3, labels=["Low","Medium","High"])



  
####################################################################################################
###################################### PROCESAMIENTO CONFIG ITEMS ##################################
####################################################################################################
  
##### Config items

column_names_config_items = ["configuration_item_id", "it_service", "configuration_item_name","CPE","category","vulnerability","cvssV2","severityV2","vectorV2","accessVectorV2","accessComplexityV2","authenticationV2","cvssV3","severityV3","vectorV3","accessComplexityV3","authenticationV3"]
df_items = pd.DataFrame(columns = column_names_config_items)

# ITERACION SOBRE CONFIG ITEMS PARA TRAER VULNERABILIDADES
for index, row in config_items.iterrows():

    print("Procesando: "+row["CPE"])
    consulta_cpe="https://services.nvd.nist.gov/rest/json/cpes/1.0?cpeMatchString="+row["CPE"]+"&addOns=cves"
    resp = requests.get(url=consulta_cpe)
    data = resp.json() 
    
    resultado_cpes = data["result"]["cpes"]
    
    for element in resultado_cpes:
        if len(element["vulnerabilities"])>1 or len(element["vulnerabilities"][0])>0:
            vulnerabilities_list = element["vulnerabilities"]
            for vul in vulnerabilities_list:
                #print(vul)
            
                consulta_cve="https://services.nvd.nist.gov/rest/json/cve/1.0/"+vul+"?"
                resp2 = requests.get(url=consulta_cve)
                data2 = resp2.json()
        
                resultado_cves = data2["result"]["CVE_Items"]
                
                for cve in resultado_cves:
                    cvssV2=0.0
                    severityV2=""
                    vectorV2=""
                    accessVectorV2=""
                    accessComplexityV2=""
                    authenticationV2=""
                    
                    cvssV3=0.0
                    severityV3=""
                    vectorV3=""
                    accessVectorV3=""
                    accessComplexityV3=""

                    
                    if "baseMetricV2" in cve["impact"].keys():
                        dic_cvssV2 = cve["impact"]["baseMetricV2"]
                        severityV2 = dic_cvssV2["severity"]
                        cvssV2 = dic_cvssV2["cvssV2"]["baseScore"]
                        vectorV2 = dic_cvssV2["cvssV2"]["vectorString"]
                        accessVectorV2 = dic_cvssV2["cvssV2"]["accessVector"]
                        accessComplexityV2 = dic_cvssV2["cvssV2"]["accessComplexity"]
                        authenticationV2 = dic_cvssV2["cvssV2"]["authentication"]
                        
                    if "baseMetricV3" in cve["impact"].keys():
                        dic_cvssV3 = cve["impact"]["baseMetricV3"]["cvssV3"]
                        cvssV3 = dic_cvssV3["baseScore"]
                        severityV3 = dic_cvssV3["baseSeverity"]
                        vectorV3 = dic_cvssV3["vectorString"]
                        accessVectorV3 = dic_cvssV3["attackVector"]
                        accessComplexityV3 = dic_cvssV3["attackComplexity"]
                    #else:
                        #print("no hay vulnerabilidades")
                    new_row = {"configuration_item_id":row["configuration_item_id"], "it_service":row["it_service"], "configuration_item_name":row["configuration_item_name"],"CPE":row["CPE"],"category":row["category"],"vulnerability":vul,"cvssV2":cvssV2,"severityV2":severityV2,"vectorV2":vectorV2,"accessVectorV2":accessVectorV2,"accessComplexityV2":accessComplexityV2,"authenticationV2":authenticationV2,"cvssV3":cvssV3,"severityV3":severityV3,"vectorV3":vectorV3,"accessVectorV3":accessVectorV3,"accessComplexityV3":accessComplexityV3}
                    df_items = df_items.append(new_row, ignore_index=True)        
                
        else:
            continue
            #new_row = {"configuration_item_id":row["configuration_item_id"], "it_service":row["it_service"], "configuration_item_name":row["configuration_item_name"],"CPE":row["CPE"],"category":row["category"]}
            #df_items = df_items.append(new_row, ignore_index=True)


# CALCULO DE CRITICIDAD
vulnerabilidades = df_items[["configuration_item_id","it_service","configuration_item_name","CPE","category","vulnerability","cvssV2","vectorV2","accessVectorV2","accessComplexityV2","authenticationV2"]]
servicios_ci = df_items.groupby(['it_service'],as_index=False).agg({"configuration_item_name":"count"})
servicios_ci = servicios_ci.rename(columns = {'configuration_item_name':'vulnerabilidades_servicio'})
severidad_ci = df_items.groupby(['configuration_item_id'],as_index=False).agg({'cvssV2':"mean","configuration_item_name":"count"})
severidad_ci = severidad_ci.rename(columns = {'configuration_item_name':'vulnerabilidades_ci'})
severidad_ci = pd.merge(severidad_ci, df_items.sort_values('it_service', ascending=False).drop_duplicates(subset=['configuration_item_id']), left_on="configuration_item_id",right_on="configuration_item_id", how ='left')
severidad_ci =severidad_ci[["configuration_item_id","cvssV2_x","vulnerabilidades_ci","it_service","category"]]
severidad_ci = pd.merge(severidad_ci, servicios_ci, left_on="it_service",right_on="it_service", how ='left')
severidad_ci["vulnerabilidades_ci/servicio"]=severidad_ci["vulnerabilidades_ci"]/severidad_ci["vulnerabilidades_servicio"]
severidad_ci["ci_impact"]=severidad_ci["cvssV2_x"]*severidad_ci["vulnerabilidades_ci/servicio"]
severidad_columns_list = severidad_ci.columns.values.tolist()
severidad_columns_list.append("business_impact")
severidad_ci2 = pd.merge(severidad_ci, pivot, left_on="it_service",right_on="activity-name_y", how ='left')
severidad_ci2 =severidad_ci2[severidad_columns_list]
severidad_ci2 = severidad_ci2.rename(columns = {'cvssV2_x':'severidad_CVSS_V2','ci_impact':'ci_impact(servicio)','business_impact':'servicio_business_impact'})
severidad_ci2["criticidad_ci"]=severidad_ci2["ci_impact(servicio)"]*severidad_ci2["servicio_business_impact"]
severidad_final =severidad_ci2[["configuration_item_id","severidad_CVSS_V2","it_service","category","criticidad_ci"]]

vulnerabilidades = vulnerabilidades.rename(columns = {'cvssV2':'severidad_CVSS_V2','vectorV2':'vector_CVSS_V2','accessVectorV2':'accessVector_CVSS_V2','accessComplexityV2':'accessComplexity_CVSS_V2','authenticationV2':'authentication_CVSS_V2'})

#Exportar resultados a excel en la ruta de entrada
vulnerabilidades.to_excel(path+"/vulnerabilidades.xlsx", index=False)
severidad_final.to_excel(path+"/criticidad_activos.xlsx", index=False)


print("Proceso completado")
