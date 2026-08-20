/**
 * useLatestPrediction.js
 * Polls getLatest() on a configurable interval.
 * Components see: { data, loading, error, refetch }
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { getLatest, POLLING_INTERVAL_MS } from '../services/api.js';

export function useLatestPrediction() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const intervalRef = useRef(null);

  const fetch = useCallback(async () => {
    setError(null);
    try {
      const result = await getLatest();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
    intervalRef.current = setInterval(fetch, POLLING_INTERVAL_MS);
    return () => clearInterval(intervalRef.current);
  }, [fetch]);

  const refetch = useCallback(() => {
    setLoading(true);
    fetch();
  }, [fetch]);

  return { data, loading, error, refetch };
}
