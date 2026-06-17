-- Spatial business insight examples for the MPHA workshop.
--
-- The single raw GeoJSON file is loaded and conformed in AIDP:
--   data/raw_spatial/healthcare_service_areas.geojson
--
-- AIDP stages the Gold output as gold_spatial_access_insights, then
-- create_ai_lakehouse_gold_layer.sql loads it into AI Lakehouse.

-- 1. Districts where geography and public-health pressure suggest mobile clinics.
SELECT
  district_name,
  population,
  facility_count,
  residents_per_facility,
  public_health_pressure_index,
  spatial_business_insight
FROM mpha_gold_spatial_access_insights
WHERE residents_per_facility >= 100000
   OR public_health_pressure_index >= 45
ORDER BY public_health_pressure_index DESC, residents_per_facility DESC;

-- 2. OAC map tooltip dataset.
SELECT
  district_name,
  'Residents per facility: ' || TO_CHAR(residents_per_facility) ||
  '; pressure index: ' || TO_CHAR(public_health_pressure_index) ||
  '; action: ' || spatial_business_insight AS map_tooltip
FROM mpha_gold_spatial_access_insights
ORDER BY residents_per_facility DESC;

-- 3. Spatial planning signal joined to executive operations.
SELECT
  s.district_name,
  s.residents_per_facility,
  s.avg_distance_to_facility_km,
  s.public_health_pressure_index,
  e.avg_ed_wait_minutes,
  e.high_occupancy_days,
  s.spatial_business_insight
FROM mpha_gold_spatial_access_insights s
JOIN mpha_gold_executive_overview e
  ON s.district_id = e.district_id
ORDER BY s.residents_per_facility DESC;
