import React, { useState, useEffect } from 'react';
import { X, Trash2, Plus, Sparkles } from 'lucide-react';
import { REQUIREMENT_TYPES, PRIORITIES, DEFAULT_STATUSES } from '../../utils/constants'


export default function JobOfferForm({ onClose, onSave, editing = null }) {
  const emptyForm = {
    title: '',
    contractType: 'UOP',
    seniority: 'Mid',
    description: '',
    status: 'active',
    publishDate: new Date().toISOString().split('T')[0],
    expiryDate: '',
    requirements: []
  };

  const [formData, setFormData] = useState(editing ? { ...editing } : emptyForm);

  const [currentReq, setCurrentReq] = useState({
    type: 'SKILL',
    name: '',
    priority: 'REQUIRED',
    weight: 5,
    keywords: '',
    synonyms: []
  });

  useEffect(() => {
    if (editing) setFormData({ ...editing });
  }, [editing]);

  const generateSynonymsMock = (keywords) => {
    if (!keywords) return [];
    const tokens = keywords.split(',').map(k => k.trim()).filter(Boolean);
    const extra = [];
    tokens.forEach(t => {
      const low = t.toLowerCase();
      if (low.includes('react')) extra.push('reactjs', 'react.js', 'react framework');
      if (low.includes('python')) extra.push('python3', 'python programming');
      if (low.includes('mgr') || low.includes('wykształcenie')) extra.push('magister', 'studia', 'dyplom');
      if (low.includes('ekspres')) extra.push('kawiarnia', 'coffee machine', 'barista');
      if (low.includes('komunikacja')) extra.push('komunikatywność', 'kontakt', 'rozmowa');
    });
    return Array.from(new Set([...tokens, ...extra]));
  };

  const handleAddRequirement = () => {
    if (!currentReq.name.trim()) {
      alert('Uzupełnij nazwę wymagania');
      return;
    }
    if (!currentReq.keywords.trim()) {
      alert('Dodaj co najmniej jedno słowo kluczowe (seed)');
      return;
    }

    const keywordsArray = currentReq.keywords.split(',').map(k => k.trim()).filter(Boolean);
    const synonyms = currentReq.synonyms.length > 0 
      ? currentReq.synonyms 
      : generateSynonymsMock(currentReq.keywords);

    const newReq = {
      id: Date.now(),
      type: currentReq.type,
      name: currentReq.name.trim(),
      priority: currentReq.priority,
      weight: Number(currentReq.weight) || 1,
      keywords: keywordsArray,
      synonyms
    };

    setFormData(prev => ({ ...prev, requirements: [...(prev.requirements || []), newReq] }));

    setCurrentReq({ type: 'SKILL', name: '', priority: 'REQUIRED', weight: 5, keywords: '', synonyms: [] });
  };

  const handleRemoveRequirement = (id) => {
    setFormData(prev => ({ ...prev, requirements: (prev.requirements || []).filter(r => r.id !== id) }));
  };

  const handleEditSynonyms = (id, newSynonymsArray) => {
    setFormData(prev => ({
      ...prev,
      requirements: prev.requirements.map(r => r.id === id ? { ...r, synonyms: newSynonymsArray } : r)
    }));
  };

  const generateJobCode = () => {
    const year = new Date().getFullYear();
    const random = Math.floor(Math.random() * 900) + 100;
    return `JOB-${year}-${String(random).padStart(3, '0')}`;
  };

  const handleSubmit = (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!formData.title || !(formData.requirements && formData.requirements.length)) {
      alert('Wypełnij tytuł i dodaj przynajmniej jedno wymaganie.');
      return;
    }

    const job = { ...formData };
    if (!job.id) job.id = generateJobCode();
    onSave(job);
  };

  const groupedRequirements = PRIORITIES.map(priority => ({
    ...priority,
    requirements: (formData.requirements || []).filter(req => req.priority === priority.value)
  }));

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="bg-white rounded-lg max-w-5xl w-full my-8 max-h-[90vh] overflow-y-auto border-2" style={{ borderColor: '#8B6F47' }}>
        <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center z-10" style={{ borderColor: '#E0D8CF' }}>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold" style={{ color: '#8B6F47' }}>
              {formData.id ? 'Edytuj Ofertę' : 'Nowa Oferta Pracy'}
            </h2>
          </div>
          <button onClick={onClose} style={{ color: '#666' }} className="hover:opacity-70">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium mb-2" style={{ color: '#2D2D2D' }}>
                Nazwa stanowiska *
              </label>
              <input
                value={formData.title}
                onChange={e => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                style={{ borderColor: '#E0D8CF' }}
                placeholder="np. Asystent Kierownika ds. obsługi ekspresu"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: '#2D2D2D' }}>Rodzaj umowy</label>
              <select
                value={formData.contractType}
                onChange={e => setFormData({ ...formData, contractType: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
                style={{ borderColor: '#E0D8CF' }}
              >
                <option>UOP</option>
                <option>B2B</option>
                <option>UZ</option>
                <option>UOD</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: '#2D2D2D' }}>Poziom seniority</label>
              <select
                value={formData.seniority}
                onChange={e => setFormData({ ...formData, seniority: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
                style={{ borderColor: '#E0D8CF' }}
              >
                <option>Junior</option>
                <option>Mid</option>
                <option>Senior</option>
                <option>Lead</option>
                <option>Expert</option>
              </select>
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-medium mb-2" style={{ color: '#2D2D2D' }}>Opis stanowiska</label>
              <textarea
                value={formData.description}
                onChange={e => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                style={{ borderColor: '#E0D8CF' }}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: '#2D2D2D' }}>Status</label>
              <select
                value={formData.status}
                onChange={e => setFormData({ ...formData, status: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
                style={{ borderColor: '#E0D8CF' }}
              >
                {DEFAULT_STATUSES.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: '#2D2D2D' }}>Data publikacji</label>
              <input
                type="date"
                value={formData.publishDate}
                onChange={e => setFormData({ ...formData, publishDate: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
                style={{ borderColor: '#E0D8CF' }}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: '#2D2D2D' }}>Data wygaśnięcia</label>
              <input
                type="date"
                value={formData.expiryDate}
                onChange={e => setFormData({ ...formData, expiryDate: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
                style={{ borderColor: '#E0D8CF' }}
              />
            </div>
          </div>

          <div className="border-t pt-6" style={{ borderColor: '#E0D8CF' }}>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: '#8B6F47' }}>
              Dodaj wymaganie
            </h3>

            <div className="p-4 rounded-lg space-y-3 mb-4" style={{ backgroundColor: '#F5F1ED', borderColor: '#E0D8CF', border: '1px solid' }}>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium mb-1" style={{ color: '#2D2D2D' }}>Typ wymagania *</label>
                  <select
                    value={currentReq.type}
                    onChange={e => setCurrentReq({ ...currentReq, type: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none"
                    style={{ borderColor: '#E0D8CF', backgroundColor: '#FFFFFF' }}
                  >
                    {REQUIREMENT_TYPES.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium mb-1" style={{ color: '#2D2D2D' }}>Priorytet *</label>
                  <select
                    value={currentReq.priority}
                    onChange={e => setCurrentReq({ ...currentReq, priority: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none"
                    style={{ borderColor: '#E0D8CF', backgroundColor: '#FFFFFF' }}
                  >
                    {PRIORITIES.map(p => (
                      <option key={p.value} value={p.value}>{p.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium mb-1" style={{ color: '#2D2D2D' }}>Waga (1-10)</label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={currentReq.weight}
                    onChange={e => setCurrentReq({ ...currentReq, weight: Number(e.target.value || 1) })}
                    className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none"
                    style={{ borderColor: '#E0D8CF', backgroundColor: '#FFFFFF' }}
                  />
                </div>

                <div className="col-span-3">
                  <label className="block text-xs font-medium mb-1" style={{ color: '#2D2D2D' }}>Nazwa wymagania *</label>
                  <input
                    value={currentReq.name}
                    onChange={e => setCurrentReq({ ...currentReq, name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none"
                    style={{ borderColor: '#E0D8CF', backgroundColor: '#FFFFFF' }}
                    placeholder="np. Wykształcenie wyższe, Obsługa ekspresu"
                  />
                </div>

                <div className="col-span-3">
                  <label className="block text-xs font-medium mb-1" style={{ color: '#2D2D2D' }}>Słowa kluczowe (oddziel przecinkami) *</label>
                  <input
                    value={currentReq.keywords}
                    onChange={e => setCurrentReq({ ...currentReq, keywords: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none"
                    style={{ borderColor: '#E0D8CF', backgroundColor: '#FFFFFF' }}
                    placeholder="np. react, reactjs, ekspres, kawa"
                  />
                  <p className="text-xs mt-1" style={{ color: '#666' }}>
                    Te słowa kluczowe będą używane do wyszukiwania wymagania w CV
                  </p>
                </div>

                <div className="col-span-3">
                  <label className="block text-xs font-medium mb-1" style={{ color: '#2D2D2D' }}>
                    <Sparkles size={12} className="inline" style={{ color: '#8B6F47' }} /> Synonimy AI (edytowalne)
                  </label>
                  <input
                    value={currentReq.synonyms.join(', ')}
                    onChange={e => setCurrentReq({ ...currentReq, synonyms: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                    className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none"
                    style={{ borderColor: '#E0D8CF', backgroundColor: '#FFFFFF' }}
                    placeholder="Automatycznie wygenerowane po dodaniu"
                  />
                  <p className="text-xs mt-1" style={{ color: '#666' }}>
                    System automatycznie wygeneruje synonimy, ale możesz je edytować
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    if (currentReq.keywords) {
                      setCurrentReq(prev => ({ ...prev, synonyms: generateSynonymsMock(prev.keywords) }));
                    }
                  }}
                  className="px-4 py-2 rounded-lg border hover:bg-gray-50 transition text-sm flex items-center gap-2"
                  style={{ borderColor: '#E0D8CF', color: '#8B6F47' }}
                >
                  <Sparkles size={14} />
                  Generuj synonimy
                </button>

                <button
                  type="button"
                  onClick={handleAddRequirement}
                  className="ml-auto px-4 py-2 rounded-lg text-white hover:opacity-90 transition text-sm flex items-center gap-2"
                  style={{ backgroundColor: '#8B6F47' }}
                >
                  <Plus size={14} />
                  Dodaj wymaganie
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {groupedRequirements.map(group => 
                group.requirements.length > 0 && (
                  <div key={group.value}>
                    <h4 className={`font-semibold mb-3 px-3 py-2 rounded inline-block border text-sm ${group.color}`}>
                      {group.label} ({group.requirements.length})
                    </h4>
                    <div className="space-y-2 mt-2">
                      {group.requirements.map(req => (
                        <div
                          key={req.id}
                          className={`border rounded-lg p-4 ${group.color}`}
                          style={{ borderWidth: '1px' }}
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="font-medium text-sm" style={{ color: '#2D2D2D' }}>
                                  {req.name}
                                </span>
                                <span className="text-xs px-2 py-1 rounded" style={{ backgroundColor: '#FFFFFF', color: '#666', border: '1px solid #E0D8CF' }}>
                                  {REQUIREMENT_TYPES.find(t => t.value === req.type)?.label}
                                </span>
                                <span className="text-xs px-2 py-1 rounded" style={{ backgroundColor: '#FFFFFF', color: '#666', border: '1px solid #E0D8CF' }}>
                                  Waga: {req.weight}
                                </span>
                              </div>

                              <div className="text-xs mb-2" style={{ color: '#666' }}>
                                <strong>Słowa kluczowe:</strong> {(req.keywords || []).join(', ')}
                              </div>

                              <div className="text-xs" style={{ color: '#666' }}>
                                <div className="flex items-center gap-2 mb-1">
                                  <Sparkles size={12} style={{ color: '#8B6F47' }} />
                                  <strong>Synonimy AI:</strong>
                                </div>
                                <input
                                  className="w-full text-xs px-2 py-1 border rounded focus:outline-none focus:ring-1"
                                  style={{ borderColor: '#E0D8CF', backgroundColor: '#FFFFFF' }}
                                  value={(req.synonyms || []).join(', ')}
                                  onChange={e => handleEditSynonyms(req.id, e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                                  placeholder="Edytuj synonimy..."
                                />
                              </div>
                            </div>

                            <button
                              type="button"
                              onClick={() => handleRemoveRequirement(req.id)}
                              className="text-red-600 hover:text-red-800 p-2"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              )}

              {(formData.requirements || []).length === 0 && (
                <div className="text-center py-8 border rounded-lg" style={{ borderColor: '#E0D8CF', backgroundColor: '#F5F1ED' }}>
                  <Sparkles size={32} className="mx-auto mb-2" style={{ color: '#8B6F47' }} />
                  <p style={{ color: '#666' }}>Dodaj wymagania do oferty pracy</p>
                  <p className="text-sm mt-1" style={{ color: '#999' }}>
                    System automatycznie wygeneruje synonimy AI
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="flex gap-3 pt-4 border-t" style={{ borderColor: '#E0D8CF' }}>
            <button
              type="button"
              onClick={() => {
                setFormData(emptyForm);
                onClose?.();
              }}
              className="flex-1 px-6 py-3 border rounded-lg hover:bg-gray-50 transition font-medium"
              style={{ borderColor: '#E0D8CF', color: '#2D2D2D' }}
            >
              Anuluj
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              className="flex-1 px-6 py-3 text-white rounded-lg hover:opacity-90 transition font-medium"
              style={{ backgroundColor: '#8B6F47' }}
            >
              {formData.id ? 'Zapisz Zmiany' : 'Utwórz Ofertę'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}