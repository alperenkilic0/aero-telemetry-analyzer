import pandas as pd
import numpy as np

# simulated telemetry logs (barometer & temp)
data_barometer = {
    'Time_s': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    'Altitude_m': [-2, 10, 150, 400, 650, 600, 450, 300, 100, 0] # -2 is calibration noise
}

data_temperature = {
    'Time_s': [0, 1, 2, 3, 4, 6, 7, 8, 9], # missing t=5 (sensor dropout)
    'Temperature_C': [25, 24, 21, 15, 10, 5, 8, 12, 18]
}

df_baro = pd.DataFrame(data_barometer)
df_temp = pd.DataFrame(data_temperature)

# outer merge to handle asynchronous sensor rates
df_flight = pd.merge(df_baro, df_temp, how='outer', on='Time_s')

# derive vertical velocity (rate of climb/descent)
df_flight['Velocity_m_s'] = df_flight['Altitude_m'].diff()

# drop negative altitude spikes (hardware noise)
noisy_rows = df_flight[df_flight['Altitude_m'] < 0].index
df_flight = df_flight.drop(noisy_rows)

# flight phase state machine based on kinematics
conditions = [
    (df_flight['Velocity_m_s'] == 0),
    (df_flight['Velocity_m_s'] > 0),
    (df_flight['Velocity_m_s'] < 0) & (df_flight['Altitude_m'] <= 400),
    (df_flight['Velocity_m_s'] < 0) & (df_flight['Altitude_m'] > 400)
]

phases = [
    'Idle/Apogee',
    'Ascent',
    'Descent_Low_Alt',
    'Descent_High_Alt'
]

df_flight['Flight_Phase'] = np.select(conditions, phases, default='Unknown')

# aggregate mission stats per flight phase
mission_report = df_flight.groupby('Flight_Phase', as_index=False).agg({
    'Velocity_m_s': ['min', 'mean', 'max'],
    'Temperature_C': ['min', 'mean', 'max'],
    'Altitude_m': ['max']
})

# flatten multi-index for db/api export compatibility
mission_report.columns = ['_'.join(col).strip('_') for col in mission_report.columns.values]

print(df_flight)
print(mission_report)