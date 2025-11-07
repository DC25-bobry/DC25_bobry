import React, { useState } from 'react'
import JobOfferCard from './JobOfferCard.jsx'
import JobOfferForm from './JobOfferForm.jsx'
import useJobOffers from '../../hooks/useJobOffers.js'


export default function JobOffersList() {
    const { jobs, addJob, updateJob, removeJob } = useJobOffers()
    const [isFormOpen, setIsFormOpen] = useState(false)
    const [editing, setEditing] = useState(null)


    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold" style={{ color: '#8B6F47' }}>Oferty Pracy</h2>
                    <p style={{ color: '#666' }}>Zarządzaj ofertami rekrutacyjnymi</p>
                </div>
                <button onClick={() => setIsFormOpen(true)} className="flex items-center gap-2 px-6 py-3 rounded-lg text-white" style={{ backgroundColor: '#8B6F47' }}>
                    Nowa Oferta
                </button>
            </div>


            <div className="grid gap-4">
                {jobs.map(job => (
                    <JobOfferCard key={job.id} job={job} onEdit={() => { setEditing(job); setIsFormOpen(true) }} onDelete={() => removeJob(job.id)} />
                ))}
            </div>


            {isFormOpen && (
                <JobOfferForm
                    onClose={() => { setIsFormOpen(false); setEditing(null) }}
                    onSave={(newJob) => { editing ? updateJob(editing.id, newJob) : addJob(newJob); setIsFormOpen(false); setEditing(null) }}
                    editing={editing}
                />
            )}
        </div>
    )
}