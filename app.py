import streamlit as st
from ortools.linear_solver import pywraplp

# Делаем красивый заголовок на сайте
st.title("🚛 Калькулятор логистики (Прототип)")
st.write("Нажмите кнопку ниже, чтобы запустить оптимизатор маршрутов и затрат.")

def solve_advanced_logistics():
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        st.error("Солвер SCIP не найден.")
        return

    # ==========================================
    # 1. НАСТРОЙКИ И ТАРИФЫ
    # ==========================================
    COST_PER_STOP = 5000       
    HEAVY_WEIGHT_LIMIT = 2000  
    COST_HEAVY_HANDLING = 15000
    COST_LIGHT_HANDLING = 500  
    MAX_AREA = 33.0            
    MAX_WEIGHT = 20000.0       

    tariffs = {
        "Белгород": 84700,
        "Ростов-на-Дону": 140400,
        "Краснодар": 180432,
        "Ставрополь": 179225
    }

    items_data = [
        {"name": "Прицеп 2ПТСЕ-4.5",  "area": 16.0, "weight": 3600, "dest": "Белгород"},
        {"name": "Косилка КРН-2.1 Б", "area": 8.0,  "weight": 580,  "dest": "Белгород"},
        {"name": "Косилка КРН-2.1 Б", "area": 8.0,  "weight": 580,  "dest": "Белгород"},
        {"name": "Опрыскиватель ОП-2500", "area": 16.0, "weight": 1350, "dest": "Ростов-на-Дону"},
        {"name": "Копалка Z-653",     "area": 4.0,  "weight": 720,  "dest": "Краснодар"},
        {"name": "Копалка Z-653",     "area": 4.0,  "weight": 720,  "dest": "Краснодар"},
        {"name": "КФ-1.5",            "area": 3.0,  "weight": 900,  "dest": "Ставрополь"}
    ]

    num_items = len(items_data)
    num_vehicles = num_items
    unique_dests = list(tariffs.keys())

    # ==========================================
    # 3. ПЕРЕМЕННЫЕ МОДЕЛИ
    # ==========================================
    x = {} 
    for i in range(num_items):
        for j in range(num_vehicles):
            x[i, j] = solver.IntVar(0, 1, f'x_{i}_{j}')

    y = {} 
    c = {} 
    for j in range(num_vehicles):
        y[j] = solver.IntVar(0, 1, f'y_{j}')
        c[j] = solver.NumVar(0, max(tariffs.values()), f'c_{j}')

    z = {} 
    for d in unique_dests:
        for j in range(num_vehicles):
            z[d, j] = solver.IntVar(0, 1, f'z_{d}_{j}')

    # ==========================================
    # 4. ОГРАНИЧЕНИЯ (ПРАВИЛА ЛОГИСТИКИ)
    # ==========================================
    for i in range(num_items):
        solver.Add(sum(x[i, j] for j in range(num_vehicles)) == 1)

    for j in range(num_vehicles):
        solver.Add(sum(items_data[i]['area'] * x[i, j] for i in range(num_items)) <= MAX_AREA * y[j])
        solver.Add(sum(items_data[i]['weight'] * x[i, j] for i in range(num_items)) <= MAX_WEIGHT * y[j])

    for i in range(num_items):
        for j in range(num_vehicles):
            dest = items_data[i]['dest']
            solver.Add(x[i, j] <= z[dest, j])

    for d in unique_dests:
        for j in range(num_vehicles):
            solver.Add(c[j] >= tariffs[d] * z[d, j])

    # ==========================================
    # 5. ЦЕЛЕВАЯ ФУНКЦИЯ
    # ==========================================
    solver.Minimize(
        solver.Sum([c[j] + COST_PER_STOP * sum(z[d, j] for d in unique_dests) for j in range(num_vehicles)])
    )

    status = solver.Solve()

    # ==========================================
    # 6. ВЫВОД РЕЗУЛЬТАТОВ НА САЙТ
    # ==========================================
    if status == pywraplp.Solver.OPTIMAL:
        st.success("✅ Оптимальный план найден!")
        total_project_cost = 0

        for j in range(num_vehicles):
            if y[j].solution_value() > 0.5:
                base_cost = c[j].solution_value()
                stops = [d for d in unique_dests if z[d, j].solution_value() > 0.5]
                stop_cost = len(stops) * COST_PER_STOP
                total_vehicle_route_cost = base_cost + stop_cost
                
                used_area = sum(items_data[i]['area'] * x[i, j].solution_value() for i in range(num_items))
                used_weight = sum(items_data[i]['weight'] * x[i, j].solution_value() for i in range(num_items))

                # Рисуем красивую карточку для каждой машины
                with st.expander(f"🚛 МАШИНА {j+1} | Маршрут: {', '.join(stops)}", expanded=True):
                    st.write(f"**Загрузка:** {used_area}/{MAX_AREA} м2 | {used_weight}/{MAX_WEIGHT} кг")
                    st.write(f"**Стоимость рейса:** {total_vehicle_route_cost:,.0f} руб.")
                    
                    for i in range(num_items):
                        if x[i, j].solution_value() > 0.5:
                            item = items_data[i]
                            transport_share = total_vehicle_route_cost * (item['area'] / used_area)
                            
                            if item['weight'] > HEAVY_WEIGHT_LIMIT:
                                handling_cost = COST_HEAVY_HANDLING
                                handling_type = "Тяжелый (>2т)"
                            else:
                                handling_cost = COST_LIGHT_HANDLING
                                handling_type = "Легкий (<2т)"
                            
                            final_item_cost = transport_share + handling_cost
                            total_project_cost += final_item_cost
                            
                            st.write(f"- 📦 {item['name']} ({item['dest']}) -> Логистика: {final_item_cost:,.0f} руб.")
                
        st.header(f"💰 ИТОГО затраты на проект: {total_project_cost:,.0f} руб.")
    else:
        st.error("Не удалось найти решение.")

# Кнопка на сайте
if st.button("🚀 Запустить расчет"):
    solve_advanced_logistics()
