#輸送(自社加工)
def transportation_own(i, BOP, basic_unit):
    total_weight = BOP[i][5] * BOP[i][7]
    load = BOP[i][8]
    distance = BOP[i][9]
    CO2 = total_weight / load * distance * basic_unit[2][1]
    cost_transportation = BOP[i][15]
    if BOP[0][0] == "R0001":
        cost_CO2 = CO2 * basic_unit[9][1]
    elif BOP[0][0] == "S0001":
        cost_CO2 = CO2 * basic_unit[10][1]
    elif BOP[0][0] == "T0001":
        cost_CO2 = CO2 * basic_unit[11][1]
    else:
        print("Unknown Product")
    return(CO2, cost_transportation, cost_CO2)


#輸送(自社加工以外)
def transportation_other(i, BOP, basic_unit):
    total_weight = BOP[i][5] * BOP[i][7]
    load = BOP[i][8]
    distance = BOP[i][9]
    CO2 = total_weight / load * distance * basic_unit[2][1]
    if BOP[0][0] == "R0001":
        cost_CO2 = CO2 * basic_unit[9][1]
    elif BOP[0][0] == "S0001":
        cost_CO2 = CO2 * basic_unit[10][1]
    elif BOP[0][0] == "T0001":
        cost_CO2 = CO2 * basic_unit[11][1]
    else:
        print("Unknown Product")
    return(CO2, cost_CO2)




#自社加工
def process_own(i, BOP, all_electricity, total_electricity, count_proceses_own, energy_total, energy_mass_balance, basic_unit):
    if energy_total >=  100000:
        energy_total_1 = 100000
        energy_total_2 = energy_total - energy_total_1
    else:
        energy_total_1 = energy_total
        energy_total_2 = 0
    
    energy_sum = BOP[i][10]
    renewable_energy_1 = energy_mass_balance * energy_total_1 / count_proceses_own
    renewable_energy_2 = energy_mass_balance * energy_total_2 / count_proceses_own
    thermal_energy = energy_sum - renewable_energy_1 - renewable_energy_2
    CO2 = thermal_energy * basic_unit[3][1]
    cost_labor = BOP[i][13]
    cost_equipment = BOP[i][14]
    renewable_energy_before_1 = total_electricity * energy_total_1 / all_electricity / count_proceses_own
    renewable_energy_before_2 = total_electricity * energy_total_2 / all_electricity / count_proceses_own
    thermal_energy_before = BOP[i][10] - renewable_energy_before_1 - renewable_energy_before_2
    cost_electricity = thermal_energy_before * basic_unit[6][1] + renewable_energy_before_1 * basic_unit[7][1] + renewable_energy_before_2 * basic_unit[8][1]
    if BOP[0][0] == "R0001":
        cost_CO2 = CO2 * basic_unit[9][1]
    elif BOP[0][0] == "S0001":
        cost_CO2 = CO2 * basic_unit[10][1]
    elif BOP[0][0] == "T0001":
        cost_CO2 = CO2 * basic_unit[11][1]
    else:
        print("Unknown Product")
    return(CO2, cost_labor, cost_equipment, cost_electricity, cost_CO2)




#他社加工
def process_other(i, BOP,basic_unit):
    energy_sum = BOP[i][10]
    CO2 = energy_sum * basic_unit[3][1]
    if BOP[0][0] == "R0001":
        cost_CO2 = CO2 * basic_unit[9][1]
    elif BOP[0][0] == "S0001":
        cost_CO2 = CO2 * basic_unit[10][1]
    elif BOP[0][0] == "T0001":
        cost_CO2 = CO2 * basic_unit[11][1]
    else:
        print("Unknown Product")
    return(CO2, cost_CO2)




#素材製造
def manufacturing(i, count_parts, BOP, all_weight, total_weight, materials_total, materials_mass_balance, procurement, basic_unit):
    partial_weight = BOP[i-1][5] * BOP[i-1][7]
    total_renewable_materials = materials_mass_balance * materials_total
    renewable_materials = total_renewable_materials * (partial_weight / total_weight)
    virgin = partial_weight - renewable_materials
    CO2 = virgin * basic_unit[0][1] + renewable_materials * basic_unit[1][1]
    if BOP[0][0] == "R0001":
        cost_CO2 = CO2 * basic_unit[9][1]
    elif BOP[0][0] == "S0001":
        cost_CO2 = CO2 * basic_unit[10][1]
    elif BOP[0][0] == "T0001":
        cost_CO2 = CO2 * basic_unit[11][1]
    else:
        print("Unknown Product")
      
    total_renewable_materials_before = total_weight * (materials_total / all_weight)
    renewable_materials_before = total_renewable_materials_before * (partial_weight / total_weight)
    virgin_before = partial_weight - renewable_materials_before
    cost_procurement = (procurement[count_parts][3] * (virgin_before / partial_weight) + procurement[count_parts][4] * (renewable_materials_before / partial_weight)) * BOP[i-1][7]
    return(CO2, cost_procurement, cost_CO2)




#リサイクル
def recycling(i, BOP, basic_unit):
    total_weight = BOP[i-1][5] * BOP[i-1][7]
    recycling_rate = BOP[i][11]
    CO2 = total_weight * recycling_rate * basic_unit[4][1]
    if BOP[0][0] == "R0001":
        cost_CO2 = CO2 * basic_unit[9][1]
    elif BOP[0][0] == "S0001":
        cost_CO2 = CO2 * basic_unit[10][1]
    elif BOP[0][0] == "T0001":
        cost_CO2 = CO2 * basic_unit[11][1]
    else:
        print("Unknown Product")
    return(CO2, cost_CO2)




#埋立
def landfill(i, BOP, basic_unit):
    total_weight = BOP[i-2][5] * BOP[i-2][7]
    landfill_rate = BOP[i][12]
    CO2 = total_weight * landfill_rate * basic_unit[5][1]
    if BOP[0][0] == "R0001":
        cost_CO2 = CO2 * basic_unit[9][1]
    elif BOP[0][0] == "S0001":
        cost_CO2 = CO2 * basic_unit[10][1]
    elif BOP[0][0] == "T0001":
        cost_CO2 = CO2 * basic_unit[11][1]
    else:
        print("Unknown Product")
    return(CO2, cost_CO2)