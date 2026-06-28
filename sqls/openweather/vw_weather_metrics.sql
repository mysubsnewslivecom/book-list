CREATE OR REPLACE VIEW openweather.weather_metrics AS
SELECT
    dt,
    to_timestamp(dt) AS observed_at,

    city_id,
    city_name,
    country,

    (payload->'main'->>'temp')::double precision temp,
    (payload->'main'->>'feels_like')::double precision feels_like,
    (payload->'main'->>'temp_min')::double precision temp_min,
    (payload->'main'->>'temp_max')::double precision temp_max,

    (payload->'main'->>'humidity')::integer humidity,
    (payload->'main'->>'pressure')::integer pressure,
    (payload->'main'->>'sea_level')::integer sea_level,
    (payload->'main'->>'grnd_level')::integer grnd_level,

    (payload->'wind'->>'speed')::double precision wind_speed,
    (payload->'wind'->>'gust')::double precision wind_gust,
    (payload->'wind'->>'deg')::integer wind_deg,

    (payload->'clouds'->>'all')::integer clouds,
    (payload->>'visibility')::integer visibility,

    payload->'weather'->0->>'main' weather,
    payload->'weather'->0->>'description' description
FROM openweather.current_weather_json;
