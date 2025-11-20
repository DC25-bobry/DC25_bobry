import { useState, useEffect, useCallback } from 'react';

const API_BASE = 'http://localhost:8000';

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`GET ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

async function apiSend(path, method, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text().catch(() => '');
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    throw new Error(
      data?.detail || `Request ${method} ${path} failed: ${res.status}`
    );
  }
  return data;
}

export default function useJobOffers() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet('/jobs');
      setJobs(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error('Failed to load jobs:', e);
      setError(e.message || 'Nie udało się pobrać ofert pracy.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  const addJob = async (job) => {
    setError(null);
    try {
      const created = await apiSend('/jobs', 'POST', job);
      setJobs((prev) => [...prev, created]);
    } catch (e) {
      console.error('Failed to add job:', e);
      setError(e.message || 'Nie udało się dodać oferty.');
      throw e;
    }
  };

  const updateJob = async (id, job) => {
    setError(null);
    try {
      const updated = await apiSend(`/jobs/${encodeURIComponent(id)}`, 'PUT', job);
      setJobs((prev) => prev.map((j) => (j.id === id ? updated : j)));
    } catch (e) {
      console.error('Failed to update job:', e);
      setError(e.message || 'Nie udało się zaktualizować oferty.');
      throw e;
    }
  };

  const removeJob = async (id) => {
    setError(null);
    try {
      await apiSend(`/jobs/${encodeURIComponent(id)}`, 'DELETE');
      setJobs((prev) => prev.filter((j) => j.id !== id));
    } catch (e) {
      console.error('Failed to remove job:', e);
      setError(e.message || 'Nie udało się usunąć oferty.');
      throw e;
    }
  };

  return {
    jobs,
    loading,
    error,
    reload: loadJobs,
    addJob,
    updateJob,
    removeJob,
  };
}
