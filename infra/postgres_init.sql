-- PostgreSQL Initialization Script for PlantGuard
-- Creates the 5 logical schemas under the single PostgreSQL database

CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS agronomy;
CREATE SCHEMA IF NOT EXISTS env;
CREATE SCHEMA IF NOT EXISTS market;
CREATE SCHEMA IF NOT EXISTS logs;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

COMMENT ON SCHEMA core IS 'Users, Farmer Profiles, Farms, Perennial Crop Blocks, IoT Device Registrations';
COMMENT ON SCHEMA agronomy IS 'Farm Activity History (fertilizer/spraying/harvesting) and Disease Detections';
COMMENT ON SCHEMA env IS 'Microclimate Weather Readings and Soil Sensor Telemetry';
COMMENT ON SCHEMA market IS 'Mandi Market Prices and Commodity Data';
COMMENT ON SCHEMA logs IS 'Advisory Logs, RL Feedback, Notifications, System Audit Logs';
