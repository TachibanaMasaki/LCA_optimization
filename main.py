import numpy as np
import input
import LCA
from platypus import NSGAII, Problem, Real, nondominated
import matplotlib.pyplot as plt
#--------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------入力データの読み込み--------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------
excel_file_path = "マスバランス組み立て.xlsx"
procurement,basic_unit=input.input_data(excel_file_path)
A_BOM,A_BOP=input.input_A(excel_file_path)
B_BOM,B_BOP=input.input_B(excel_file_path)
C_BOM,C_BOP=input.input_C(excel_file_path)
#--------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------USERの入力値-------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------
#製造する型の数
num_product = 3
name_set = np.array(("形名A","形名B","形名C"))
#再生材重量上限
materials_limit = 50000
#再エネ調達上限
energy_limit_1 = 100000
energy_limit_2 = 100000
energy_limit = energy_limit_1 + energy_limit_2

total_electricity = np.zeros(num_product)
for k in range(num_product):
    if k == 0:
        BOP = A_BOP
        BOM = A_BOM
    elif k == 1:
        BOP = B_BOP
        BOM = B_BOM
    elif k == 2:
        BOP = C_BOP
        BOM = C_BOM
    else:
        print("製品の情報が足りません")
    for i in range(len(BOP)):
        if BOP[i][4] == "自社加工":
            total_electricity[k] +=  BOP[i][10]

#CO2削減率（顧客要望）
request = np.zeros(num_product)
request[0] = 0.10
request[1] = 0.15
request[2] = 0.15

acceptable_error = 0.0001
better_error = 100
roop = 2
#--------------------------------------------------------------------------------------------------------------------------------------   
#----------------------------------------------------最適化計算-------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------
# 目的関数
def objective(vars):
    import input
    excel_file_path = "マスバランス組み立て.xlsx"
    procurement,basic_unit=input.input_data(excel_file_path)
    A_BOM,A_BOP=input.input_A(excel_file_path)
    B_BOM,B_BOP=input.input_B(excel_file_path)
    C_BOM,C_BOP=input.input_C(excel_file_path)
    
    num_product = 3
    
    #CO2削減率（顧客要望）
    request = np.zeros(num_product)
    request[0] = 0.10
    request[1] = 0.15
    request[2] = 0.15
    
    #使用可能の再生材（顧客要望）
    weight_limit = np.zeros(num_product)
    weight_limit[0] = 0.3
    weight_limit[1] = 0.3
    weight_limit[2] = 0.3
#--------------------------------------------------------
    
    num_parts = np.zeros(num_product, dtype=int)
    total_number = np.zeros(num_product)
    total_weight = np.zeros(num_product)
    for k in range(num_product):
        if k == 0:
            BOM = A_BOM
        elif k == 1:
            BOM = B_BOM
        elif k == 2:
            BOM = C_BOM
        else:
            print("製品の情報が足りません")
        for row in BOM:
            if row[0] == 1:
                num_parts[k] += 1
        total_number[k] = procurement[(num_parts[k]+1)*k][6]
        total_weight[k] = BOM[0][6] * BOM[0][7] * total_number[k] 
                
                
        CO2 = np.zeros((num_product, num_parts[k]+1))
        cost_labor = np.zeros((num_product, num_parts[k]+1))
        cost_equipment = np.zeros((num_product, num_parts[k]+1))
        cost_electricity = np.zeros((num_product, num_parts[k]+1))
        cost_transportation = np.zeros((num_product, num_parts[k]+1))
        cost_CO2 = np.zeros((num_product, num_parts[k]+1))
        cost_procurement = np.zeros((num_product, num_parts[k]+1))
    
#再エネ、再生材なしのときの計算
    materials_mass_balance = np.zeros(num_product)
    energy_mass_balance = np.zeros(num_product)
    CO2_non_Renewable = np.zeros(num_product)
    cost_non_Renewable = np.zeros(num_product)
    materials_total = 0.0
    energy_total = 0.0
    CO2, cost_procurement, cost_labor, cost_equipment, cost_electricity, cost_transportation, cost_CO2 = LCA.CO2_COST(procurement, basic_unit, num_product, A_BOM, A_BOP, B_BOM, B_BOP, C_BOM, C_BOP, materials_mass_balance, energy_mass_balance, materials_total, energy_total)
    for k in range(num_product):
        CO2_non_Renewable[k] = sum(CO2[k][:])
        cost_non_Renewable[k] = sum(cost_procurement[k][:]) + sum(cost_labor[k][:]) + sum(cost_equipment[k][:]) \
            + sum(cost_electricity[k][:]) + sum(cost_transportation[k][:]) + sum(cost_CO2[k][:])
            
    #再生材重量
    materials_total = vars[0]
    #再エネ調達量
    energy_total = vars[1]
    
    for k in range(num_product-1):
        materials_mass_balance[k] = vars[k+2]
    materials_mass_balance[num_product-1] = 1 - sum(materials_mass_balance[:-1])
         
    for k in range(num_product-1):
        energy_mass_balance[k] = vars[k+num_product+1]
    energy_mass_balance[num_product-1] = 1 - sum(materials_mass_balance[:-1])
        
    
    CO2, cost_procurement, cost_labor, cost_equipment, cost_electricity, cost_transportation, cost_CO2 = LCA.CO2_COST(procurement, basic_unit, num_product, A_BOM, A_BOP, B_BOM, B_BOP, C_BOM, C_BOP, materials_mass_balance, energy_mass_balance, materials_total, energy_total)
    
    total_CO2 = np.zeros(num_product)
    total_cost  = np.zeros(num_product)
    for k in range(num_product):
        total_CO2[k] = sum(CO2[k][:])
        total_cost[k] = sum(cost_procurement[k][:]) + sum(cost_labor[k][:]) + sum(cost_equipment[k][:]) \
                   + sum(cost_electricity[k][:]) + sum(cost_transportation[k][:]) + sum(cost_CO2[k][:])   
    function_total_CO2 = sum(total_CO2)
    function_total_cost = sum(total_cost)
    function_total_CO2 = (sum(CO2_non_Renewable) - sum(total_CO2)) / sum(CO2_non_Renewable) * 100
    function_total_cost = (sum(cost_non_Renewable) * 1.2 - sum(total_cost)) / (sum(cost_non_Renewable) * 1.2) * 100
    
            

#制約条件
    condition = np.zeros(2*num_product)
    for i in range(num_product):
        condition[i] = (CO2_non_Renewable[i] - total_CO2[i]) / CO2_non_Renewable[i] - request[i]
        condition[i+num_product] = weight_limit[i] - materials_total * materials_mass_balance[i] / total_weight[i]

    return [function_total_CO2, function_total_cost], condition
#--------------------------------------------------------------------------------------------------------------------------------------   
#----------------------------------------------最適化計算を実行する関数-------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------
def optimization(n_var, n_obj, n_con, vars, n_run):
    # 設計変数と目的関数の数を設定
    problem = Problem(n_var, n_obj, n_con)
    # 最適化問題に最小化を設定
    # 制約条件を設定
    problem.directions = [Problem.MAXIMIZE, Problem.MAXIMIZE]
    problem.constraints[:] = ">0"

    # 設計変数と目的関数を設定
    problem.types[:] = vars
    problem.function = objective
 
    # 最適化アルゴリズムを設定して計算を実行する
    algorithm = NSGAII(problem)
    algorithm.run(n_run)

    return algorithm 
#--------------------------------------------------------------------------------------------------------------------------------------   
#----------------------------------------------------最適化計算-------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------
print("wait a minites!")

for r in range(roop):
    # 設計変数を設定
    var1 = Real(0.0, materials_limit)
    var2 = Real(0.0, energy_limit)
    var3 = Real(0.0, 1.0)
    var4 = Real(0.0, 1.0)
    var5 = Real(0.0, total_electricity[0] / energy_limit)
    var6 = Real(0.0, total_electricity[1] / energy_limit)
    
    vars = [var1, var2, var3, var4, var5, var6]
     
    # 最適化計算を実行
    algorithm = optimization(n_var=len(vars), n_obj=2, n_con=6, vars=vars, n_run=5)

    # # フォントの種類とサイズを設定する。
    # plt.rcParams['font.size'] = 14
    # plt.rcParams['font.family'] = 'Times New Roman'
     
    # # グラフの入れ物を用意する。
    # fig = plt.figure(figsize=(6, 5))
    # ax1 = fig.add_subplot(111)
     
    # # 軸のラベルを設定する。
    # ax1.set_xlabel('CO2 reduction rate')
    # ax1.set_ylabel('Profit margin')
     
    # 最適化結果から実現可能解をプロットする。
    obj1 = []
    obj2 = []
    obj3 = []
    
    var1 = []
    var2 = []
    var3 = []
    var4 = []
    var5 = []
    var6 = []
    for solution in algorithm.result:
        obj1.append(solution.objectives[0])
        obj2.append(solution.objectives[1])
        
        var1.append(solution.variables[0])
        var2.append(solution.variables[1])
        var3.append(solution.variables[2])
        var4.append(solution.variables[3])
        var5.append(solution.variables[4])
        var6.append(solution.variables[5])
     
    feasible_obj1 = obj1
    feasible_obj2 = obj2
    
    feasible_var1 = var1
    feasible_var2 = var2
    feasible_var3 = var3
    feasible_var4 = var4
    feasible_var5 = var5
    feasible_var6 = var6
    
    
    
    n_dominated = nondominated(algorithm.result)    # 非劣解を抽出する
    obj1 = []
    obj2 = []
    for solution in n_dominated:
        obj1.append(solution.objectives[0])
        obj2.append(solution.objectives[1])
    pareto_obj = solution.objectives
    pareto_var = solution.variables
  
        
    #再エネ、再生材なしのときの計算
    materials_mass_balance = np.zeros(num_product)
    energy_mass_balance = np.zeros(num_product)
    CO2_non_Renewable = np.zeros(num_product)
    cost_non_Renewable = np.zeros(num_product)
    materials_total = 0.0
    energy_total = 0.0
    CO2, cost_procurement, cost_labor, cost_equipment, cost_electricity, cost_transportation, cost_CO2 = LCA.CO2_COST(procurement, basic_unit, num_product, A_BOM, A_BOP, B_BOM, B_BOP, C_BOM, C_BOP, materials_mass_balance, energy_mass_balance, materials_total, energy_total)
    for k in range(num_product):
        CO2_non_Renewable[k] = sum(CO2[k][:])
        cost_non_Renewable[k] = sum(cost_procurement[k][:]) + sum(cost_labor[k][:]) + sum(cost_equipment[k][:]) \
            + sum(cost_electricity[k][:]) + sum(cost_transportation[k][:]) + sum(cost_CO2[k][:]) 
    weight_limit = np.zeros(num_product)
    weight_limit[0] = 0.3
    weight_limit[1] = 0.3
    weight_limit[2] = 0.3
        
    #再生材調達量
    materials_total = solution.variables[0]
    #再エネ調達量
    energy_total = solution.variables[1]
    
    materials_mass_balance = np.zeros(num_product)
    energy_mass_balance = np.zeros(num_product)
     
    materials_mass_balance[0] = solution.variables[2]
    materials_mass_balance[1] = solution.variables[3]
    materials_mass_balance[2] = 1 - materials_mass_balance[0] - materials_mass_balance[1]
    
    energy_mass_balance[0] = solution.variables[4]
    energy_mass_balance[1] = solution.variables[5]
    energy_mass_balance[2] = 1 - energy_mass_balance[0] - energy_mass_balance[1]
    
    CO2, cost_procurement, cost_labor, cost_equipment, cost_electricity, cost_transportation, cost_CO2 = LCA.CO2_COST(procurement, basic_unit, num_product, A_BOM, A_BOP, B_BOM, B_BOP, C_BOM, C_BOP, materials_mass_balance, energy_mass_balance, materials_total, energy_total)
    num_parts = np.zeros(num_product, dtype=int)
    total_number = np.zeros(num_product)
    total_weight = np.zeros(num_product)
    for k in range(num_product):
        if k == 0:
            BOM = A_BOM
        elif k == 1:
            BOM = B_BOM
        elif k == 2:
            BOM = C_BOM
        else:
            print("製品の情報が足りません")
        for row in BOM:
            if row[0] == 1:
                num_parts[k] += 1
        total_number[k] = procurement[(num_parts[k]+1)*k][6]
        total_weight[k] = BOM[0][6] * BOM[0][7] * total_number[k] 
            
    total_CO2 = np.zeros(num_product)
    total_cost  = np.zeros(num_product)
    for k in range(num_product):
        total_CO2[k] = sum(CO2[k][:])
    error = 0
    count = 0
    for i in range(num_product):
        condition_CO2 = (CO2_non_Renewable[i] - total_CO2[i]) / CO2_non_Renewable[i] - request[i]
        condition_materials = weight_limit[i] - materials_total * materials_mass_balance[i] / total_weight[i]
        if condition_CO2 < 0:
            count += 1
            error += condition_CO2 ** 2
        if condition_materials < 0:
            count += 1
            error += condition_materials ** 2
    if count == 0:
        beter_obj1 = feasible_obj1
        beter_obj2 = feasible_obj2
        
        beter_var1 = feasible_var1
        beter_var2 = feasible_var2
        beter_var3 = feasible_var3
        beter_var4 = feasible_var4
        beter_var5 = feasible_var5
        beter_var6 = feasible_var6
        beter_pareto_obj = pareto_obj
        beter_pareto_var = pareto_var
        better_materials_mass_balance = np.zeros(num_product)
        better_energy_mass_balance = np.zeros(num_product)

        better_materials_total = solution.variables[0]
        better_energy_total = solution.variables[1]
         
        for k in range(num_product-1):
            better_materials_mass_balance[k] = solution.variables[k+2]
        better_materials_mass_balance[num_product-1] = 1 - sum(materials_mass_balance[:-1])
             
        for k in range(num_product-1):
            better_energy_mass_balance[k] = solution.variables[k+num_product+1]
        better_energy_mass_balance[num_product-1] = 1 - sum(better_energy_mass_balance[:-1])
        print("収束したタイミング",r)
        break
    else:
        error = error / count
        error = np.sqrt(error)
        print("error =",error)
        if error <= better_error:
            better_error = error
            beter_obj1 = feasible_obj1
            beter_obj2 = feasible_obj2
            
            beter_var1 = feasible_var1
            beter_var2 = feasible_var2
            beter_var3 = feasible_var3
            beter_var4 = feasible_var4
            beter_var5 = feasible_var5
            beter_var6 = feasible_var6
            beter_pareto_obj = pareto_obj
            beter_pareto_var = pareto_var
            better_materials_mass_balance = np.zeros(num_product)
            better_energy_mass_balance = np.zeros(num_product)

            better_materials_total = solution.variables[0]
            better_energy_total = solution.variables[1]
             
            for k in range(num_product-1):
                better_materials_mass_balance[k] = solution.variables[k+2]
            better_materials_mass_balance[num_product-1] = 1 - sum(materials_mass_balance[:-1])
                 
            for k in range(num_product-1):
                better_energy_mass_balance[k] = solution.variables[k+num_product+1]
            better_energy_mass_balance[num_product-1] = 1 - sum(better_energy_mass_balance[:-1])
        
        if better_error <= acceptable_error:
            print("収束したタイミング",r)
            break

#--------------------------------------------------------------------------------------------------------------------------------------   
#----------------------------------------------------出力------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------
#再エネ、再生材なしのときの計算
materials_mass_balance = np.zeros(num_product)
energy_mass_balance = np.zeros(num_product)
CO2_non_Renewable = np.zeros(num_product)
cost_non_Renewable = np.zeros(num_product)
materials_total = 0.0
energy_total = 0.0
CO2, cost_procurement, cost_labor, cost_equipment, cost_electricity, cost_transportation, cost_CO2 = LCA.CO2_COST(procurement, basic_unit, num_product, A_BOM, A_BOP, B_BOM, B_BOP, C_BOM, C_BOP, materials_mass_balance, energy_mass_balance, materials_total, energy_total)
for k in range(num_product):
    CO2_non_Renewable[k] = sum(CO2[k][:])
    cost_non_Renewable[k] = sum(cost_procurement[k][:]) + sum(cost_labor[k][:]) + sum(cost_equipment[k][:]) \
        + sum(cost_electricity[k][:]) + sum(cost_transportation[k][:]) + sum(cost_CO2[k][:]) 


#------得られた結果をもう一度確かめるために出力---
#使用可能の再生材（顧客要望）
weight_limit = np.zeros(num_product)
weight_limit[0] = 0.3
weight_limit[1] = 0.3
weight_limit[2] = 0.3

profit_margin = np.zeros(100)
CO2_reduction_rate = np.zeros(100)
CO2_achievement_rate = np.zeros(100)
materials_achievement_rate = np.zeros(100)
achievement_rate = np.zeros(100)
    # CSVファイルを開く（存在しない場合は新規作成）
import csv
with open('data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)  # CSVファイルへの書き込み用のwriterを作成
    writer.writerow(["CO2 reduction rate", "Profit magin", "achievement rate","Amount of recycled materials procured", "Amount of renewable energy procured", "materials mass balance_A", "materials mass balance_B", "materials mass balance_C", "energy mass balance_A", "energy mass balance_B", "energy mass balance_C", "CO2 reduction rate_A", "CO2 reduction rate_B", "CO2 reduction rate_C", "Recycle nmaterials rate_A", "Recycle nmaterials rate_B", "Recycle nmaterials rate_C"])
    for i in range(100):
    #これをループさせて、プロットすべてにおける情報をすべて記録する。
        better_materials_total = beter_var1[i]
        better_energy_total = beter_var2[i]
        better_materials_mass_balance[0] = beter_var3[i]
        better_materials_mass_balance[1] = beter_var4[i]
        better_materials_mass_balance[2] = 1 - sum(better_materials_mass_balance[:-1])

        better_energy_mass_balance[0] = beter_var5[i]
        better_energy_mass_balance[1] = beter_var6[i]
        better_energy_mass_balance[2] = 1 - sum(better_energy_mass_balance[:-1])

    
        if better_materials_mass_balance[2] > 0 and better_energy_mass_balance[2] > 0:
            CO2, cost_procurement, cost_labor, cost_equipment, cost_electricity, cost_transportation, cost_CO2 = LCA.CO2_COST(procurement, basic_unit, num_product, A_BOM, A_BOP, B_BOM, B_BOP, C_BOM, C_BOP, better_materials_mass_balance, better_energy_mass_balance, better_materials_total, better_energy_total)
            num_parts = np.zeros(num_product, dtype=int)
            total_number = np.zeros(num_product)
            total_weight = np.zeros(num_product)
            for k in range(num_product):
                if k == 0:
                    BOM = A_BOM
                elif k == 1:
                    BOM = B_BOM
                elif k == 2:
                    BOM = C_BOM
                else:
                    print("製品の情報が足りません")
                for row in BOM:
                    if row[0] == 1:
                        num_parts[k] += 1
                total_number[k] = procurement[(num_parts[k]+1)*k][6]
                total_weight[k] = BOM[0][6] * BOM[0][7] * total_number[k] 
                    
            total_CO2 = np.zeros(num_product)
            total_cost  = np.zeros(num_product)
            for k in range(num_product):
                total_CO2[k] = sum(CO2[k][:])
                total_cost[k] = sum(cost_procurement[k][:]) + sum(cost_labor[k][:]) + sum(cost_equipment[k][:]) \
                    + sum(cost_electricity[k][:]) + sum(cost_transportation[k][:]) + sum(cost_CO2[k][:])   
                    
            CO2_reduction_rate[i] = (sum(CO2_non_Renewable) - sum(total_CO2)) / sum(CO2_non_Renewable) * 100
            profit_margin[i] = (sum(cost_non_Renewable) * 1.2 - sum(total_cost)) / (sum(cost_non_Renewable) * 1.2) * 100
            
            
            for k in range(num_product):
                condition_CO2 = (CO2_non_Renewable[k] - total_CO2[k]) / CO2_non_Renewable[k] - request[k]
                condition_materials = weight_limit[k] - better_materials_total * better_materials_mass_balance[k] / total_weight[k]
    
                if condition_CO2 > 0:
                    CO2_achievement_rate[i]  += 100
                else:
                    CO2_achievement_rate[i]  += (CO2_non_Renewable[k] - total_CO2[k]) / CO2_non_Renewable[k] / request[k] * 100

                if condition_materials > 0:
                    materials_achievement_rate[i] += 100
                else:
                    materials_achievement_rate[i] += 100 - (better_materials_total * better_materials_mass_balance[k] / total_weight[k] - weight_limit[k]) / weight_limit[k] * 100
       
            CO2_achievement_rate[i]  = CO2_achievement_rate[i] / num_product
            materials_achievement_rate[i]  = materials_achievement_rate[i] / num_product
            achievement_rate[i] = (CO2_achievement_rate[i] + materials_achievement_rate[i]) / 2
         
            condition = np.zeros(2*num_product)
            for k in range(num_product):
                condition[k] = (CO2_non_Renewable[k] - total_CO2[k]) / CO2_non_Renewable[k]
                condition[k+num_product] = better_materials_total * better_materials_mass_balance[k] / total_weight[k]
        
        
            writer = csv.writer(file)  # CSVファイルへの書き込み用のwriterを作成
                  
            writer.writerow([CO2_reduction_rate[i], profit_margin[i], achievement_rate[i], better_materials_total, better_energy_total, better_materials_mass_balance[0], better_materials_mass_balance[1], better_materials_mass_balance[2], better_energy_mass_balance[0], better_energy_mass_balance[1], better_energy_mass_balance[2], condition[0], condition[1], condition[2], condition[3], condition[4], condition[5]])


better_materials_total = beter_pareto_var[0]
better_energy_total = beter_pareto_var[1]
better_materials_mass_balance[0] = beter_pareto_var[2]
better_materials_mass_balance[1] = beter_pareto_var[3]
better_materials_mass_balance[2] = 1 - sum(better_materials_mass_balance[:-1])

better_energy_mass_balance[0] = beter_pareto_var[4]
better_energy_mass_balance[1] = beter_pareto_var[5]
better_energy_mass_balance[2] = 1 - sum(better_energy_mass_balance[:-1])

CO2, cost_procurement, cost_labor, cost_equipment, cost_electricity, cost_transportation, cost_CO2 = LCA.CO2_COST(procurement, basic_unit, num_product, A_BOM, A_BOP, B_BOM, B_BOP, C_BOM, C_BOP, better_materials_mass_balance, better_energy_mass_balance, better_materials_total, better_energy_total)         
num_parts = np.zeros(num_product, dtype=int)          
total_number = np.zeros(num_product)    
total_weight = np.zeros(num_product)   
for k in range(num_product):
    if k == 0:
        BOM = A_BOM
    elif k == 1:
        BOM = B_BOM
    elif k == 2:
        BOM = C_BOM
    else:
        print("製品の情報が足りません")
    for row in BOM:
        if row[0] == 1:
            num_parts[k] += 1
    total_number[k] = procurement[(num_parts[k]+1)*k][6]
    total_weight[k] = BOM[0][6] * BOM[0][7] * total_number[k] 
                    
total_CO2 = np.zeros(num_product)
total_cost  = np.zeros(num_product)
for k in range(num_product):
    total_CO2[k] = sum(CO2[k][:])
    total_cost[k] = sum(cost_procurement[k][:]) + sum(cost_labor[k][:]) + sum(cost_equipment[k][:]) \
        + sum(cost_electricity[k][:]) + sum(cost_transportation[k][:]) + sum(cost_CO2[k][:])   
                    
   #制約条件
condition = np.zeros(2*num_product)
for i in range(num_product):
    condition[i] = (CO2_non_Renewable[i] - total_CO2[i]) / CO2_non_Renewable[i]

pareto_CO2_achievement_rate = 0
pareto_materials_achievement_rate = 0
pareto_achievement_rate = 0

pareto_condition_materials = np.zeros(num_product)
pareto_condition_materials[0] = weight_limit[0] - beter_pareto_var[0] * beter_pareto_var[4] / total_weight[0]
pareto_condition_materials[1] = weight_limit[1] - beter_pareto_var[0] * beter_pareto_var[5] / total_weight[1]
pareto_condition_materials[2] = weight_limit[2] - beter_pareto_var[0] * (1 - beter_pareto_var[4] - beter_pareto_var[5]) / total_weight[2]

for k in range(num_product):
    condition_CO2 = (CO2_non_Renewable[k] - total_CO2[k]) / CO2_non_Renewable[k] - request[k]

    if condition_CO2 > 0:
        pareto_CO2_achievement_rate += 100
    else:
        pareto_CO2_achievement_rate += (CO2_non_Renewable[k] - total_CO2[k]) / CO2_non_Renewable[k] / request[k] * 100

    if pareto_condition_materials[k] > 0:
        pareto_materials_achievement_rate += 100
    else:
        pareto_materials_achievement_rate += 100 + pareto_condition_materials[k] / weight_limit[k] * 100

pareto_CO2_achievement_rate = pareto_CO2_achievement_rate / num_product
pareto_materials_achievement_rate = pareto_materials_achievement_rate / num_product
pareto_achievement_rate = (pareto_CO2_achievement_rate + pareto_materials_achievement_rate) / 2                

print("CO2排出量合計",sum(total_CO2),"kg-CO2/month")
print("コスト合計",sum(total_cost),"円")
print()
print("再生材調達量",beter_pareto_var[0],"kg/month")
print("再エネ調達量",beter_pareto_var[1],"kWh/month")
print()
print("Aの再生材マスバランス",beter_pareto_var[2] * 100,"%")
print("Bの再生材マスバランス",beter_pareto_var[3] * 100,"%")
print("Cの再生材マスバランス",(1.0 - beter_pareto_var[2] - beter_pareto_var[3]) * 100,"%")
print()
print("Aの再エネマスバランス",beter_pareto_var[4] * 100,"%")
print("Bの再エネマスバランス",beter_pareto_var[5] * 100,"%")
print("Cの再エネマスバランス",(1.0 - beter_pareto_var[4] - beter_pareto_var[5]) * 100,"%")
print()
print("AのCO2削減率",condition[0] * 100,"%")
print("BのCO2削減率",condition[1] * 100,"%")
print("CのCO2削減率",condition[2] * 100,"%")
print("全体のCO2削減率",beter_pareto_obj[0],"%")
print()
print("Aの再生材使用率",beter_pareto_var[0] * beter_pareto_var[2] / total_weight[0] * 100,"%")
print("Bの再生材使用率",beter_pareto_var[0] * beter_pareto_var[3] / total_weight[1] * 100,"%")
print("Cの再生材使用率",beter_pareto_var[0] * (1 - beter_pareto_var[2] - beter_pareto_var[3]) / total_weight[2] * 100,"%")
print()
print("Aの利益率",(cost_non_Renewable[0] * 1.2 - total_cost[0]) / (cost_non_Renewable[0] * 1.2) * 100,"%")
print("Bの利益率",(cost_non_Renewable[1] * 1.2 - total_cost[1]) / (cost_non_Renewable[1] * 1.2) * 100,"%")
print("Cの利益率",(cost_non_Renewable[2] * 1.2 - total_cost[2]) / (cost_non_Renewable[2] * 1.2) * 100,"%")
print("全体の利益率",(sum(cost_non_Renewable) * 1.2 - sum(total_cost)) / (sum(cost_non_Renewable) * 1.2) * 100,"%")


import csv
# データを結合してリストにする
raw_data = list(zip(CO2_reduction_rate, profit_margin, achievement_rate))
# CSVファイルを書き込みモードで開く
with open("raw_data.csv", "w", newline="") as csv_file:
    # CSVファイルの書き込みオブジェクトを作成
    csv_writer = csv.writer(csv_file)
    
    # データをCSVファイルに書き込む
    csv_writer.writerow(["CO2 reduction rate", "Profit magin", "achievement rate"]) 
    csv_writer.writerows(raw_data) 

#--------------------------------------------------------------------------------------------------------------
# カラーマップ
cm = plt.cm.get_cmap('seismic')

# フォントの種類とサイズを設定する。
plt.rcParams['font.size'] = 14
plt.rcParams['font.family'] = 'Times New Roman'
     
# グラフの入れ物を用意する。
#fig = plt.figure(figsize=(6, 5))
fig = plt.figure()
#ax = fig.add_subplot(111)
# axをfigureに設定する
ax = fig.add_subplot(1, 1, 1)
plt.xlim(0, 25)
# 軸のラベルを設定する。
ax.set_xlabel('CO2 reduction rate')
ax.set_ylabel('Profit margin')

# axに散布図を描画、戻り値にPathCollectionを得る
mappable = ax.scatter(CO2_reduction_rate, profit_margin, c = CO2_achievement_rate, vmin=0, vmax=100, s=15, cmap=cm)
mappable = ax.scatter(beter_pareto_obj[0], beter_pareto_obj[1], c = pareto_CO2_achievement_rate, vmin=0, vmax=100, s=100, cmap=cm)
white = np.zeros(2)
mappable = ax.scatter(white[0], white[1], c = 50, vmin=0, vmax=100, s=100, cmap=cm)
# カラーバーを付加
cb = fig.colorbar(mappable, ax=ax)
cb.set_label("CO2 Achievement rate", loc='center')


#--------------------------------------------------------------------------------------------------------------
# カラーマップ
cm = plt.cm.get_cmap('seismic')

# フォントの種類とサイズを設定する。
plt.rcParams['font.size'] = 14
plt.rcParams['font.family'] = 'Times New Roman'
     
# グラフの入れ物を用意する。
#fig = plt.figure(figsize=(6, 5))
fig = plt.figure()
#ax = fig.add_subplot(111)
# axをfigureに設定する
ax = fig.add_subplot(1, 1, 1)
plt.xlim(0, 25)
# 軸のラベルを設定する。
ax.set_xlabel('CO2 reduction rate')
ax.set_ylabel('Profit margin')

# axに散布図を描画、戻り値にPathCollectionを得る
mappable = ax.scatter(CO2_reduction_rate, profit_margin, c = materials_achievement_rate, vmin=0, vmax=100, s=15, cmap=cm)
mappable = ax.scatter(beter_pareto_obj[0], beter_pareto_obj[1], c = pareto_materials_achievement_rate, vmin=0, vmax=100, s=100, cmap=cm)
white = np.zeros(2)
mappable = ax.scatter(white[0], white[1], c = 50, vmin=0, vmax=100, s=100, cmap=cm)
# カラーバーを付加
cb = fig.colorbar(mappable, ax=ax)
cb.set_label("materials limit", loc='center')


#--------------------------------------------------------------------------------------------------------------
# カラーマップ
cm = plt.cm.get_cmap('seismic')

# フォントの種類とサイズを設定する。
plt.rcParams['font.size'] = 14
plt.rcParams['font.family'] = 'Times New Roman'
     
# グラフの入れ物を用意する。
#fig = plt.figure(figsize=(6, 5))
fig = plt.figure()
#ax = fig.add_subplot(111)
# axをfigureに設定する
ax = fig.add_subplot(1, 1, 1)
plt.xlim(0, 25)
# 軸のラベルを設定する。
ax.set_xlabel('CO2 reduction rate')
ax.set_ylabel('Profit margin')
for i in range(100):
    if materials_achievement_rate[i] != 100:
        CO2_reduction_rate[i] = 0
        profit_margin[i] = 0
        achievement_rate[i] = 0

# axに散布図を描画、戻り値にPathCollectionを得る
mappable = ax.scatter(CO2_reduction_rate, profit_margin, c = CO2_achievement_rate, vmin=0, vmax=100, s=15, cmap=cm)
mappable = ax.scatter(beter_pareto_obj[0], beter_pareto_obj[1], c = pareto_achievement_rate, vmin=0, vmax=100, s=100, cmap=cm)
white = np.zeros(2)
mappable = ax.scatter(white[0], white[1], c = 50, vmin=0, vmax=100, s=100, cmap=cm)
# カラーバーを付加
cb = fig.colorbar(mappable, ax=ax)
cb.set_label("CO2 Achievement rate", loc='center')