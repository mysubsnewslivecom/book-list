CREATE MATERIALIZED VIEW openweather.mv_today_forecast
AS
SELECT
    c.id AS city_id,
    c.name AS city_name,
    c.country,
    c.lat,
    c.lon,

    f.id AS forecast_id,
    f.dt,
    f.dt_txt,
    f.visibility,
    f.pop,

    fm.temp,
    fm.feels_like,
    fm.temp_min,
    fm.temp_max,
    fm.pressure,
    fm.sea_level,
    fm.grnd_level,
    fm.humidity,
    fm.temp_kf,
    fm.dew_point,

    fc."all" AS cloud_cover,

    fw.speed AS wind_speed,
    fw.deg AS wind_direction,
    fw.gust AS wind_gust,

    fr.volume_3h AS rain_volume_3h,

    fs.pod,

    wc.weather_id,
    wc.main AS weather_main,
    wc.description AS weather_description,
    wc.icon,

    ca.sunrise,
    ca.sunset
        ROW_NUMBER() OVER (
            PARTITION BY c.id
            ORDER BY f.dt_txt
        ) AS rn
FROM openweather.forecasts f
JOIN openweather.cities c
    ON c.id = f.city_id

LEFT JOIN openweather.forecast_main fm
    ON fm.forecast_id = f.id

LEFT JOIN openweather.forecast_clouds fc
    ON fc.forecast_id = f.id

LEFT JOIN openweather.forecast_wind fw
    ON fw.forecast_id = f.id

LEFT JOIN openweather.forecast_rain fr
    ON fr.forecast_id = f.id

LEFT JOIN openweather.forecast_sys fs
    ON fs.forecast_id = f.id

LEFT JOIN openweather.weather_conditions wc
    ON wc.forecast_id = f.id

LEFT JOIN openweather.city_astronomy ca
    ON ca.city_id = c.id
   AND ca.date = DATE(f.dt_txt)

WHERE DATE(f.dt_txt) = CURRENT_DATE
WITH DATA;

CREATE UNIQUE INDEX ix_mv_today_forecast
ON openweather.mv_today_forecast (
    city_id,
    forecast_id,
    weather_id
);

-- REFRESH MATERIALIZED VIEW openweather.mv_today_forecast;