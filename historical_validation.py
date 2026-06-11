import pandas as pd


def load_historical_validation_sample(
    path: str = "historical_validation_sample.csv",
) -> pd.DataFrame:
    return pd.read_csv(path)


def summarize_validation(df: pd.DataFrame) -> dict:
    carbon_only = df[df["carbon_only_choice"] == "yes"].iloc[0]
    guardian = df[df["gridcarbon_choice"] == "yes"].iloc[0]

    return {
        "carbon_only_hour": carbon_only["hour"],
        "carbon_only_carbon": int(carbon_only["carbon_intensity"]),
        "carbon_only_grid": int(carbon_only["grid_load"]),
        "guardian_hour": guardian["hour"],
        "guardian_carbon": int(guardian["carbon_intensity"]),
        "guardian_grid": int(guardian["grid_load"]),
        "grid_load_reduction": int(carbon_only["grid_load"] - guardian["grid_load"]),
        "carbon_tradeoff": int(guardian["carbon_intensity"] - carbon_only["carbon_intensity"]),
    }