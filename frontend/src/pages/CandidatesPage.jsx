import React, { useEffect, useMemo, useState } from 'react';
import {
  FileText,
  Users,
  CheckCircle,
  XCircle,
  AlertCircle,
  Mail,
  Phone,
  Link as LinkIcon,
  Briefcase,
  Filter,
  RefreshCw,
  Trash2,
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState([]);
  const [summary, setSummary] = useState({ total: 0, returned: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [filterJobId, setFilterJobId] = useState('');
  const [onlyMatched, setOnlyMatched] = useState(false);
  const [onlyRejected, setOnlyRejected] = useState(false);

  const [deletingIds, setDeletingIds] = useState(new Set());

  const fetchCandidates = async () => {
    setLoading(true);
    setError(null);

    const params = new URLSearchParams();
    if (filterJobId) params.set('job_id', filterJobId);
    if (onlyMatched) params.set('only_matched', 'true');
    if (onlyRejected) params.set('only_rejected', 'true');

    const url = `${API_BASE}/candidates${params.toString() ? `?${params.toString()}` : ''}`;

    try {
      const res = await fetch(url);
      const text = await res.text();
      let data = null;

      try {
        data = text ? JSON.parse(text) : null;
      } catch (e) {
        console.error('❌ Nie udało się sparsować JSON z /candidates:', e, text);
        throw new Error('Backend (GET /candidates) zwrócił nieprawidłowy JSON');
      }

      if (!res.ok) {
        throw new Error(data?.detail || `GET /candidates zwrócił błąd ${res.status}`);
      }

      const list = data?.candidates || [];
      setCandidates(list);
      setSummary({
        total: data?.total_candidates ?? list.length,
        returned: data?.returned_candidates ?? list.length,
      });
    } catch (err) {
      console.error(err);
      setError(
        err.message ||
          'Wystąpił błąd podczas pobierania kandydatów. Sprawdź backend na /candidates.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterJobId, onlyMatched, onlyRejected]);

  const handleDeleteCandidate = async (candidateId) => {
    const confirm = window.confirm(
      'Na pewno chcesz usunąć tego kandydata z candidates.json?\nPlik CV na Google Drive NIE zostanie usunięty.'
    );
    if (!confirm) return;

    setError(null);
    setDeletingIds((prev) => {
      const next = new Set(prev);
      next.add(candidateId);
      return next;
    });

    try {
      const res = await fetch(
        `${API_BASE}/candidates/${encodeURIComponent(candidateId)}`,
        {
          method: 'DELETE',
        }
      );

      const text = await res.text();
      let data = null;
      try {
        data = text ? JSON.parse(text) : null;
      } catch (e) {
        console.error('❌ Nie udało się sparsować JSON z DELETE /candidates:', e, text);
        throw new Error('Backend (DELETE /candidates) zwrócił nieprawidłowy JSON');
      }

      if (!res.ok) {
        throw new Error(
          data?.detail || `Usuwanie kandydata nie powiodło się (${res.status})`
        );
      }

      // lokalnie usuwamy
      setCandidates((prev) => prev.filter((c) => c.id !== candidateId));
      setSummary((prev) => ({
        ...prev,
        total: Math.max(0, (prev.total ?? 0) - 1),
        returned: Math.max(0, (prev.returned ?? 0) - 1),
      }));
    } catch (err) {
      console.error(err);
      setError(
        err.message ||
          'Wystąpił błąd podczas usuwania kandydata. Sprawdź backend na DELETE /candidates/{id}.'
      );
    } finally {
      setDeletingIds((prev) => {
        const next = new Set(prev);
        next.delete(candidateId);
        return next;
      });
    }
  };

  const derived = useMemo(() => {
    let withMatches = 0;
    let globallyRejected = 0;

    for (const c of candidates) {
      if (c.has_matched) withMatches += 1;
      if (c.is_globally_rejected) globallyRejected += 1;
    }

    return { withMatches, globallyRejected };
  }, [candidates]);

  const jobOptions = useMemo(() => {
    const map = new Map();
    candidates.forEach((c) => {
      (c.job_matches || []).forEach((jm) => {
        const id = jm.job_id;
        const title = jm.job_title;
        if (id && !map.has(id)) {
          map.set(id, title || id);
        }
      });
    });
    return Array.from(map.entries()).map(([id, title]) => ({ id, title }));
  }, [candidates]);

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold mb-2" style={{ color: '#8B6F47' }}>
            Kandydaci
          </h2>
          <p style={{ color: '#666' }}>
            Przegląd wyników przetwarzania CV i dopasowania do ofert pracy
          </p>
        </div>
        <button
          onClick={fetchCandidates}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ borderColor: '#E0D8CF', color: '#8B6F47' }}
        >
          <RefreshCw
            size={16}
            className={loading ? 'animate-spin' : ''}
          />
          Odśwież
        </button>
      </div>

      {/* Podsumowanie */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div
          className="bg-white rounded-lg shadow-sm p-6 border"
          style={{ borderColor: '#E0D8CF' }}
        >
          <div className="flex items-center gap-3 mb-2">
            <Users size={24} style={{ color: '#8B6F47' }} />
            <span
              className="text-2xl font-bold"
              style={{ color: '#8B6F47' }}
            >
              {summary.total}
            </span>
          </div>
          <p className="text-sm" style={{ color: '#666' }}>
            Łącznie kandydatów (w pliku)
          </p>
          <p className="text-xs mt-1" style={{ color: '#999' }}>
            Wyświetlanych po filtrach: {summary.returned}
          </p>
        </div>

        <div
          className="bg-white rounded-lg shadow-sm p-6 border"
          style={{ borderColor: '#E0D8CF' }}
        >
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle size={24} style={{ color: '#4A7C59' }} />
            <span
              className="text-2xl font-bold"
              style={{ color: '#4A7C59' }}
            >
              {derived.withMatches}
            </span>
          </div>
          <p className="text-sm" style={{ color: '#666' }}>
            Kandydatów z dopasowaniem
          </p>
        </div>

        <div
          className="bg-white rounded-lg shadow-sm p-6 border"
          style={{ borderColor: '#E0D8CF' }}
        >
          <div className="flex items-center gap-3 mb-2">
            <XCircle size={24} style={{ color: '#DC2626' }} />
            <span
              className="text-2xl font-bold"
              style={{ color: '#DC2626' }}
            >
              {derived.globallyRejected}
            </span>
          </div>
          <p className="text-sm" style={{ color: '#666' }}>
            Globalnie odrzuconych
          </p>
        </div>
      </div>

      {/* Filtry */}
      <div
        className="bg-white rounded-lg shadow-sm p-6 mb-6 border"
        style={{ borderColor: '#E0D8CF' }}
      >
        <div className="flex items-center gap-2 mb-4">
          <Filter size={18} style={{ color: '#8B6F47' }} />
          <h3
            className="text-lg font-semibold"
            style={{ color: '#8B6F47' }}
          >
            Filtry
          </h3>
        </div>

        <div className="flex flex-col md:flex-row md:items-center gap-4">
          <div className="flex-1">
            <label
              className="block text-sm font-medium mb-1"
              style={{ color: '#2D2D2D' }}
            >
              Oferta pracy
            </label>
            <select
              value={filterJobId}
              onChange={(e) => setFilterJobId(e.target.value)}
              className="w-full md:w-80 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
              style={{ borderColor: '#E0D8CF' }}
            >
              <option value="">Wszystkie</option>
              {jobOptions.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.title} ({opt.id})
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-4 items-center">
            <label className="inline-flex items-center gap-2 text-sm" style={{ color: '#2D2D2D' }}>
              <input
                type="checkbox"
                checked={onlyMatched}
                onChange={(e) => {
                  const checked = e.target.checked;
                  setOnlyMatched(checked);
                  if (checked) setOnlyRejected(false);
                }}
              />
              Tylko z dopasowaniem
            </label>

            <label className="inline-flex items-center gap-2 text-sm" style={{ color: '#2D2D2D' }}>
              <input
                type="checkbox"
                checked={onlyRejected}
                onChange={(e) => {
                  const checked = e.target.checked;
                  setOnlyRejected(checked);
                  if (checked) setOnlyMatched(false);
                }}
              />
              Tylko odrzuceni
            </label>
          </div>
        </div>
      </div>

      {/* Błąd */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Ładowanie */}
      {loading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-3">
            <RefreshCw size={24} className="animate-spin text-blue-600" />
            <div>
              <p className="font-medium text-blue-900">Ładowanie kandydatów...</p>
              <p className="text-sm text-blue-700">
                Pobieram dane z candidates.json na Google Drive
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Lista kandydatów */}
      {!loading && candidates.length === 0 && (
        <div
          className="bg-white rounded-lg shadow-sm p-6 border text-center"
          style={{ borderColor: '#E0D8CF' }}
        >
          <FileText size={32} className="mx-auto mb-2" style={{ color: '#8B6F47' }} />
          <p className="text-sm" style={{ color: '#666' }}>
            Brak kandydatów do wyświetlenia. Przetwórz CV w zakładce &quot;Przetwarzanie CV&quot;.
          </p>
        </div>
      )}

      {!loading && candidates.length > 0 && (
        <div className="space-y-4">
          {candidates.map((c) => {
            const profile = c.profile || {};
            const matches = c.job_matches || [];
            const globalReason = c.global_rejection_reason;
            const hasMatched = !!c.has_matched;
            const isGloballyRejected = !!c.is_globally_rejected;

            return (
              <div
                key={c.id}
                className="bg-white rounded-lg shadow-sm p-6 border"
                style={{ borderColor: '#E0D8CF' }}
              >
                {/* Nagłówek */}
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-4">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center"
                      style={{ backgroundColor: '#F5F1ED' }}
                    >
                      <Users size={20} style={{ color: '#8B6F47' }} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3
                          className="text-lg font-semibold"
                          style={{ color: '#2D2D2D' }}
                        >
                          {profile.name || 'Nieznane'} {profile.surname || ''}
                        </h3>
                      </div>
                      <div className="flex flex-wrap gap-3 mt-1 text-sm" style={{ color: '#666' }}>
                        {profile.email && (
                          <span className="inline-flex items-center gap-1">
                            <Mail size={14} />
                            {profile.email}
                          </span>
                        )}
                        {profile.phone_number && (
                          <span className="inline-flex items-center gap-1">
                            <Phone size={14} />
                            {profile.phone_number}
                          </span>
                        )}
                        {profile.linkedin_profile && (
                          <span className="inline-flex items-center gap-1">
                            <LinkIcon size={14} />
                            <a
                              href={profile.linkedin_profile}
                              target="_blank"
                              rel="noreferrer"
                              className="underline"
                            >
                              Profil LinkedIn
                            </a>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 items-center">
                    {hasMatched && (
                      <span
                        className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: '#E8F5E9',
                          color: '#2E7D32',
                          border: '1px solid #A5D6A7',
                        }}
                      >
                        <CheckCircle size={12} />
                        Ma dopasowania
                      </span>
                    )}
                    {isGloballyRejected && (
                      <span
                        className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: '#FEF2F2',
                          color: '#B91C1C',
                          border: '1px solid #FECACA',
                        }}
                      >
                        <AlertCircle size={12} />
                        Globalnie odrzucony
                      </span>
                    )}

                    {/* przycisk usuwania */}
                    <button
                      type="button"
                      onClick={() => handleDeleteCandidate(c.id)}
                      disabled={deletingIds.has(c.id)}
                      className="ml-0 md:ml-2 inline-flex items-center gap-1 px-3 py-1 rounded-lg text-xs font-medium border hover:bg-red-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
                      style={{ borderColor: '#FECACA', color: '#B91C1C' }}
                      title="Usuń kandydata"
                    >
                      <Trash2 size={14} />
                      {deletingIds.has(c.id) ? 'Usuwanie...' : 'Usuń'}
                    </button>
                  </div>
                </div>

                {/* Powód globalnego odrzucenia */}
                {globalReason && (
                  <div className="mb-4">
                    <div className="inline-flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium bg-red-50 border border-red-200">
                      <AlertCircle size={14} style={{ color: '#B91C1C' }} />
                      <span style={{ color: '#991B1B' }}>
                        Powód globalnego odrzucenia: {globalReason}
                      </span>
                    </div>
                  </div>
                )}

                {/* Dopasowania do ofert */}
                {matches.length > 0 && (
                  <div className="space-y-3">
                    {matches.map((m) => {
                      const matchedReqs = m.matched_requirements || [];
                      const missingRequired = m.missing_required || [];
                      const missingOptional = m.missing_optional || [];
                      const reasons = m.rejection_reasons || [];

                      const isMatch = m.status === 'MATCHED';

                      return (
                        <div
                          key={m.job_id}
                          className="rounded-lg border p-4"
                          style={{
                            borderColor: isMatch ? '#A5D6A7' : '#E0D8CF',
                            backgroundColor: isMatch ? '#F0F9F4' : '#FFFFFF',
                          }}
                        >
                          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-2">
                            <div className="flex items-center gap-2">
                              <Briefcase size={18} style={{ color: '#8B6F47' }} />
                              <div>
                                <div
                                  className="font-semibold text-sm"
                                  style={{ color: '#2D2D2D' }}
                                >
                                  {m.job_title} ({m.job_id})
                                </div>
                                <div className="text-xs" style={{ color: '#666' }}>
                                  Status: {m.status}
                                </div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div
                                className="text-xl font-bold"
                                style={{ color: '#4A7C59' }}
                              >
                                {m.score_percent}%
                              </div>
                              <div
                                className="text-xs"
                                style={{ color: '#666' }}
                              >
                                {m.total_score}/{m.max_score} pkt
                              </div>
                            </div>
                          </div>

                          {/* Spełnione wymagania */}
                          {matchedReqs.length > 0 && (
                            <div className="mb-2">
                              <p
                                className="text-xs font-medium mb-1"
                                style={{ color: '#4A7C59' }}
                              >
                                ✓ Spełnione wymagania ({matchedReqs.length}):
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {matchedReqs.map((r, idx) => (
                                  <span
                                    key={`${m.job_id}-m-${idx}`}
                                    className="px-2 py-1 rounded text-xs"
                                    style={{
                                      backgroundColor: '#E8F5E9',
                                      color: '#2E7D32',
                                      border: '1px solid #A5D6A7',
                                    }}
                                  >
                                    {r.name} ({r.weight} pkt)
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Brakujące wymagania obowiązkowe */}
                          {missingRequired.length > 0 && (
                            <div className="mb-2">
                              <p
                                className="text-xs font-medium mb-1"
                                style={{ color: '#B91C1C' }}
                              >
                                ✗ Brakujące wymagania obowiązkowe (
                                {missingRequired.length}):
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {missingRequired.map((r, idx) => (
                                  <span
                                    key={`${m.job_id}-mr-${idx}`}
                                    className="px-2 py-1 rounded text-xs"
                                    style={{
                                      backgroundColor: '#FEF2F2',
                                      color: '#B91C1C',
                                      border: '1px solid #FECACA',
                                    }}
                                  >
                                    {r.name} ({r.weight} pkt)
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Brakujące wymagania dodatkowe */}
                          {missingOptional.length > 0 && (
                            <div className="mb-2">
                              <p
                                className="text-xs font-medium mb-1"
                                style={{ color: '#DC2626' }}
                              >
                                ✗ Brakujące wymagania dodatkowe (
                                {missingOptional.length}):
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {missingOptional.map((r, idx) => (
                                  <span
                                    key={`${m.job_id}-mo-${idx}`}
                                    className="px-2 py-1 rounded text-xs"
                                    style={{
                                      backgroundColor: '#FFEBEE',
                                      color: '#C62828',
                                      border: '1px solid #EF9A9A',
                                    }}
                                  >
                                    {r.name} ({r.weight} pkt)
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Powody odrzucenia konkretnej oferty */}
                          {reasons.length > 0 && (
                            <div className="mt-2">
                              <p
                                className="text-xs font-medium mb-1"
                                style={{ color: '#9A3412' }}
                              >
                                Powody odrzucenia dla tej oferty:
                              </p>
                              <ul className="list-disc list-inside text-xs" style={{ color: '#7C2D12' }}>
                                {reasons.map((r, idx) => (
                                  <li key={`${m.job_id}-reason-${idx}`}>{r}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
