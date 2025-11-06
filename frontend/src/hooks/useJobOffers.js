import { useState } from 'react'

const initialJobs = [
  {
    id: 'JOB-2025-001',
    title: 'Asystent Kierownika ds. obsługi ekspresu',
    contractType: 'UOP',
    seniority: 'Mid',
    description: 'Poszukujemy osoby do obsługi ekspresu do kawy w biurze — przygotowywanie napojów, kontrola stanu urządzeń, kontakt z klientami.',
    status: 'active',
    publishDate: '2025-01-15',
    expiryDate: '2025-03-15',
    requirements: [
      {
        id: 'REQ-1',
        type: 'SKILL',
        name: 'Obsługa ekspresu',
        priority: 'REQUIRED',
        weight: 10,
        keywords: ['ekspres', 'kawa', 'barista'],
        synonyms: ['kawiarnia', 'coffee machine', 'barista']
      },
      {
        id: 'REQ-2',
        type: 'SKILL',
        name: 'Komunikatywność',
        priority: 'REQUIRED',
        weight: 8,
        keywords: ['komunikacja', 'kontakt', 'rozmowa'],
        synonyms: ['komunikatywność', 'interpersonal']
      },
      {
        id: 'REQ-3',
        type: 'EXPERIENCE',
        name: 'Doświadczenie w gastronomii',
        priority: 'IMPORTANT',
        weight: 5,
        keywords: ['gastronomia', 'kawiarnia', 'restauracja'],
        synonyms: []
      },
      {
        id: 'REQ-4',
        type: 'LANGUAGE',
        name: 'Znajomość języka angielskiego',
        priority: 'OPTIONAL',
        weight: 3,
        keywords: ['english', 'angielski'],
        synonyms: []
      }
    ]
  }
]

export default function useJobOffers() {
  const [jobs, setJobs] = useState(initialJobs)

  const addJob = (job) => {
    setJobs(prev => [...prev, job])
  }

  const updateJob = (id, data) => {
    setJobs(prev => prev.map(j => j.id === id ? { ...j, ...data } : j))
  }

  const removeJob = (id) => {
    setJobs(prev => prev.filter(j => j.id !== id))
  }

  return { jobs, addJob, updateJob, removeJob }
}
