import streamlit as st

# Настройка страницы
st.set_page_config(page_title="Калькулятор логистики Автотехнологий", layout="wide")

st.title("🚜 Калькулятор логистики и ценообразования")
st.write("Расчет оптимальной схемы доставки с учетом рентабельности 15%")

# --- БОКОВАЯ ПАНЕЛЬ (Параметры техники) ---
st.sidebar.header("1. Параметры техники")
product_name = st.sidebar.text_input("Название техники", value="Борона БД-2.4")
cost_price = st.sidebar.number_input("Себестоимость производства (руб)", min_value=0, value=500000)
capacity_in_truck = st.sidebar.number_input("Вместимость в фуру 20т (шт)", min_value=1, value=5)
delivery_type = st.sidebar.selectbox("Тип локальной машины", ["Газель (1.5т)", "3-тонник", "5-тонник"])
local_rate = st.sidebar.number_input("Тариф локальной доставки (руб/км)", value=45 if delivery_type == "3-тонник" else 35)

# --- ОСНОВНОЙ БЛОК (Параметры логистики) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Выбор ЛЦ")
    lc_option = st.radio("Выберите логистический центр", ["ЛЦ Смоленск", "ЛЦ Екатеринбург"])
    
    if lc_option == "ЛЦ Смоленск":
        dist_factory_to_lc = 960
        truck_cost = 85000
    else:
        dist_factory_to_lc = 1750
        truck_cost = 161000

with col2:
    st.subheader("🚛 Дистанция до клиента")
    dist_lc_to_client = st.number_input("От ЛЦ до Клиента (км)", min_value=0, value=100)
    # Расчет расстояния напрямую от завода (упрощенно: Завод-ЛЦ-Клиент)
    dist_factory_to_client = st.number_input("От Завода до Клиента (км) напрямую", min_value=0, value=dist_factory_to_lc + dist_lc_to_client)

# --- ЭКОНОМИЧЕСКИЙ РАСЧЕТ ---
# 1. Схема через ЛЦ
magistral_per_unit = truck_cost / capacity_in_truck
last_mile_cost = dist_lc_to_client * local_rate
total_logistics_lc = magistral_per_unit + last_mile_cost
final_price_lc = (cost_price + total_logistics_lc) / 0.85

# 2. Схема напрямую
direct_delivery_cost = dist_factory_to_client * local_rate
final_price_direct = (cost_price + direct_delivery_cost) / 0.85

# --- ВЫВОД РЕЗУЛЬТАТОВ ---
st.divider()
res_col1, res_col2 = st.columns(2)

with res_col1:
    st.metric("Цена через ЛЦ", f"{round(final_price_lc):,} руб.")
    st.caption(f"Логистика: {round(total_logistics_lc):,} руб. (Магистраль: {round(magistral_per_unit):,})")

with res_col2:
    st.metric("Цена Напрямую", f"{round(final_price_direct):,} руб.")
    st.caption(f"Логистика: {round(direct_delivery_cost):,} руб.")

# --- ВЕРДИКТ ---
if final_price_lc < final_price_direct:
    diff = final_price_direct - final_price_lc
    st.success(f"✅ Везем через **{lc_option}**. Экономия для клиента: {round(diff):,} руб.")
else:
    diff = final_price_lc - final_price_direct
    st.warning(f"🚀 Везем **Напрямую**. Экономия: {round(diff):,} руб.")

# --- РАСЧЕТ ТОЧКИ ПЕРЕЛОМА (Автоматически) ---
# Уравнение: Magistral + (Rate * X) = Rate * (Dist_to_LC - X)
# X = (Rate * Dist_to_LC - Magistral) / (2 * Rate)
break_even_dist = (local_rate * dist_factory_to_lc - magistral_per_unit) / (2 * local_rate)

st.info(f"ℹ️ **Справочно:** Для этой техники в сторону {lc_option} точка перелома — **{round(break_even_dist)} км**. "
        f"Если клиент ближе к ЛЦ, чем это расстояние, склад выгоден.")
