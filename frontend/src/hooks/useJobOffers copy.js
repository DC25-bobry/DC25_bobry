import { useState } from 'react'


const initialJobs = [
  {
    id: 'JOB-2025-001',
    title: 'Asystent Kierownika ds. obsługi ekspresu',
    contractType: 'UOP',
    seniority: 'Mid',
    description: 'Poszukujemy osoby do obsługi ekspresu do kawy...',
    status: 'active',
    publishDate: '2025-01-15',
    expiryDate: '2025-03-15',
    requirements: [
      {
        id: 'r-1',
        type: 'SKILL',
        name: 'Obsługa ekspresu',
        priority: 'REQUIRED',
        weight: 8,
        keywords: ['ekspres', 'coffee machine', 'barista'],
        synonyms: ['kawiarnia', 'coffee machine', 'barista']
      },
      {
        id: 'r-2',
        type: 'OTHER',
        name: 'Komunikatywność',
        priority: 'REQUIRED',
        weight: 6,
        keywords: ['komunikacja', 'komunikatywność'],
        synonyms: ['kontakt', 'rozmowa']
      },
      {
        id: 'r-3',
        type: 'EXPERIENCE',
        name: 'Doświadczenie w gastronomii',
        priority: 'IMPORTANT',
        weight: 5,
        keywords: ['gastronomia', 'restauracja'],
        synonyms: []
      },
      {
        id: 'r-4',
        type: 'LANGUAGE',
        name: 'Znajomość języka angielskiego',
        priority: 'OPTIONAL',
        weight: 4,
        keywords: ['english', 'angielski'],
        synonyms: ['english']
      }
    ]
  }
]


export default function useJobOffers() {
    const [jobs, setJobs] = useState(initialJobs)


    const addJob = (job) => setJobs(prev => [...prev, job])
    const updateJob = (id, data) => setJobs(prev => prev.map(j => j.id === id ? { ...j, ...data } : j))
    const removeJob = (id) => setJobs(prev => prev.filter(j => j.id !== id))


    return { jobs, addJob, updateJob, removeJob }
}