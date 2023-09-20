def input_data(excel_file_path):
    import pandas as pd
    data = pd.read_excel(excel_file_path, sheet_name="入力データ(調達)")
    procurement = []
    # データフレームの行と列を反復処理してセルの値を記憶
    for row_index, row in data.iterrows():
        row_values = []
        for col_index, value in enumerate(row):
            row_values.append(value)
        procurement.append(row_values)
    
    data = pd.read_excel(excel_file_path, sheet_name="入力データ(原単位)") 
    basic_unit = []    
    # データフレームの行と列を反復処理してセルの値を記憶
    for row_index, row in data.iterrows():
        row_values = []
        for col_index, value in enumerate(row):
            row_values.append(value)
        basic_unit.append(row_values)
    return(procurement,basic_unit)




def input_A(excel_file_path):
    import pandas as pd
    data = pd.read_excel(excel_file_path, sheet_name="入力データ 形名A_BOM")  
    A_BOM = []   
    # データフレームの行と列を反復処理してセルの値を記憶
    for row_index, row in data.iterrows():
        row_values = []
        for col_index, value in enumerate(row):
            row_values.append(value)
        A_BOM.append(row_values)   
        
    data = pd.read_excel(excel_file_path, sheet_name="入力データ 形名A_BOP")  
    A_BOP = []   
    # データフレームの行と列を反復処理してセルの値を記憶
    for row_index, row in data.iterrows():
        row_values = []
        for col_index, value in enumerate(row):
            row_values.append(value)
        A_BOP.append(row_values)

    return(A_BOM,A_BOP)




def input_B(excel_file_path):
    import pandas as pd
    data = pd.read_excel(excel_file_path, sheet_name="入力データ 形名B_BOM") 
    B_BOM = []
    # データフレームの行と列を反復処理してセルの値を記憶
    for row_index, row in data.iterrows():
        row_values = []
        for col_index, value in enumerate(row):
            row_values.append(value)
        B_BOM.append(row_values)
    
    data = pd.read_excel(excel_file_path, sheet_name="入力データ 形名B_BOP")   
    B_BOP = [] 
    # データフレームの行と列を反復処理してセルの値を記憶
    for row_index, row in data.iterrows():
        row_values = []
        for col_index, value in enumerate(row):
            row_values.append(value)
        B_BOP.append(row_values)

    return(B_BOM,B_BOP)




def input_C(excel_file_path):
    import pandas as pd
    data = pd.read_excel(excel_file_path, sheet_name="入力データ 形名C_BOM") 
    C_BOM = []  
    # データフレームの行と列を反復処理してセルの値を記憶
    for row_index, row in data.iterrows():
        row_values = []
        for col_index, value in enumerate(row):
            row_values.append(value)
        C_BOM.append(row_values)
    
    data = pd.read_excel(excel_file_path, sheet_name="入力データ 形名C_BOP")  
    C_BOP = []   
    # データフレームの行と列を反復処理してセルの値を記憶
    for row_index, row in data.iterrows():
        row_values = []
        for col_index, value in enumerate(row):
            row_values.append(value)
        C_BOP.append(row_values)

    return(C_BOM,C_BOP) 