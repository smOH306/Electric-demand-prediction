import duckdb
import pathlib

data_path = pathlib.Path(__file__).parents[1] / "data"

translation_dict = {
    '건물기타': 0,
    '공공': 1,
    '학교': 2,
    '백화점': 3,
    '병원': 4,
    '상용': 5,
    '아파트': 6,
    '연구소': 7,
    'IDC(전화국)': 8,
    '호텔': 9
}

query = f"""
    WITH temporal_ AS (
        SELECT
            *,
            COS(HOUR(datetime_) * (2 * PI() / 24)) AS cos_hour,
            SIN(HOUR(datetime_) * (2 * PI() / 24)) AS sin_hour,
            COS(MONTH(datetime_) * (2 * PI() / 12)) AS cos_month,
            SIN(MONTH(datetime_) * (2 * PI() / 12)) AS sin_month,
            COS(WEEK(datetime_) * (2 * PI() / 52)) AS cos_week,
            SIN(WEEK(datetime_) * (2 * PI() / 52)) AS sin_week,
        FROM '{str(data_path / "whole_data.parquet")}'
    )
    SELECT
        *,
        total_area_m2 / cooling_area_m2 AS cooling_area_ratio,
        power_consumption_kwh 
            / total_area_m2
            AS power_density_kwhpm2,
    FROM temporal_
"""

data_frame = duckdb.query(query).to_df()
data_frame["building_type"] = data_frame["building_type"].map(translation_dict)
data_frame.to_parquet(data_path / "preprocessed_data.parquet")