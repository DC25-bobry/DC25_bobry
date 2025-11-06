export const REQUIREMENT_TYPES = [
  { value: 'SKILL', label: 'Umiejętność', icon: '🎯' },
  { value: 'EDUCATION', label: 'Wykształcenie', icon: '🎓' },
  { value: 'EXPERIENCE', label: 'Doświadczenie', icon: '💼' },
  { value: 'CERT', label: 'Certyfikat', icon: '📜' },
  { value: 'LANGUAGE', label: 'Język', icon: '🌍' },
  { value: 'OTHER', label: 'Inne', icon: '📌' }
]

export const PRIORITIES = [
  { value: 'REQUIRED', label: 'Wymagane', scoreMultiplier: 3, color: 'bg-red-50 text-red-900 border-red-200' },
  { value: 'IMPORTANT', label: 'Ważne', scoreMultiplier: 2, color: 'bg-orange-50 text-orange-900 border-orange-200' },
  { value: 'OPTIONAL', label: 'Opcjonalne', scoreMultiplier: 1, color: 'bg-blue-50 text-blue-900 border-blue-200' }
]

export const DEFAULT_STATUSES = [
  { value: 'active', label: 'Aktywna', color: 'bg-green-100 text-green-800' },
  { value: 'paused', label: 'Wstrzymana', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'closed', label: 'Zakończona', color: 'bg-gray-100 text-gray-800' }
]

export const PRIORITY_STYLES = {
  REQUIRED: { headingBg: '#FEF2F2', headingText: '#991B1B', border: '#FECACA', cardBg: '#FFF7F7' },
  IMPORTANT: { headingBg: '#FFF7ED', headingText: '#7C2D12', border: '#FED7AA', cardBg: '#FFFBF5' },
  OPTIONAL: { headingBg: '#EFF6FF', headingText: '#1E3A8A', border: '#BFDBFE', cardBg: '#F8FBFF' }
}