import { useState, useEffect, useCallback } from 'react';
import { getHistoricalList, getHistoricalEvent } from '../services/api.js';

export function useHistoricalList() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  useEffect(() => {
    getHistoricalList()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}

export function useHistoricalEvent(id) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const replay = useCallback(async (eventId) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await getHistoricalEvent(eventId);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, replay };
}
