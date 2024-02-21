import PyPDF2
import tabula
import json

#define variables
path = "MonitoringReportClient.pdf"
FinalJson= json.loads('{}')

#function to find number of pages in pdf
def findNumberOfPages(path):    
    pdfFileObj = open(path, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    return pdfReader.numPages

#function to return list of Columns for a given size
def getColumns(size):
    columns = []
    for i in range(size):
        columns.append(f"Column{i+1}")
    return columns

#define a function pdftables_tojson to convert pdf to json
def pdftables_tojson(path):
    #define empty pageJson array to store the json of each page in the pdf
    pageJson = json.loads('[]') 
    #define tblIdx integer to store the index of the table
    tblIdx = 0
    #get number of pages in pdf
    numPages = findNumberOfPages(path)
    #iterate through each page
    for i in range(numPages):
        #read the pdf and convert to json
        dfs = tabula.read_pdf(path, pages = i+1, lattice=True, multiple_tables=True)
        #iterate through each dataframe
        for df in dfs:
            #if the dataframe is empty, skip
            if df.empty:
                continue
            #if the dataframe has only one row, skip
            if len(df) == 1:
                continue
            #if the dataframe has only one column, skip
            if len(df.columns) == 1:
                continue

            #remove first two rows from the df as they are not required
            df = df.iloc[2:]

            #set columns for the dataframe
            df.columns = getColumns(len(df.columns))
            

            #define empty json tablesJson to store the dataframe
            tablesJson = json.loads('{}')

            #add the table columns -tablename, tableIndex, pageNo,tableRows, totalColumns to the json
            tablesJson["tableName"] = f"Table{tblIdx+1}"
            tablesJson["tableIndex"] = tblIdx+1
            tablesJson["pageNo"] = i+1
            tablesJson["tableRows"] = len(df)
            tablesJson["totalColumns"] = len(df.columns)

            #add tableData column with df as json to the tablesJson
            tablesJson["tableData"] = json.loads(df.to_json(orient='records'))
            
            #add the tablesJson to the pageJson
            pageJson.append(tablesJson)
            tblIdx += 1
            
    #add the pageJson to the FinalJson- the final json to be returned            
    FinalJson["tables"] = pageJson

    #write json to file-PDFTojson.json
    with open('PDFTojson.json', 'w') as json_file:
        json.dump(FinalJson, json_file, indent=4)

#write python if__name__ == "__main__": to call the function pdftables_tojson
if __name__ == "__main__":
    pdftables_tojson(path)
    #print(FinalJson)
