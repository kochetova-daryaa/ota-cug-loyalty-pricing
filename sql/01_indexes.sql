CREATE INDEX IF NOT EXISTS idx_sessions_fence ON fact_sessions(fence_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON fact_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_sessions_hotel ON fact_sessions(hotel_id);
