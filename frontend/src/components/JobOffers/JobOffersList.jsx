import React, { useState } from 'react';
import JobOfferCard from './JobOfferCard.jsx';
import JobOfferForm from './JobOfferForm.jsx';
import useJobOffers from '../../hooks/useJobOffers.js';

export default function JobOffersList() {
  const { jobs, loading, error, addJob, updateJob, removeJob } = useJobOffers();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editing, setEditing] = useState(null);

  const handleOpenNew = () => {
    setEditing(null);
    setIsFormOpen(true);
  };

  const handleEdit = (job) => {
    setEditing(job);
    setIsFormOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Na pewno usunąć tę ofertę?')) return;
    await removeJob(id);
  };

  const handleSave = async (job) => {
    if (editing) {
      await updateJob(editing.id, job);
    } else {
      await addJob(job);
    }
    setIsFormOpen(false);
    setEditing(null);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2
            className="text-2xl font-bold"
            style={{ color: '#8B6F47' }}
          >
            Oferty Pracy
          </h2>
          <p style={{ color: '#666' }}>Zarządzaj ofertami rekrutacyjnymi</p>
        </div>
        <button
          onClick={handleOpenNew}
          className="flex items-center gap-2 px-6 py-3 rounded-lg text-white"
          style={{ backgroundColor: '#8B6F47' }}
        >
          Nowa Oferta
        </button>
      </div>

      {loading && (
        <div className="mb-4 text-sm" style={{ color: '#666' }}>
          Ładowanie ofert...
        </div>
      )}

      {error && (
        <div className="mb-4 text-sm text-red-600">
          Błąd podczas pobierania ofert: {error}
        </div>
      )}

      <div className="grid gap-4">
        {jobs.map((job) => (
          <JobOfferCard
            key={job.id}
            job={job}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        ))}

        {!loading && jobs.length === 0 && !error && (
          <div
            className="border rounded-lg p-6 text-center text-sm"
            style={{ borderColor: '#E0D8CF', backgroundColor: '#F5F1ED' }}
          >
            Brak ofert pracy. Dodaj pierwszą ofertę.
          </div>
        )}
      </div>

      {isFormOpen && (
        <JobOfferForm
          onClose={() => {
            setIsFormOpen(false);
            setEditing(null);
          }}
          onSave={handleSave}
          editing={editing}
        />
      )}
    </div>
  );
}
