import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="AI FEMM LRK EV Motor Optimizer", layout="wide")

st.title("AI FEMM LRK EV Motor Optimizer")
st.write(
    "Change LRK motor parameters like air gap, magnets, coils, and current. "
    "The app predicts torque and shows how the electric car changes."
)

# -----------------------------
# Load ML dataset
# -----------------------------
data = pd.read_csv("bldc_data.csv")

X = data[["air_gap", "magnet_thickness", "turns", "current"]]
y = data["torque"]

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# -----------------------------
# Sidebar: LRK / FEMM variables
# -----------------------------
st.sidebar.header("LRK / FEMM Motor Variables")

fixed_current = st.sidebar.slider("Fixed Current (A)", 1, 20, 8)

air_gap = st.sidebar.slider("Air Gap (mm)", 0.2, 1.5, 0.5)
magnet_diameter = st.sidebar.slider("Magnet Diameter (mm)", 3, 20, 10)
magnet_thickness = st.sidebar.slider("Magnet Thickness (mm)", 1.0, 8.0, 4.0)
coil_diameter = st.sidebar.slider("Coil / Winding Diameter (mm)", 3, 25, 12)
turns = st.sidebar.slider("Coil Turns", 5, 160, 60)

st.sidebar.divider()

st.sidebar.header("Advanced Motor Geometry")

stator_teeth = st.sidebar.slider("Stator Teeth", 6, 24, 12)
rotor_poles = st.sidebar.slider("Rotor Poles", 8, 28, 14)
rotor_radius = st.sidebar.slider("Rotor Radius (mm)", 20, 120, 50)
stator_radius = st.sidebar.slider("Stator Radius (mm)", 10, 100, 38)
slot_opening = st.sidebar.slider("Slot Opening Width (mm)", 1, 12, 4)
pole_arc = st.sidebar.slider("Pole Arc Angle (degrees)", 60, 180, 120)

st.sidebar.divider()

st.sidebar.header("EV System Variables")

battery_voltage = st.sidebar.slider("Battery Voltage (V)", 200, 1000, 400)
cooling = st.sidebar.slider("Cooling System Level", 1, 10, 5)
vehicle_mass = st.sidebar.slider("Vehicle Mass (kg)", 800, 2500, 1500)

# -----------------------------
# ML base prediction
# -----------------------------
input_data = pd.DataFrame([{
    "air_gap": air_gap,
    "magnet_thickness": magnet_thickness,
    "turns": turns,
    "current": fixed_current
}])

base_torque = model.predict(input_data)[0]

# -----------------------------
# Engineering-inspired torque model
# -----------------------------
torque = base_torque
torque += magnet_diameter * 0.018
torque += magnet_thickness * 0.055
torque += coil_diameter * 0.012
torque += turns * 0.004
torque += rotor_radius * 0.004
torque += pole_arc * 0.0015
torque += rotor_poles * 0.012
torque -= air_gap * 0.45
torque -= slot_opening * 0.018
torque -= abs(rotor_poles - 14) * 0.01
torque -= abs(stator_teeth - 12) * 0.008
torque = max(0.05, torque)

efficiency = (
    82
    - air_gap * 9
    + magnet_thickness * 1.8
    + magnet_diameter * 0.3
    - fixed_current * 0.9
    - slot_opening * 1.1
    + cooling * 0.9
    + pole_arc * 0.025
    - abs(rotor_poles - 14) * 0.4
)
efficiency = max(25, min(97, efficiency))

heat_risk = (
    fixed_current * 7
    + turns * 0.08
    + magnet_thickness * 1.5
    + battery_voltage * 0.012
    - cooling * 6
    + slot_opening * 0.8
)
heat_risk = max(5, min(100, heat_risk))

battery_drain = (
    fixed_current * 5.5
    + heat_risk * 0.25
    + battery_voltage * 0.008
    - efficiency * 0.22
)
battery_drain = max(5, min(100, battery_drain))

acceleration_time = (
    12
    - torque * 5.8
    + vehicle_mass * 0.002
    + air_gap * 1.7
    - rotor_poles * 0.035
)
acceleration_time = max(2.1, min(18, acceleration_time))

top_speed = (
    70
    + torque * 75
    + battery_voltage * 0.09
    + fixed_current * 1.8
    - rotor_poles * 1.1
    - vehicle_mass * 0.015
)
top_speed = max(45, min(340, top_speed))

ev_range = (
    efficiency * 5.5
    - fixed_current * 8
    - heat_risk * 0.5
    + cooling * 6
    - vehicle_mass * 0.035
)
ev_range = max(40, min(700, ev_range))

# -----------------------------
# Baseline comparison
# -----------------------------
baseline_torque = 0.75
baseline_accel = 8.5
baseline_speed = 160
baseline_range = 320
baseline_eff = 78
baseline_heat = 55

torque_gain = ((torque - baseline_torque) / baseline_torque) * 100
accel_gain = ((baseline_accel - acceleration_time) / baseline_accel) * 100
speed_gain = ((top_speed - baseline_speed) / baseline_speed) * 100
range_gain = ((ev_range - baseline_range) / baseline_range) * 100
eff_gain = ((efficiency - baseline_eff) / baseline_eff) * 100
heat_change = ((heat_risk - baseline_heat) / baseline_heat) * 100

# -----------------------------
# Main metrics
# -----------------------------
st.subheader("Main Results")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Torque", f"{torque:.2f} Nm", f"{torque_gain:+.0f}% vs baseline")
    st.metric("Efficiency", f"{efficiency:.0f}%", f"{eff_gain:+.0f}%")

with c2:
    st.metric("0–100 km/h", f"{acceleration_time:.1f} sec", f"{accel_gain:+.0f}% faster")
    st.metric("Top Speed", f"{top_speed:.0f} km/h", f"{speed_gain:+.0f}%")

with c3:
    st.metric("EV Range", f"{ev_range:.0f} km", f"{range_gain:+.0f}%")
    st.metric("Battery Drain", f"{battery_drain:.0f}%")

with c4:
    st.metric("Heat Risk", f"{heat_risk:.0f}%", f"{heat_change:+.0f}%")
    st.metric("Current", f"{fixed_current} A", "fixed input")

st.divider()

# -----------------------------
# Progress visualization
# -----------------------------
left, right = st.columns(2)

with left:
    st.subheader("Motor Physics")
    st.write("Torque")
    st.progress(int(max(0, min(100, torque * 55))))

    st.write("Efficiency")
    st.progress(int(efficiency))

    st.write("Thermal Safety")
    st.progress(int(max(0, min(100, 100 - heat_risk))))

    st.write("Magnetic Coupling")
    magnetic_coupling = max(0, min(100, 100 - air_gap * 55 + magnet_thickness * 5))
    st.progress(int(magnetic_coupling))

with right:
    st.subheader("Electric Car Behavior")
    st.write("Acceleration")
    st.progress(int(max(0, min(100, 100 - acceleration_time * 5))))

    st.write("Top Speed")
    st.progress(int(max(0, min(100, top_speed / 340 * 100))))

    st.write("Range")
    st.progress(int(max(0, min(100, ev_range / 700 * 100))))

    st.write("Battery Health")
    st.progress(int(max(0, min(100, 100 - battery_drain))))

st.divider()

# -----------------------------
# Outcome type generator
# -----------------------------
st.subheader("Outcome Type")

outcomes = []

if accel_gain > 45 and heat_risk < 70:
    outcomes.append(("🏎️ Drag Race EV", "Extremely fast launch. Best for short acceleration performance."))

if torque_gain > 60:
    outcomes.append(("💪 Torque Monster", "Very high torque. Strong for launch, hill climbing, or heavy-load movement."))

if range_gain > 25 and efficiency > 85:
    outcomes.append(("🔋 Long-Range EV", "Best for distance. Prioritizes efficiency and battery range."))

if efficiency > 88 and heat_risk < 55:
    outcomes.append(("🌱 Eco Efficiency Setup", "Very efficient and thermally safe. Good for daily energy savings."))

if top_speed > 240:
    outcomes.append(("🛣️ Highway Cruiser", "High top speed potential. Better for highway performance."))

if heat_risk > 85:
    outcomes.append(("🚨 Thermal Danger Setup", "Motor may overheat. Reduce current or improve cooling."))

if battery_drain > 78:
    outcomes.append(("🪫 Battery-Draining Setup", "Strong power demand but poor range sustainability."))

if cooling >= 8 and heat_risk < 65 and fixed_current > 10:
    outcomes.append(("❄️ Cooling-Optimized Power Setup", "High power is supported by strong cooling."))

if air_gap <= 0.35:
    outcomes.append(("🧲 Tight Air-Gap Performance Setup", "Strong magnetic coupling, but harder manufacturing tolerance."))

if air_gap >= 1.0:
    outcomes.append(("🐢 Weak Magnetic Coupling", "Large air gap reduces useful magnetic force and torque."))

if rotor_poles >= 18:
    outcomes.append(("🌀 Smooth Torque Setup", "More rotor poles can improve smoother low-speed torque."))

if rotor_poles <= 10:
    outcomes.append(("⚡ High-RPM Leaning Setup", "Lower pole count may favor higher speed but less smooth torque."))

if rotor_radius >= 80:
    outcomes.append(("🚚 Heavy-Duty Motor", "Large rotor radius supports torque for heavier loads."))

if rotor_radius <= 35:
    outcomes.append(("🪶 Lightweight Motor", "Smaller rotor is lighter but sacrifices torque."))

if magnet_thickness >= 6 or magnet_diameter >= 16:
    outcomes.append(("🧲 Overbuilt Magnet Setup", "Strong magnets increase torque but may increase cost and weight."))

if magnet_thickness <= 2:
    outcomes.append(("💸 Low-Cost Magnet Setup", "Cheaper magnet design, but lower torque potential."))

if slot_opening >= 8:
    outcomes.append(("⚠️ Magnetic Leakage Setup", "Large slot opening may make winding easier but reduces efficiency."))

if pole_arc >= 150:
    outcomes.append(("📈 Wide Pole Arc Setup", "Better field coverage and torque, but possible saturation risk."))

if vehicle_mass > 2000 and torque > 1.2:
    outcomes.append(("🚙 SUV / Heavy EV Setup", "Suitable for heavier electric vehicles."))

if vehicle_mass < 1100 and accel_gain > 30:
    outcomes.append(("🏁 Lightweight Sport EV", "Light vehicle plus strong torque gives very fast acceleration."))

if fixed_current <= 4 and heat_risk < 35:
    outcomes.append(("🧊 Cool Safe Setup", "Low current keeps the motor safe, but performance may be limited."))

if fixed_current >= 15 and heat_risk > 70:
    outcomes.append(("🔥 Experimental High-Current Setup", "Powerful but risky. Needs cooling and FEMM validation."))

if not outcomes:
    outcomes.append(("🚙 Balanced Daily EV", "Balanced torque, range, heat, and acceleration."))

for title, explanation in outcomes[:5]:
    st.info(f"{title}: {explanation}")

st.divider()

# -----------------------------
# Optimization explanation
# -----------------------------
st.subheader("Optimization Goal")

st.write(
    f"Goal: maximize torque at a fixed current of **{fixed_current} A** by changing "
    "air gap, magnet size, coil size, winding turns, rotor/stator geometry, and pole structure."
)

if torque_gain > 40:
    st.success(f"Torque improved by {torque_gain:.0f}% compared to the baseline LRK setup.")
elif torque_gain > 10:
    st.info(f"Torque improved by {torque_gain:.0f}%. This is a moderate optimization.")
else:
    st.warning(f"Torque change is only {torque_gain:.0f}%. Try reducing air gap, increasing magnet size, or increasing rotor radius.")

st.divider()

# -----------------------------
# Engineering recommendations
# -----------------------------
st.subheader("AI Engineering Recommendations")

recommendations = []

if air_gap > 0.7:
    recommendations.append("Reduce air gap to improve magnetic coupling and torque.")

if magnet_thickness < 3:
    recommendations.append("Increase magnet thickness to strengthen the magnetic field.")

if magnet_diameter < 8:
    recommendations.append("Increase magnet diameter for stronger rotor magnetic field.")

if coil_diameter < 8:
    recommendations.append("Increase coil diameter to improve electromagnetic interaction area.")

if turns < 40:
    recommendations.append("Increase coil turns for higher torque at the same current.")

if heat_risk > 75:
    recommendations.append("Reduce current or increase cooling because heat risk is high.")

if battery_drain > 75:
    recommendations.append("Improve efficiency or reduce current to protect EV range.")

if slot_opening > 7:
    recommendations.append("Reduce slot opening to lower magnetic leakage.")

if rotor_radius < 45:
    recommendations.append("Increase rotor radius if the goal is higher torque.")

if not recommendations:
    recommendations.append("This setup is already reasonable. Fine-tune air gap and magnet size for more torque.")

for rec in recommendations:
    st.write("✅ " + rec)

st.divider()

# -----------------------------
# Variable explanation
# -----------------------------
st.subheader("What Changed Physically?")

st.write(f"- Air gap = **{air_gap:.2f} mm**. Smaller gap usually increases magnetic coupling.")
st.write(f"- Magnet size = **{magnet_diameter} mm diameter**, **{magnet_thickness:.1f} mm thickness**.")
st.write(f"- Coil size = **{coil_diameter} mm**, with **{turns} turns**.")
st.write(f"- LRK structure = **{stator_teeth} stator teeth** and **{rotor_poles} rotor poles**.")
st.write(f"- Rotor radius = **{rotor_radius} mm**.")

st.divider()

st.subheader("ML Dataset Used for Torque Prediction")
st.dataframe(data)
