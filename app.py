import streamlit as st

# Настройка страницы (отключаем боковые отступы, чтобы было как на макете)
st.set_page_config(page_title="Логистика", layout="centered")

# Создаем "контейнеры", чтобы панель с ползунками всегда была снизу, 
# а красивый визуал рисовался сверху, но при этом реагировал на цифры
top_visual = st.container()
bottom_controls = st.container()

# ==========================================
# 1. ПАНЕЛЬ УПРАВЛЕНИЯ (ПОЛЗУНКИ СНИЗУ)
# ==========================================
with bottom_controls:
    st.markdown("<br><hr>", unsafe_allow_html=True) # Полоска-разделитель
    
    col1, col2 = st.columns(2)
    with col1:
        total_dist = st.slider("Общее расстояние (км)", min_value=100, max_value=5000, value=1600, step=10)
        stop_cost = st.slider("Стоимость заезда (руб)", min_value=0, max_value=20000, value=5000, step=100)
        area1 = st.slider("Точка 1: Площадь груза (кв.м)", min_value=1.0, max_value=33.0, value=9.0, step=0.5)
    
    with col2:
        tariff = st.slider("Тариф за 1 км (руб)", min_value=50, max_value=250, value=112, step=1)
        dist1 = st.slider("Точка 1: Расстояние (км)", min_value=10, max_value=total_dist, value=400, step=10)
        area2 = st.slider("Конечная точка: Площадь груза (кв.м)", min_value=1.0, max_value=33.0, value=13.0, step=0.5)

# ==========================================
# 2. МАТЕМАТИКА (Считаем как на твоем скрине)
# ==========================================
# Общая стоимость рейса
total_trip_cost = (total_dist * tariff) + stop_cost

# Считаем "работу" (площадь умножаем на пройденное расстояние)
work1 = dist1 * area1
work2 = total_dist * area2
total_work = work1 + work2

# Распределяем общую сумму пропорционально проделанной "работе"
if total_work > 0:
    cost1_total = total_trip_cost * (work1 / total_work)
    cost2_total = total_trip_cost * (work2 / total_work)
    
    # Затраты на 1 кв.м.
    cost1_per_m2 = cost1_total / area1 if area1 > 0 else 0
    cost2_per_m2 = cost2_total / area2 if area2 > 0 else 0
else:
    cost1_total = cost2_total = cost1_per_m2 = cost2_per_m2 = 0

# Красивое форматирование цифр (пробелы между тысячами, запятые)
def f_num(val, is_float=False):
    if is_float:
        return f"{val:,.2f}".replace(",", " ").replace(".", ",")
    return f"{val:,.0f}".replace(",", " ")

str_total_trip = f_num(total_trip_cost)
str_c1_tot = f_num(cost1_total)
str_c2_tot = f_num(cost2_total)
str_c1_m2 = f_num(cost1_per_m2, True)
str_c2_m2 = f_num(cost2_per_m2, True)

# Вычисляем позицию первой точки для линии (в процентах от 0 до 100)
pos1_percent = (dist1 / total_dist) * 100 if total_dist > 0 else 0

# ==========================================
# 3. ВИЗУАЛ САЙТА (HTML + CSS В СТИЛЕ МАКЕТА)
# ==========================================
with top_visual:
    html_design = f"""
    <div style="background-color: #1a1a21; padding: 30px; border-radius: 15px; font-family: sans-serif; color: white; box-shadow: 0px 4px 15px rgba(0,0,0,0.5);">
        
        <!-- ШАПКА -->
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 40px; border-bottom: 1px solid #2a2a35; padding-bottom: 20px;">
            <div style="font-size: 18px; font-weight: bold;">Калькулятор распределения логистики</div>
            <div style="display: flex; gap: 30px; text-align: left;">
                <div>
                    <div style="font-size: 10px; color: #a0a0a0; text-transform: uppercase;">Общая стоимость рейса</div>
                    <div style="font-size: 16px; font-weight: bold;">{str_total_trip} ₽</div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #a0a0a0; text-transform: uppercase;">Всего км</div>
                    <div style="font-size: 16px; font-weight: bold;">{total_dist} км</div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #a0a0a0; text-transform: uppercase;">Тариф</div>
                    <div style="font-size: 16px; font-weight: bold;">{tariff} ₽/км</div>
                </div>
            </div>
        </div>

        <!-- ЛИНИЯ МАРШРУТА -->
        <div style="position: relative; width: 100%; height: 80px; margin-bottom: 40px;">
            <!-- Серая полоса -->
            <div style="position: absolute; top: 40px; left: 5%; right: 5%; height: 6px; background-color: #3b3b4d; border-radius: 3px;"></div>
            
            <!-- Старт -->
            <div style="position: absolute; left: 5%; top: 10px; transform: translateX(-50%); text-align: center;">
                <div style="color: #8a8a9a; font-size: 20px;">📍</div>
                <div style="width: 14px; height: 14px; background: #1a1a21; border: 3px solid #8a8a9a; border-radius: 50%; margin: 2px auto; position: relative; z-index: 2;"></div>
                <div style="border: 1px solid #8a8a9a; border-radius: 15px; padding: 4px 14px; font-size: 10px; margin-top: 5px;">СТАРТ</div>
            </div>

            <!-- Точка 1 (Движущаяся) -->
            <div style="position: absolute; left: {5 + (pos1_percent * 0.9)}%; top: 0px; transform: translateX(-50%); text-align: center; z-index: 10;">
                <div style="color: #4a90e2; font-size: 22px; margin-bottom: 5px;">🚚</div>
                <div style="width: 22px; height: 22px; background: #4a90e2; border-radius: 50%; margin: -2px auto 2px auto; border: 4px solid #1a1a21;"></div>
                <div style="border: 1px solid #4a90e2; border-radius: 15px; padding: 4px 14px; font-size: 10px; color: #4a90e2; white-space: nowrap;">T1: {dist1}КМ</div>
            </div>

            <!-- Финиш -->
            <div style="position: absolute; left: 95%; top: 10px; transform: translateX(-50%); text-align: center;">
                <div style="color: #66cc66; font-size: 20px;">🏁</div>
                <div style="width: 22px; height: 22px; background: #66cc66; border-radius: 50%; margin: 2px auto; border: 4px solid #1a1a21;"></div>
                <div style="border: 1px solid #66cc66; border-radius: 15px; padding: 4px 14px; font-size: 10px; color: #66cc66; white-space: nowrap;">ФИНИШ: {total_dist}КМ</div>
            </div>
        </div>

        <!-- СИНИЙ БЛОК (ТОЧКА 1) -->
        <div style="border: 2px solid #4a90e2; border-radius: 12px; padding: 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; background-color: #22222d;">
            <div>
                <div style="color: #a0a0a0; font-size: 14px; font-weight: bold; margin-bottom: 12px;">ТОЧКА 1 (ПРОМЕЖУТОЧНАЯ)</div>
                <div style="color: #d0d0d0; font-size: 12px;">Затраты на 1 кв.м:</div>
                <div style="color: white; font-size: 18px; font-weight: bold;">{str_c1_m2} ₽</div>
            </div>
            <div style="text-align: right;">
                <div style="color: white; font-size: 12px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase;">Сумма за точку</div>
                <div style="color: #4a90e2; font-size: 24px; font-weight: bold;">{str_c1_tot} ₽</div>
            </div>
        </div>

        <!-- ЗЕЛЕНЫЙ БЛОК (ФИНИШ) -->
        <div style="border: 2px solid #66cc66; border-radius: 12px; padding: 20px; display: flex; justify-content: space-between; align-items: center; background-color: #22222d;">
            <div>
                <div style="color: #a0a0a0; font-size: 14px; font-weight: bold; margin-bottom: 12px;">КОНЕЧНАЯ ТОЧКА</div>
                <div style="color: #d0d0d0; font-size: 12px;">Затраты на 1 кв.м:</div>
                <div style="color: white; font-size: 18px; font-weight: bold;">{str_c2_m2} ₽</div>
            </div>
            <div style="text-align: right;">
                <div style="color: white; font-size: 12px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase;">Сумма за точку</div>
                <div style="color: #66cc66; font-size: 24px; font-weight: bold;">{str_c2_tot} ₽</div>
            </div>
        </div>
        
    </div>
    """
    
    # Отрисовываем весь дизайн на сайте
    st.markdown(html_design, unsafe_allow_html=True)
