import duckdb
import pathlib

data_path = pathlib.Path(__file__).parents[1] / "data"

query = f"""
    SELECT
        t."건물번호" AS building_id,
        b."건물유형" AS building_type,
        STRPTIME(t."일시", '%Y%m%d %H') AS datetime_,
        t."기온(°C)" AS temperature_celsius,
        t."강수량(mm)" AS rainfall_mm,
        t."풍속(m/s)" AS windspeed_mps,
        t."습도(%)" AS humidity_percent,
        IFNULL(t."일조(hr)", 0) AS sunshine_hour,
        IFNULL(t."일사(MJ/m2)" * 1_000_000 / 3600, 0) AS solar_radiation_wpm2,
        t."전력소비량(kWh)" AS power_consumption_kwh,
        b."연면적(m2)" AS total_area_m2,
        b."냉방면적(m2)" AS cooling_area_m2,
        CASE WHEN b."태양광용량(kW)" = '-' 
            THEN NULL ELSE b."태양광용량(kW)"::DOUBLE
            END AS solar_panel_capacity_kw,
        CASE WHEN b."ESS저장용량(kWh)" = '-' 
            THEN NULL ELSE b."ESS저장용량(kWh)"::DOUBLE
            END AS ess_storage_capacity_kwh,
        CASE WHEN b."PCS용량(kW)" = '-' 
            THEN NULL ELSE b."PCS용량(kW)"::DOUBLE
            END AS pcs_capacity_kw
    FROM 
        '{str(data_path / "train.csv")}' AS t
        LEFT JOIN '{str(data_path / "building_info.csv")}' AS b
        ON t."건물번호" = b."건물번호"
"""

duckdb.query(query).to_parquet(str(data_path / "whole_data.parquet"))