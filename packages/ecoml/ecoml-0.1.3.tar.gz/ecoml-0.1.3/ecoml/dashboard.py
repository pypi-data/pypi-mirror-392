"""
Simple dashboard helpers.

You can use these inside a notebook to quickly inspect the CSV log.
For PowerBI you will mostly just load data/data/emissions_log.csv directly.
"""

from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


def load_log(log_path: str) -> pd.DataFrame:
    df = pd.read_csv(log_path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def show_summary(df: pd.DataFrame) -> None:
    total_runs = len(df)
    total_runtime = df["runtime_sec"].sum()
    total_co2 = df["co2_g"].sum()
    avg_co2 = df["co2_g"].mean()

    print("==== EcoML Summary ====")
    print(f"Runs: {total_runs}")
    print(f"Total runtime: {total_runtime:.2f} sec")
    print(f"Total CO₂: {total_co2:.3f} g")
    print(f"Average CO₂ per cell: {avg_co2:.4f} g")


def plot_emissions_over_time(df: pd.DataFrame) -> None:
    if "timestamp" not in df.columns:
        print("No timestamp column – cannot plot over time.")
        return

    df_sorted = df.sort_values("timestamp")
    plt.figure()
    plt.plot(df_sorted["timestamp"], df_sorted["co2_g"])
    plt.xlabel("Time")
    plt.ylabel("CO₂ per cell (g)")
    plt.title("EcoML: CO₂ Emissions Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_runtime_vs_emissions(df: pd.DataFrame) -> None:
    plt.figure()
    plt.scatter(df["runtime_sec"], df["co2_g"])
    plt.xlabel("Runtime (sec)")
    plt.ylabel("CO₂ (g)")
    plt.title("EcoML: Runtime vs CO₂")
    plt.tight_layout()
    plt.show()
