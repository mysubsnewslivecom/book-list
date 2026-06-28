CREATE MATERIALIZED VIEW openweather.mv_current_forecast
AS
SELECT *
FROM (
    SELECT
        c.name AS city_name,
		c.id as city_id,
        f.dt_txt,
        fm.temp,
        fm.feels_like,
        wc.main AS weather_main,
        wc.description,
        ROW_NUMBER() OVER (
            PARTITION BY c.id
            ORDER BY f.dt_txt
        ) AS rn
    FROM openweather.forecasts f
    JOIN openweather.cities c
        ON c.id = f.city_id
    LEFT JOIN openweather.forecast_main fm
        ON fm.forecast_id = f.id
    LEFT JOIN openweather.weather_conditions wc
        ON wc.forecast_id = f.id
    WHERE f.dt_txt >= NOW()
) x
WHERE rn = 1
WITH DATA;

CREATE UNIQUE INDEX ux_mv_current_forecast_city_id
ON openweather.mv_current_forecast (city_id);