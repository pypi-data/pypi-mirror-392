-- Ontologia Playground Database Initialization
-- This script sets up the initial database schema and extensions

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Create indexes for better performance
-- These will be created by Alembic migrations, but we add some basic ones here

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_objects_search ON objects USING gin(to_tsvector('english', properties::text));
CREATE INDEX IF NOT EXISTS idx_links_search ON links USING gin(to_tsvector('english', properties::text));

-- JSON property indexes
CREATE INDEX IF NOT EXISTS idx_objects_properties ON objects USING gin(properties);
CREATE INDEX IF NOT EXISTS idx_links_properties ON links USING gin(properties);

-- Created/Updated indexes
CREATE INDEX IF NOT EXISTS idx_objects_created_at ON objects(created_at);
CREATE INDEX IF NOT EXISTS idx_links_created_at ON links(created_at);

-- Object type indexes
CREATE INDEX IF NOT EXISTS idx_objects_type ON objects(object_type_id);
CREATE INDEX IF NOT EXISTS idx_links_type ON links(link_type_id);

-- Setup temporal visibility database (if needed)
-- This will be handled by Temporal auto-setup

-- Setup Dagster database (if needed)
-- This will be handled by Dagster setup

-- Create sample schema for demonstration
CREATE SCHEMA IF NOT EXISTS demo;

-- Create sample tables for analytics
CREATE TABLE IF NOT EXISTS demo.analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    properties JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id VARCHAR(100),
    session_id VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON demo.analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON demo.analytics_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_analytics_events_user ON demo.analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_properties ON demo.analytics_events USING gin(properties);

-- Create sample table for metrics
CREATE TABLE IF NOT EXISTS demo.metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    labels JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_name ON demo.metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON demo.metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_labels ON demo.metrics USING gin(labels);

-- Insert some sample data
INSERT INTO demo.analytics_events (event_type, properties, user_id, session_id) VALUES
('page_view', '{"page": "dashboard", "referrer": "direct"}', 'user1', 'session1'),
('button_click', '{"button": "submit", "form": "contact"}', 'user1', 'session1'),
('page_view', '{"page": "about", "referrer": "dashboard"}', 'user2', 'session2'),
('search', '{"query": "ontologia", "results": 10}', 'user2', 'session2'),
('page_view', '{"page": "docs", "referrer": "search"}', 'user3', 'session3')
ON CONFLICT DO NOTHING;

INSERT INTO demo.metrics (metric_name, metric_value, labels) VALUES
('api_requests_total', 1250.0, '{"endpoint": "/api/v1/objects", "method": "GET"}'),
('api_response_time_ms', 45.5, '{"endpoint": "/api/v1/objects", "method": "GET"}'),
('active_users', 42.0, '{"timeframe": "1h"}'),
('database_connections', 8.0, '{"pool": "default"}')
ON CONFLICT DO NOTHING;

-- Create view for analytics summary
CREATE OR REPLACE VIEW demo.analytics_summary AS
SELECT
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as unique_sessions,
    MIN(timestamp) as first_event,
    MAX(timestamp) as last_event
FROM demo.analytics_events
GROUP BY event_type
ORDER BY event_count DESC;

-- Create view for metrics summary
CREATE OR REPLACE VIEW demo.metrics_summary AS
SELECT
    metric_name,
    AVG(metric_value) as avg_value,
    MIN(metric_value) as min_value,
    MAX(metric_value) as max_value,
    COUNT(*) as measurement_count,
    MIN(timestamp) as first_measurement,
    MAX(timestamp) as last_measurement
FROM demo.metrics
GROUP BY metric_name
ORDER BY avg_value DESC;

-- Grant permissions to the ontologia user
GRANT USAGE ON SCHEMA demo TO ontologia;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA demo TO ontologia;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA demo TO ontologia;

-- Set default permissions for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA demo GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ontologia;
ALTER DEFAULT PRIVILEGES IN SCHEMA demo GRANT USAGE, SELECT ON SEQUENCES TO ontologia;

-- Create function for full-text search
CREATE OR REPLACE FUNCTION demo.search_objects(search_query TEXT)
RETURNS TABLE(
    id UUID,
    object_type_id VARCHAR(100),
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    search_rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.id,
        o.object_type_id,
        o.properties,
        o.created_at,
        o.updated_at,
        ts_rank(to_tsvector('english', o.properties::text), plainto_tsquery('english', search_query)) as search_rank
    FROM objects o
    WHERE to_tsvector('english', o.properties::text) @@ plainto_tsquery('english', search_query)
    ORDER BY search_rank DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function for analytics aggregation
CREATE OR REPLACE FUNCTION demo.get_hourly_metrics(metric_name_param TEXT, hours_back INTEGER DEFAULT 24)
RETURNS TABLE(
    hour_bucket TIMESTAMP WITH TIME ZONE,
    avg_value DECIMAL(15,4),
    min_value DECIMAL(15,4),
    max_value DECIMAL(15,4),
    count_values INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        date_trunc('hour', timestamp) as hour_bucket,
        AVG(metric_value) as avg_value,
        MIN(metric_value) as min_value,
        MAX(metric_value) as max_value,
        COUNT(*) as count_values
    FROM demo.metrics
    WHERE metric_name = metric_name_param
    AND timestamp >= NOW() - (hours_back || ' hours')::INTERVAL
    GROUP BY date_trunc('hour', timestamp)
    ORDER BY hour_bucket DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function for event analytics
CREATE OR REPLACE FUNCTION demo.get_event_analytics(event_type_param TEXT, days_back INTEGER DEFAULT 7)
RETURNS TABLE(
    date_bucket DATE,
    event_count INTEGER,
    unique_users INTEGER,
    unique_sessions INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        DATE(timestamp) as date_bucket,
        COUNT(*) as event_count,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(DISTINCT session_id) as unique_sessions
    FROM demo.analytics_events
    WHERE event_type = event_type_param
    AND timestamp >= NOW() - (days_back || ' days')::INTERVAL
    GROUP BY DATE(timestamp)
    ORDER BY date_bucket DESC;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updating timestamps
CREATE OR REPLACE FUNCTION demo.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for analytics events
CREATE TRIGGER update_analytics_events_updated_at
    BEFORE UPDATE ON demo.analytics_events
    FOR EACH ROW
    EXECUTE FUNCTION demo.update_updated_at_column();

-- Create trigger for metrics
CREATE TRIGGER update_metrics_updated_at
    BEFORE UPDATE ON demo.metrics
    FOR EACH ROW
    EXECUTE FUNCTION demo.update_updated_at_column();

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE 'Ontologia Playground database initialized successfully';
    RAISE NOTICE 'Demo schema created with sample data';
    RAISE NOTICE 'Analytics functions and views created';
END $$;
