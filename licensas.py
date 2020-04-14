import pandas as pd
import re
import numpy as np

def getData(dataFile):
    fo = open(dataFile)
    lines = fo.readlines()
    lengthFile = len(lines)
    body = []
    headers = []
    splitBody = []
    
    for i in range(lengthFile):
        #cria a variavel onde o programa deve começar a ler os dados (start)
        if(lines[i].startswith('License Usage')):
            start = i+2
        
        #cria a variavel onde o programa deve parar de ler os dados (end)
        elif(lines[i].startswith('(Number of')):
            h = (re.split(r'\s{2,}', lines[start]))       #splita o cabeçalho
            end = i - 1
            
            #Faz o split do corpo do arquivo
            for t in range(start+2, end+1):
                splitLine = (re.split(r'\s{2,}', lines[t]))
                splitBody.append(splitLine)   #vetor de linhas splitadas
        
            headers.append(h)     #vetor de cabeçalhos (nesse caso temos apenas um cabeçalho)
            body.extend(splitBody)  #vetor final que guarda todo o arquivo splitado
            
            #trocando os espaços da coluna License Item por Underscore "_"
            for t in range(len(body)):
                body[t][1] = body[t][1].replace(" ", "_")

    #Tratando a string vazia qua aparece no final (posição 7 do vetor interno)
    for t in body:
        del t[7]
        del t[6]
   
    for t in range(len(body)):
        for ti in range(len(body[t])):
            if(ti > 2 and (body[t][ti] != '' and body[t][ti] != '-')):
                body[t][ti] = float(body[t][ti])
                
    
    return body


def createCsv(File, Name):
    tuples = getData(File)
    #df = pd.DataFrame(tuples, columns = [' License ID', 'License Item', 'Type', 'Authorization-values', 'Real-values', 'Usage-percent(%)'])
    #df = df.sort_values(by=['Real-values'])
    
    df = pd.DataFrame(tuples, columns = ['License ID', 'License Item', 'Type', 'maximum_tuple_number', 'used_number', 'Usage-percent(%)'])
    df.to_csv(Name, index = False)
    return df


def renameColumns(df, columns): 
    newColumns = {}
    
    for c in columns:
        newColumns[c] = c.lower().replace(" ", "_")
    
    df = df.rename(columns=newColumns)

    return df

def generateCompleteReport(fileBase, createdFile, name_csv, countDays):
    created = pd.read_csv(createdFile)
    created = renameColumns(created, list(created.columns))
    
    base = pd.read_csv(fileBase)    
    base = renameColumns(base, list(base.columns))
    
    completeReport = []
    
    for index,row in created.iterrows():
        rowBase = base.loc[base['license_id'] == row.license_id]
        if(row.maximum_tuple_number == 0):
            usage = 0
        else:
            usage = str(int(round(row.used_number/row.maximum_tuple_number, 2)*100)) + '%'
            
        monthlyGrowth = int(round(((row.used_number - rowBase.used_number.values[0])/countDays)))
        realGrowth = int(round(((row.used_number - rowBase.used_number.values[0])/countDays)*30))
        
        forecastNumber = round(row.maximum_tuple_number/realGrowth) if realGrowth != 0 else 0
        
        if forecastNumber == 0: forecast = 'Estável'
        elif forecastNumber >= 1 and forecastNumber <= 24: forecast = forecastNumber
        elif forecastNumber > 24: forecast = 'Maior que 2 Anos'
        elif forecastNumber < 0: forecast = 'Decrescimento'
            
        newRow = [row.license_id, row.license_item, row.type, int(row.maximum_tuple_number), int(row.used_number), usage, monthlyGrowth,realGrowth, forecast, forecastNumber]
        completeReport.append(newRow)
    
    report = pd.DataFrame(completeReport, columns=['License ID', 'License Item', 'Type', 'maximum_tuple_number', 'used_number', 'Usage-percent','Crescimento Mensal','Crescimento Real','Previsão de Esgotamento','Esgotamento'])

    report.to_csv(name_csv, index=False)
    
    return report



def run(txt, month6, name_csv, days):

	createCsv(txt, name_csv)
	# csvBase = createCsv('LICENÇAS ULA - 13-09-2019.log', 'licensesBase.csv')

	generateCompleteReport(month6, name_csv, name_csv, days)
	# csv = createCsv('LICENÇAS ULA - 03-03-2020.txt', 'licenses.csv')
	# csvBase = createCsv('LICENÇAS ULA - 13-09-2019.log', 'licensesBase.csv')

	# relatorioFinal = generateCompleteReport('licensesBase.csv', 'licenses.csv', 180 )

if __name__ == '__main__':

    archive = open('arguments_licenses.txt','r')
    line = []
    for lines in archive:
        lines = lines.strip()
        line.append(lines)
    archive.close()

    list_path = []
    for pos in line:
        count = 0
        for character in pos:
            count += 1
            if character == "=":
                list_path.append(pos[count+1:])

    # print(list_path)
    run(list_path[0], list_path[1], list_path[2] , int(list_path[3]))