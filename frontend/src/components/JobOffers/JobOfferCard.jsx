import React from 'react';
import {
  Briefcase,
  Calendar,
  Download,
  Edit2,
  Trash2,
  FileText,
  UserCheck,
} from 'lucide-react';
import {
  DEFAULT_STATUSES,
  REQUIREMENT_TYPES,
  PRIORITIES,
  PRIORITY_STYLES,
} from '../../utils/constants';

const groupRequirementsByPriority = (requirements = []) =>
  (requirements || []).reduce((acc, r) => {
    const pr = (r.priority || 'OPTIONAL').toUpperCase();
    acc[pr] = acc[pr] || [];
    acc[pr].push(r);
    return acc;
  }, {});

const formatDatePL = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr;
  return new Intl.DateTimeFormat('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(d);
};

export default function JobOfferCard({ job, onEdit, onDelete }) {
  const advancedReqs = job.requirements || [];

  const fallbackReqs = [
    ...(job.obligatory_requirements || []).map((r) => ({
      ...r,
      priority: 'REQUIRED',
      type: r.type ?? 'SKILL',
    })),
    ...(job.important_requirements || []).map((r) => ({
      ...r,
      priority: 'IMPORTANT',
      type: r.type ?? 'SKILL',
    })),
    ...(job.optional_requirements || []).map((r) => ({
      ...r,
      priority: 'OPTIONAL',
      type: r.type ?? 'SKILL',
    })),
  ];

  const allReqs = advancedReqs.length ? advancedReqs : fallbackReqs;
  const grouped = groupRequirementsByPriority(allReqs);

  const statusMeta = DEFAULT_STATUSES.find((s) => s.value === job.status);

  return (
    <div
      className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition border"
      style={{ borderColor: '#E0D8CF' }}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3
              className="text-xl font-semibold"
              style={{ color: '#8B6F47' }}
            >
              {job.title}
            </h3>

            <span
              className={`px-3 py-1 rounded-full text-xs font-medium border ${
                statusMeta?.color ||
                'bg-gray-100 text-gray-800 border-gray-200'
              }`}
              aria-label={`Status: ${statusMeta?.label || job.status}`}
              title={statusMeta?.label || job.status}
            >
              {statusMeta?.label || job.status}
            </span>
          </div>

          <div className="flex flex-wrap gap-3 text-sm mb-3 text-gray-700">
            <div className="flex items-center gap-1 border rounded-md px-2 py-1">
              <Briefcase size={16} />
              <span>{job.id}</span>
            </div>

            <div className="flex items-center gap-1 border rounded-md px-2 py-1">
              <FileText size={16} />
              <span>{job.contractType}</span>
            </div>

            <div className="flex items-center gap-1 border rounded-md px-2 py-1">
              <UserCheck size={16} />
              <span>{job.seniority}</span>
            </div>

            <div className="flex items-center gap-1 border rounded-md px-2 py-1">
              <Calendar size={16} />
              <span>
                {formatDatePL(job.publishDate)}
                {job.expiryDate && ` - ${formatDatePL(job.expiryDate)}`}
              </span>
            </div>
          </div>

          <div className="space-y-4">
            {(PRIORITIES || [
              { value: 'REQUIRED', label: 'Wymagane' },
              { value: 'IMPORTANT', label: 'Ważne' },
              { value: 'OPTIONAL', label: 'Opcjonalne' },
            ]).map((groupMeta) => {
              const pr = groupMeta.value;
              const reqs = grouped[pr] || [];
              if (!reqs.length) return null;
              const style =
                PRIORITY_STYLES?.[pr] ||
                PRIORITY_STYLES?.OPTIONAL || {
                  headingBg: '#fff',
                  headingText: '#000',
                  border: '#e5e7eb',
                  cardBg: '#fff',
                };
              return (
                <div key={pr}>
                  <div
                    className="inline-block px-3 py-1 rounded text-sm font-semibold mb-2"
                    style={{
                      backgroundColor: style.headingBg,
                      color: style.headingText,
                      border: `1px solid ${style.border}`,
                    }}
                  >
                    {groupMeta.label || pr} ({reqs.length})
                  </div>

                  <div className="flex flex-wrap gap-3 mt-2">
                    {reqs.map((req) => (
                      <div
                        key={req.id}
                        className="rounded-lg p-3 border"
                        style={{
                          minWidth: 200,
                          borderColor: style.border,
                          backgroundColor: style.cardBg,
                        }}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-1">
                            <div
                              className="text-xs px-2 py-0.5 rounded"
                              style={{
                                backgroundColor: '#FFFFFF',
                                color: '#666',
                                border: '1px solid #E0D8CF',
                              }}
                            >
                              {(
                                REQUIREMENT_TYPES.find(
                                  (t) => t.value === req.type
                                ) || {}
                              ).label || req.type}
                            </div>
                            <div
                              className="text-xs px-2 py-0.5 rounded"
                              style={{
                                backgroundColor: '#FFFFFF',
                                color: '#666',
                                border: '1px solid #E0D8CF',
                              }}
                            >
                              {req.weight ?? '-'}
                            </div>
                          </div>
                          <div
                            className="font-medium text-sm"
                            style={{ color: '#2D2D2D' }}
                          >
                            {req.name}
                          </div>
                        </div>

                        {Array.isArray(req.keywords) &&
                          req.keywords.length > 0 && (
                            <div
                              className="mt-2 text-xs"
                              style={{ color: '#666' }}
                            >
                              <strong>Słowa kluczowe:</strong>{' '}
                              {req.keywords.join(', ')}
                            </div>
                          )}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}

            {allReqs.length === 0 && (
              <div className="text-sm text-gray-500">
                Brak wymagań w tej ofercie.
              </div>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => {
              const blob = new Blob([JSON.stringify(job, null, 2)], {
                type: 'application/json',
              });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `${job.id || 'job'}.json`;
              a.click();
            }}
            className="p-2 rounded-lg transition hover:bg-green-50"
            style={{ color: '#4A7C59' }}
            title="Eksportuj JSON"
          >
            <Download size={18} />
          </button>

          <button
            onClick={() => onEdit?.(job)}
            className="p-2 rounded-lg transition"
            style={{ color: '#8B6F47' }}
            title="Edytuj ofertę"
          >
            <Edit2 size={18} />
          </button>

          <button
            onClick={() => onDelete?.(job.id)}
            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
            title="Usuń ofertę"
          >
            <Trash2 size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
