# Aero-Telemetry-Analyzer

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Engineering-green.svg)
![NumPy](https://img.shields.io/badge/NumPy-State_Machine-blue.svg)

A lightweight ETL pipeline for processing asynchronous aerospace telemetry logs (e.g., model rockets, CanSats). The script merges multi-sensor data, filters hardware noise, computes kinematics, and classifies flight phases using a state machine.

## Pipeline Architecture

1. **Data Integration:** Merges asynchronous sensor logs (barometer and temperature) on a common time-axis (`Time_s`) via outer join to handle sensor dropouts.
2. **Noise Filtering:** Drops negative altitude spikes and calibration errors to keep the dataset clean.
3. **Feature Engineering:** Calculates vertical velocity (`Velocity_m_s`) using altitude deltas (`.diff()`).
4. **State Machine:** Classifies flight phases (`Flight_Phase`) based on velocity and altitude thresholds:
   * `Idle/Apogee`
   * `Ascent`
   * `Descent_High_Alt` (> 400m)
   * `Descent_Low_Alt` (<= 400m)
5. **Mission Reporting:** Aggregates telemetry per flight phase and flattens the multi-index output for direct database or API injection.

## Sample Mission Report

| Flight_Phase | Velocity_m_s_min | Velocity_m_s_mean | Velocity_m_s_max | Temperature_C_min | Temperature_C_mean | Altitude_m_max |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Descent_High_Alt | -150.0 | -100.0 | -50.0 | 5.0 | 7.5 | 650 |
| Descent_Low_Alt | -200.0 | -150.0 | -100.0 | 12.0 | 15.0 | 300 |
| Ascent | 12.0 | 134.0 | 250.0 | 10.0 | 17.5 | 650 |
| Idle/Apogee | 0.0 | 0.0 | 0.0 | 25.0 | 25.0 | 10 |

## Usage

```bash
pip install pandas numpy
python telemetry_pipeline.py