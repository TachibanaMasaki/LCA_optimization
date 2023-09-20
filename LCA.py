import numpy as np
import life_stage
def CO2_COST(procurement, basic_unit, num_product, A_BOM, A_BOP, B_BOM, B_BOP, C_BOM, C_BOP, materials_mass_balance, energy_mass_balance, materials_total, energy_total):
    total_number = np.zeros(num_product)
    count_proceses_own = np.zeros(num_product)
    total_electricity = np.zeros(num_product)
    total_weight = np.zeros(num_product)
    num_parts = np.zeros(num_product, dtype=int)
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
        for row in BOM:
            if row[0] == 1:
                num_parts[k] += 1
        total_number[k] = procurement[(num_parts[k]+1)*k][6]
        total_weight[k] = BOM[0][6] * BOM[0][7] * total_number[k]
        for i in range(len(BOP)):
            if BOP[i][4] == "自社加工":
                count_proceses_own[k] += 1
                total_electricity[k] +=  BOP[i][10]
        child_CO2 = np.zeros((num_product, num_parts[k]+1))
        child_cost_labor = np.zeros((num_product, num_parts[k]+1))
        child_cost_equipment = np.zeros((num_product, num_parts[k]+1))
        child_cost_electricity = np.zeros((num_product, num_parts[k]+1))
        child_cost_transportation = np.zeros((num_product, num_parts[k]+1))
        child_cost_CO2 = np.zeros((num_product, num_parts[k]+1))
        child_cost_procurement = np.zeros((num_product, num_parts[k]+1))
        
    all_electricity = sum(total_electricity)
    all_weight = sum(total_weight)
    
    count_procurement = 0   #入力データ（調達）において、それぞれの製品ごとのデータを参照するためにカウントする。
    #--------------------------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------全体のループの開始----------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------
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
    #--------------------------------------------------------------------------------------------------------------------------------------
    #---------------------------------------------------品目の数、パーツの数を取得-------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------
        #品目の数
        first_column_elements = [row[2] for row in BOM]
        column_elements = set(first_column_elements)
        num_elements = len(column_elements)
    #--------------------------------------------------------------------------------------------------------------------------------------
    #------------------------------------------各親品番号ごとのCO2排出量、及び費用の合計を算出---------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------------
        partial_CO2 = np.zeros(num_elements)
        partial_cost_labor = np.zeros(num_elements)
        partial_cost_equipment = np.zeros(num_elements)
        partial_cost_electricity = np.zeros(num_elements)
        partial_cost_transportation = np.zeros(num_elements)
        partial_cost_CO2 = np.zeros(num_elements)
    
        num_parent = 0 #どのパーツにおける値かをカウントしていく。   
        count_parts = 0 #どの品目における値かをカウントしていく。
        
        parent = BOP[0][0]
        for i in range(len(BOP)):
            if BOP[i][0] == parent:       
                if BOP[i][4] == "輸送":
                    if BOP[i+1][4] == "自社加工":
                        CO2, cost_transportation, cost_CO2 = life_stage.transportation_own(i, BOP, basic_unit)
                        partial_CO2[num_parent] += CO2
                        partial_cost_transportation[num_parent] += cost_transportation
                        partial_cost_CO2[num_parent] += cost_CO2
                    else:
                        CO2, cost_CO2 = life_stage.transportation_other(i, BOP, basic_unit)
                        partial_CO2[num_parent] += CO2
                        partial_cost_CO2[num_parent] += cost_CO2
                        
                elif BOP[i][4] == "自社加工":
                      CO2, cost_labor, cost_equipment, cost_electricity, cost_CO2 = life_stage.process_own(i, BOP, all_electricity,  \
                                               total_electricity[k], count_proceses_own[k], energy_total, energy_mass_balance[k], basic_unit)
                      partial_CO2[num_parent] += CO2
                      partial_cost_labor[num_parent] += cost_labor
                      partial_cost_equipment[num_parent] += cost_equipment
                      partial_cost_electricity[num_parent] += cost_electricity
                      partial_cost_CO2[num_parent] += cost_CO2
                    
                elif BOP[i][4] == "他社加工":
                    if BOP[i][2] == "加工１":
                        count_parts += 1
                        count_procurement += 1
                        CO2, cost_procurement, cost_CO2 = life_stage.manufacturing(i, count_procurement, BOP,  all_weight,   \
                                              total_weight[k], materials_total, materials_mass_balance[k], procurement, basic_unit)
                        partial_CO2[num_parent] += CO2     
                        child_cost_procurement[k][count_parts] = cost_procurement
                        partial_cost_CO2[num_parent] += cost_CO2
                    CO2, cost_CO2 = life_stage.process_other(i, BOP, basic_unit)
                    partial_CO2[num_parent] += CO2
                    partial_cost_CO2[num_parent] += cost_CO2
                    
                elif BOP[i][4] == "リサイクル":
                    CO2, cost_CO2 = life_stage.recycling(i, BOP, basic_unit)
                    partial_CO2[num_parent] += CO2
                    partial_cost_CO2[num_parent] += cost_CO2
                   
                elif BOP[i][4] == "埋立":
                    CO2, cost_CO2 = life_stage.landfill(i, BOP, basic_unit)
                    partial_CO2[num_parent] += CO2
                    partial_cost_CO2[num_parent] += cost_CO2
                    
                else:
                    print("error")
                  
            else:
                parent = BOP[i][0]
                num_parent += 1
                if BOP[i][4] == "輸送":
                    if BOP[i+1][4] == "自社加工":
                        CO2, cost_transportation, cost_CO2 = life_stage.transportation_own(i, BOP, basic_unit)
                        partial_CO2[num_parent] += CO2
                        partial_cost_transportation[num_parent] += cost_transportation
                        partial_cost_CO2[num_parent] += cost_CO2
                    else:
                        CO2, cost_CO2 = life_stage.transportation_other(i, BOP, basic_unit)
                        partial_CO2[num_parent] += CO2
                        partial_cost_CO2[num_parent] += cost_CO2
                        
                elif BOP[i][4] == "自社加工":
                      CO2, cost_labor, cost_equipment, cost_electricity, cost_CO2 = life_stage.process_own(i, BOP, all_electricity,  \
                                               total_electricity[k], count_proceses_own[k], energy_total, energy_mass_balance[k], basic_unit)
                      partial_CO2[num_parent] += CO2
                      partial_cost_labor[num_parent] += cost_labor
                      partial_cost_equipment[num_parent] += cost_equipment
                      partial_cost_electricity[num_parent] += cost_electricity
                      partial_cost_CO2[num_parent] += cost_CO2
                    
                elif BOP[i][4] == "他社加工":
                    if BOP[i][2] == "加工１":
                        count_parts += 1
                        count_procurement += 1
                        CO2, cost_procurement, cost_CO2 = life_stage.manufacturing(i, count_procurement, BOP,  all_weight,   \
                                              total_weight[k], materials_total, materials_mass_balance[k], procurement, basic_unit)
                        partial_CO2[num_parent] += CO2     
                        child_cost_procurement[k][count_parts] = cost_procurement
                        partial_cost_CO2[num_parent] += cost_CO2
                    CO2, cost_CO2 = life_stage.process_other(i, BOP, basic_unit)
                    partial_CO2[num_parent] += CO2
                    partial_cost_CO2[num_parent] += cost_CO2
                    
                elif BOP[i][4] == "リサイクル":
                    CO2, cost_CO2 = life_stage.recycling(i, BOP, basic_unit)
                    partial_CO2[num_parent] += CO2
                    partial_cost_CO2[num_parent] += cost_CO2
                   
                elif BOP[i][4] == "埋立":
                    CO2, cost_CO2 = life_stage.landfill(i, BOP, basic_unit)
                    partial_CO2[num_parent] += CO2
                    partial_cost_CO2[num_parent] += cost_CO2
                    
                else:
                    print("error")
        count_procurement += 1
    #-------------------------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------各パーツごとのCO2排出量、及び費用の合計を算出---------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------------------------    
        child_CO2[k][0] = partial_CO2[0]
        child_cost_labor[k][0] = partial_cost_labor[0]
        child_cost_equipment[k][0] = partial_cost_equipment[0]
        child_cost_electricity[k][0] = partial_cost_electricity[0]
        child_cost_transportation[k][0] = partial_cost_transportation[0]
        child_cost_CO2[k][0] = partial_cost_CO2[0]
        
        num_child = 0
        for i in range(num_elements-1):
            if A_BOM[i+1][0] == 1:
                num_child += 1
                child_CO2[k][num_child] = partial_CO2[i+1]
                child_cost_labor[k][num_child] = partial_cost_labor[i+1]
                child_cost_equipment[k][num_child] = partial_cost_equipment[i+1]
                child_cost_electricity[k][num_child] = partial_cost_electricity[i+1]
                child_cost_transportation[k][num_child] = partial_cost_transportation[i+1]
                child_cost_CO2[k][num_child] = partial_cost_CO2[i+1]
            else:
                child_CO2[k][num_child] += partial_CO2[i+1]
                child_cost_labor[k][num_child] += partial_cost_labor[i+1]
                child_cost_equipment[k][num_child] += partial_cost_equipment[i+1]
                child_cost_electricity[k][num_child] += partial_cost_electricity[i+1]
                child_cost_transportation[k][num_child] += partial_cost_transportation[i+1]
                child_cost_CO2[k][num_child] += partial_cost_CO2[i+1]
    return(child_CO2, child_cost_procurement, child_cost_labor, child_cost_equipment, child_cost_electricity, child_cost_transportation, child_cost_CO2)