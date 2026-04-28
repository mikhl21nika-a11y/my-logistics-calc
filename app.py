import streamlit as st

# Настройка страницы на всю ширину для красивого отображения
st.set_page_config(page_title="Калькулятор логистики", layout="wide")

# ==========================================
# 1. СТИЛИ И ДИЗАЙН (ТЕМНАЯ ТЕМА)
# ==========================================
st.markdown("""
    <style>
    .metric-box { background-color: #23232e; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #3a3a4a;}
    .big-value { font-size: 28px; font-weight: bold; color: white;}
    .small-label { font-size: 12px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 1px;}
    .title-text { font-size: 24px; font-weight: bold; color: white; margin-top: 10px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ПАНЕЛЬ НАСТРОЕК (ПОЛЗУНКИ)
# ==========================================
st.markdown("### ⚙️ Ввод данных")
col1, col2 = st.columns(2)

with col1:
    total_dist = st.slider("Общий путь (км)", min_value=100, max_value=5000, value=1600, step=10)
    stop_cost = st.slider("Заезд на точку (руб)", min_value=0, max_value=20000, value=5000, step=500)
    load_coef = st.slider("Коэф. загрузки", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
    area1 = st.slider("Точка 1: Площадь (м²)", min_value=1.0, max_value=33.0, value=8.0, step=0.1)
    area2 = st.slider("Точка 2: Площадь (м²)", min_value=1.0, max_value=33.0, value=10.0, step=0.1)

with col2:
    tariff = st.slider("Тариф (руб/км)", min_value=10, max_value=200, value=90, step=1)
    capacity = st.slider("Вместимость (м²)", min_value=10.0, max_value=100.0, value=33.0, step=1.0)
    dist1 = st.slider("Точка 1: Расстояние (км)", min_value=10, max_value=total_dist, value=400, step=10)
    dist2 = st.slider("Точка 2: Расстояние (км)", min_value=dist1, max_value=total_dist, value=900, step=10)
    area_final = st.slider("Конечная: Площадь (м²)", min_value=1.0, max_value=33.0, value=5.1, step=0.1)

# ==========================================
# 3. МАТЕМАТИКА И РАСЧЕТЫ (Метод Кв.км)
# ==========================================
# Общие показатели
total_area = area1 + area2 + area_final
eff_capacity = capacity * load_coef
trip_cost = (total_dist * tariff) + (2 * stop_cost) # 2 промежуточные точки выгрузки

# Считаем "работу" (площадь * расстояние)
work1 = dist1 * area1
work2 = dist2 * area2
work3 = total_dist * area_final
total_work = work1 + work2 + work3

# Распределяем стоимость пропорционально работе
if total_work > 0:
    cost1_total = trip_cost * (work1 / total_work)
    cost2_total = trip_cost * (work2 / total_work)
    cost3_total = trip_cost * (work3 / total_work)
    
    # Стоимость на 1 м2 для каждой точки
    cost1_per_m2 = cost1_total / area1 if area1 > 0 else 0
    cost2_per_m2 = cost2_total / area2 if area2 > 0 else 0
    cost3_per_m2 = cost3_total / area_final if area_final > 0 else 0
else:
    cost1_per_m2 = cost2_per_m2 = cost3_per_m2 = 0

# Форматирование чисел для красоты (замена запятых на пробелы)
f_trip_cost = f"{trip_cost:,.0f}".replace(',', ' ')
f_cost1 = f"{cost1_per_m2:,.0f}".replace(',', ' ')
f_cost2 = f"{cost2_per_m2:,.0f}".replace(',', ' ')
f_cost3 = f"{cost3_per_m2:,.0f}".replace(',', ' ')

# ==========================================
# 4. ВЫВОД РЕЗУЛЬТАТОВ (ВИЗУАЛ)
# ==========================================
st.markdown("---")

# Верхняя плашка со статистикой
st.markdown(f"""
<div class="metric-box">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div class="title-text">Калькулятор распределения затрат</div>
        <div style="text-align: right; padding: 10px;">
            <div class="small-label">Стоимость рейса</div>
            <div class="big-value">{f_trip_cost} ₽</div>
        </div>
        <div style="text-align: right; padding: 10px;">
            <div class="small-label">Расчетная вместимость</div>
            <div class="big-value">{eff_capacity:.1f} м²</div>
        </div>
        <div style="text-align: right; padding: 10px;">
            <div class="small-label">Груз всего</div>
            <div class="big-value">{total_area:.1f} м²</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Предупреждение о перегрузе
if total_area >= eff_capacity:
    st.warning("⚠️ **Перегруз:** Сумма грузов превышает или равна расчетной вместимости!")
else:
    st.success("✅ Загрузка в пределах нормы.")

# Индикатор заполненности (прогресс-бар)
fill_percentage = min((total_area / capacity) * 100, 100)
st.markdown(f"<div class='small-label' style='margin-bottom: 5px;'>Заполненность кузова: {fill_percentage:.1f}%</div>", unsafe_allow_html=True)
st.progress(int(fill_percentage))

# Рисуем красивый график маршрута (HTML+CSS)
pos1 = (dist1 / total_dist) * 100
pos2 = (dist2 / total_dist) * 100
pos3 = 100

html_visual = f"""
<div style="background-color: #1a1a24; padding: 80px 40px 60px 40px; border-radius: 10px; margin-top: 30px; border: 1px solid #3a3a4a;">
    <div style="color: #ffffff; font-size: 18px; font-weight: bold; margin-bottom: 5px;">Распределение затрат (Метод Кв.км)</div>
    <div style="color: #a0a0a0; font-size: 12px; margin-bottom: 60px;">Доля стоимости = (Расстояние точки × Объем точки) / Суммарная работа</div>
    
    <!-- Сама линия графика -->
    <div style="height: 4px; background-color: #4a4a5a; width: 100%; position: relative;">
        
        <!-- Точка 1 -->
        <div style="position: absolute; left: {pos1}%; top: -35px; transform: translateX(-50%); text-align: center; width: 120px;">
            <div style="border: 2px solid #5c85d6; border-radius: 20px; padding: 5px; background: #23232e; color: white; font-weight: bold; font-size: 14px; margin-bottom: 8px;">
                {f_cost1} ₽/м²
            </div>
            <div style="font-size: 24px; margin-bottom: 5px;">📍</div>
            <div style="color: #d0d0d0; font-size: 14px; font-weight: bold;">{dist1} км</div>
            <div style="color: #a0a0a0; font-size: 12px;">{area1} м²</div>
        </div>

        <!-- Точка 2 -->
        <div style="position: absolute; left: {pos2}%; top: -35px; transform: translateX(-50%); text-align: center; width: 120px;">
            <div style="border: 2px solid #66cc66; border-radius: 20px; padding: 5px; background: #23232e; color: white; font-weight: bold; font-size: 14px; margin-bottom: 8px;">
                {f_cost2} ₽/м²
            </div>
            <div style="font-size: 24px; margin-bottom: 5px;">🚚</div>
            <div style="color: #d0d0d0; font-size: 14px; font-weight: bold;">{dist2} км</div>
            <div style="color: #a0a0a0; font-size: 12px;">{area2} м²</div>
        </div>

        <!-- Конечная -->
        <div style="position: absolute; left: {pos3}%; top: -35px; transform: translateX(-50%); text-align: center; width: 120px;">
            <div style="border: 2px solid #d6a35c; border-radius: 20px; padding: 5px; background: #23232e; color: white; font-weight: bold; font-size: 14px; margin-bottom: 8px;">
                {f_cost3} ₽/м²
            </div>
            <div style="font-size: 24px; margin-bottom: 5px;">🏁</div>
            <div style="color: #d0d0d0; font-size: 14px; font-weight: bold;">{total_dist} км</div>
            <div style="color: #a0a0a0; font-size: 12px;">{area_final} м²</div>
        </div>

    </div>
</div>
"""
st.markdown(html_visual, unsafe_allow_html=True)
