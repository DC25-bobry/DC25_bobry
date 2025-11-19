import React, { useState, useRef } from 'react';
import { Upload, X, FileText, Mail, CheckCircle, XCircle, Clock, AlertCircle, UserCheck, Briefcase, Send } from 'lucide-react';

// mock
const extractTextFromFile = async (file) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const mockCVs = [
        {
          name: 'Jan Kowalski',
          skills: ['React', 'JavaScript', 'TypeScript', 'Node.js', 'komunikacja'],
          education: 'Magister informatyki',
          experience: '5 lat doświadczenia w programowaniu frontend'
        },
        {
          name: 'Anna Nowak',
          skills: ['Python', 'Django', 'PostgreSQL', 'ekspres do kawy', 'komunikatywność'],
          education: 'Licencjat zarządzania',
          experience: '2 lata w branży gastronomicznej'
        },
        {
          name: 'Piotr Wiśniewski',
          skills: ['Java', 'Spring Boot', 'Angular', 'wykształcenie wyższe'],
          education: 'Magister ekonomii',
          experience: '3 lata w IT'
        }
      ];
      
      const randomCV = mockCVs[Math.floor(Math.random() * mockCVs.length)];
      const text = `
        ${randomCV.name}
        Umiejętności: ${randomCV.skills.join(', ')}
        Wykształcenie: ${randomCV.education}
        Doświadczenie: ${randomCV.experience}
      `;
      resolve(text);
    }, 500);
  });
};

// mock
const analyzeCV = (cvText, jobRequirements) => {
  const text = cvText.toLowerCase();
  let totalScore = 0;
  let maxScore = 0;
  const matchedRequirements = [];
  const unmatchedRequirements = [];

  (jobRequirements || []).forEach(req => {
    const weight = req.weight || 5;
    maxScore += weight;

    const allKeywords = [...(req.keywords || []), ...(req.synonyms || [])];
    const matched = allKeywords.some(kw => text.includes(kw.toLowerCase()));

    if (matched) {
      totalScore += weight;
      matchedRequirements.push({
        name: req.name,
        type: req.type,
        priority: req.priority,
        weight: weight
      });
    } else {
      unmatchedRequirements.push({
        name: req.name,
        type: req.type,
        priority: req.priority,
        weight: weight
      });
    }
  });

  const score = maxScore > 0 ? Math.round((totalScore / maxScore) * 100) : 0;

  return {
    score,
    totalScore,
    maxScore,
    matchedRequirements,
    unmatchedRequirements
  };
};

// mock
const useMockJobOffers = () => {
  const [jobs] = useState([
    {
      id: 'JOB-2025-001',
      title: 'Frontend Developer',
      status: 'active',
      requirements: [
        {
          id: 1,
          type: 'SKILL',
          name: 'React',
          priority: 'REQUIRED',
          weight: 10,
          keywords: ['react', 'reactjs'],
          synonyms: ['react.js', 'react framework']
        },
        {
          id: 2,
          type: 'SKILL',
          name: 'JavaScript',
          priority: 'REQUIRED',
          weight: 8,
          keywords: ['javascript', 'js'],
          synonyms: ['ES6', 'ECMAScript']
        },
        {
          id: 3,
          type: 'SOFT_SKILL',
          name: 'Komunikacja',
          priority: 'IMPORTANT',
          weight: 5,
          keywords: ['komunikacja', 'komunikatywność'],
          synonyms: ['kontakt', 'rozmowa', 'współpraca']
        }
      ]
    },
    {
      id: 'JOB-2025-002',
      title: 'Asystent Kierownika ds. obsługi ekspresu',
      status: 'active',
      requirements: [
        {
          id: 4,
          type: 'EDUCATION',
          name: 'Wykształcenie wyższe',
          priority: 'REQUIRED',
          weight: 7,
          keywords: ['mgr', 'wykształcenie', 'magister'],
          synonyms: ['studia', 'dyplom', 'uniwersytet']
        },
        {
          id: 5,
          type: 'SKILL',
          name: 'Obsługa ekspresu',
          priority: 'REQUIRED',
          weight: 9,
          keywords: ['ekspres', 'kawa'],
          synonyms: ['kawiarnia', 'coffee machine', 'barista']
        },
        {
          id: 6,
          type: 'SOFT_SKILL',
          name: 'Komunikacja',
          priority: 'IMPORTANT',
          weight: 6,
          keywords: ['komunikacja', 'komunikatywność'],
          synonyms: ['kontakt', 'rozmowa']
        }
      ]
    }
  ]);

  return jobs;
};

export default function CVPage() {
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [topCandidatesCount, setTopCandidatesCount] = useState(3);
  const [emailsSent, setEmailsSent] = useState(new Set());
  const fileInputRef = useRef(null);
  
  const jobOffers = useMockJobOffers();

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files).filter(
      f => f.type === 'application/pdf' || 
           f.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const processCV = async () => {
    if (files.length === 0) {
      alert('Dodaj przynajmniej jedno CV');
      return;
    }

    setProcessing(true);
    setResults(null);
    setEmailsSent(new Set());

    const candidateResults = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const cvText = await extractTextFromFile(file);
      
      const jobMatches = jobOffers
        .filter(job => job.status === 'active')
        .map(job => {
          const analysis = analyzeCV(cvText, job.requirements);
          return {
            jobId: job.id,
            jobTitle: job.title,
            ...analysis
          };
        })
        .filter(match => match.score > 0)
        .sort((a, b) => b.score - a.score);

      candidateResults.push({
        id: `CV-${Date.now()}-${i}`,
        fileName: file.name,
        cvText,
        matches: jobMatches,
        bestMatch: jobMatches[0] || null,
        status: jobMatches.length > 0 ? 'matched' : 'rejected'
      });
    }

    setResults(candidateResults);
    setProcessing(false);
  };

  const sendEmailToTopCandidates = () => {
    if (!results) return;

    const jobGroups = {};
    results.forEach(candidate => {
      if (candidate.bestMatch) {
        const jobId = candidate.bestMatch.jobId;
        if (!jobGroups[jobId]) {
          jobGroups[jobId] = [];
        }
        jobGroups[jobId].push(candidate);
      }
    });

    const newEmailsSent = new Set(emailsSent);
    Object.keys(jobGroups).forEach(jobId => {
      const candidates = jobGroups[jobId]
        .sort((a, b) => b.bestMatch.score - a.bestMatch.score)
        .slice(0, topCandidatesCount);
      
      candidates.forEach(candidate => {
        // simulate mail sent
        newEmailsSent.add(candidate.id);
      });
    });

    setEmailsSent(newEmailsSent);
    alert(`Wysłano maile do ${newEmailsSent.size} kandydatów!`);
  };

  const matchedCandidates = results?.filter(c => c.status === 'matched') || [];
  const rejectedCandidates = results?.filter(c => c.status === 'rejected') || [];

  const candidatesByJob = {};
  matchedCandidates.forEach(candidate => {
    if (candidate.bestMatch) {
      const jobId = candidate.bestMatch.jobId;
      if (!candidatesByJob[jobId]) {
        candidatesByJob[jobId] = [];
      }
      candidatesByJob[jobId].push(candidate);
    }
  });

  Object.keys(candidatesByJob).forEach(jobId => {
    candidatesByJob[jobId].sort((a, b) => b.bestMatch.score - a.bestMatch.score);
  });

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2" style={{ color: '#8B6F47' }}>
          Przetwarzanie CV
        </h2>
        <p style={{ color: '#666' }}>
          Przesyłaj CV kandydatów i automatycznie dopasuj ich do ofert pracy
        </p>
      </div>

      {/* Panel przesyłania plików */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6 border" style={{ borderColor: '#E0D8CF' }}>
        <h3 className="text-lg font-semibold mb-4" style={{ color: '#8B6F47' }}>
          1. Przesyłanie CV
        </h3>

        <div 
          className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50 transition"
          style={{ borderColor: '#E0D8CF' }}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload size={48} className="mx-auto mb-4" style={{ color: '#8B6F47' }} />
          <p className="text-lg font-medium mb-2" style={{ color: '#2D2D2D' }}>
            Kliknij lub przeciągnij pliki CV
          </p>
          <p className="text-sm" style={{ color: '#666' }}>
            Obsługiwane formaty: PDF, DOCX
          </p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>

        {files.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="font-medium text-sm" style={{ color: '#2D2D2D' }}>
              Wybrane pliki ({files.length}):
            </p>
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 rounded-lg border"
                style={{ borderColor: '#E0D8CF', backgroundColor: '#F5F1ED' }}
              >
                <div className="flex items-center gap-3">
                  <FileText size={20} style={{ color: '#8B6F47' }} />
                  <span className="text-sm">{file.name}</span>
                  <span className="text-xs" style={{ color: '#666' }}>
                    ({(file.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 hover:bg-red-50 rounded transition"
                  style={{ color: '#DC2626' }}
                >
                  <X size={18} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Panel konfiguracji */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6 border" style={{ borderColor: '#E0D8CF' }}>
        <h3 className="text-lg font-semibold mb-4" style={{ color: '#8B6F47' }}>
          2. Konfiguracja
        </h3>

        <div className="flex items-center gap-4">
          <label className="text-sm font-medium" style={{ color: '#2D2D2D' }}>
            Liczba najlepszych kandydatów (na ofertę):
          </label>
          <input
            type="number"
            min="1"
            max="20"
            value={topCandidatesCount}
            onChange={(e) => setTopCandidatesCount(Number(e.target.value))}
            className="w-24 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
            style={{ borderColor: '#E0D8CF' }}
          />
        </div>
      </div>

      {/* Przycisk przetwarzania */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={processCV}
          disabled={processing || files.length === 0}
          className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg text-white font-medium hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ backgroundColor: '#8B6F47' }}
        >
          {processing ? (
            <>
              <Clock size={20} className="animate-spin" />
              Przetwarzanie...
            </>
          ) : (
            <>
              <UserCheck size={20} />
              Przetwórz CV
            </>
          )}
        </button>

        {results && matchedCandidates.length > 0 && (
          <button
            onClick={sendEmailToTopCandidates}
            className="flex items-center gap-2 px-6 py-3 rounded-lg text-white font-medium hover:opacity-90 transition"
            style={{ backgroundColor: '#4A7C59' }}
          >
            <Send size={20} />
            Wyślij maile do top {topCandidatesCount}
          </button>
        )}
      </div>

      {/* Status przetwarzania */}
      {processing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-3">
            <Clock size={24} className="animate-spin text-blue-600" />
            <div>
              <p className="font-medium text-blue-900">Przetwarzanie w toku...</p>
              <p className="text-sm text-blue-700">
                Analizuję CV i dopasowuję do ofert pracy
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Wyniki */}
      {results && !processing && (
        <div className="space-y-6">
          {/* Podsumowanie */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow-sm p-6 border" style={{ borderColor: '#E0D8CF' }}>
              <div className="flex items-center gap-3 mb-2">
                <FileText size={24} style={{ color: '#8B6F47' }} />
                <span className="text-2xl font-bold" style={{ color: '#8B6F47' }}>
                  {results.length}
                </span>
              </div>
              <p className="text-sm" style={{ color: '#666' }}>Przetworzonych CV</p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border" style={{ borderColor: '#E0D8CF' }}>
              <div className="flex items-center gap-3 mb-2">
                <CheckCircle size={24} style={{ color: '#4A7C59' }} />
                <span className="text-2xl font-bold" style={{ color: '#4A7C59' }}>
                  {matchedCandidates.length}
                </span>
              </div>
              <p className="text-sm" style={{ color: '#666' }}>Dopasowanych</p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border" style={{ borderColor: '#E0D8CF' }}>
              <div className="flex items-center gap-3 mb-2">
                <XCircle size={24} style={{ color: '#DC2626' }} />
                <span className="text-2xl font-bold" style={{ color: '#DC2626' }}>
                  {rejectedCandidates.length}
                </span>
              </div>
              <p className="text-sm" style={{ color: '#666' }}>Odrzuconych</p>
            </div>
          </div>

          {/* Dopasowani kandydaci (pogrupowani po ofertach) */}
          {matchedCandidates.length > 0 && (
            <div>
              <h3 className="text-xl font-bold mb-4" style={{ color: '#8B6F47' }}>
                Dopasowani kandydaci
              </h3>

              {Object.keys(candidatesByJob).map(jobId => {
                const candidates = candidatesByJob[jobId];
                const jobTitle = candidates[0]?.bestMatch?.jobTitle;

                return (
                  <div key={jobId} className="mb-6">
                    <div className="flex items-center gap-2 mb-3">
                      <Briefcase size={20} style={{ color: '#8B6F47' }} />
                      <h4 className="text-lg font-semibold" style={{ color: '#2D2D2D' }}>
                        {jobTitle} ({jobId})
                      </h4>
                      <span className="text-sm px-2 py-1 rounded" style={{ backgroundColor: '#F5F1ED', color: '#666' }}>
                        {candidates.length} kandydatów
                      </span>
                    </div>

                    <div className="space-y-3">
                      {candidates.map((candidate, index) => {
                        const isTop = index < topCandidatesCount;
                        const emailSent = emailsSent.has(candidate.id);

                        return (
                          <div
                            key={candidate.id}
                            className={`rounded-lg p-4 border ${isTop ? 'border-2' : ''}`}
                            style={{
                              borderColor: isTop ? '#4A7C59' : '#E0D8CF',
                              backgroundColor: isTop ? '#F0F9F4' : '#FFFFFF'
                            }}
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <div className="flex items-center gap-2">
                                  <span className="font-semibold text-lg" style={{ color: '#2D2D2D' }}>
                                    #{index + 1}
                                  </span>
                                  <FileText size={20} style={{ color: '#8B6F47' }} />
                                  <span className="font-medium">{candidate.fileName}</span>
                                </div>
                                
                                {isTop && (
                                  <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                                    TOP {topCandidatesCount}
                                  </span>
                                )}
                                
                                {emailSent && (
                                  <div className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                    <Mail size={12} />
                                    Mail wysłany
                                  </div>
                                )}
                              </div>

                              <div className="text-right">
                                <div className="text-2xl font-bold" style={{ color: '#4A7C59' }}>
                                  {candidate.bestMatch.score}%
                                </div>
                                <div className="text-xs" style={{ color: '#666' }}>
                                  {candidate.bestMatch.totalScore}/{candidate.bestMatch.maxScore} pkt
                                </div>
                              </div>
                            </div>

                            {/* Dopasowane wymagania */}
                            <div className="mb-2">
                              <p className="text-sm font-medium mb-1" style={{ color: '#4A7C59' }}>
                                ✓ Spełnione wymagania ({candidate.bestMatch.matchedRequirements.length}):
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {candidate.bestMatch.matchedRequirements.map((req, i) => (
                                  <span
                                    key={i}
                                    className="px-2 py-1 rounded text-xs"
                                    style={{ backgroundColor: '#E8F5E9', color: '#2E7D32', border: '1px solid #A5D6A7' }}
                                  >
                                    {req.name} ({req.weight} pkt)
                                  </span>
                                ))}
                              </div>
                            </div>

                            {/* Niespełnione wymagania */}
                            {candidate.bestMatch.unmatchedRequirements.length > 0 && (
                              <div>
                                <p className="text-sm font-medium mb-1" style={{ color: '#DC2626' }}>
                                  ✗ Brakujące wymagania ({candidate.bestMatch.unmatchedRequirements.length}):
                                </p>
                                <div className="flex flex-wrap gap-2">
                                  {candidate.bestMatch.unmatchedRequirements.map((req, i) => (
                                    <span
                                      key={i}
                                      className="px-2 py-1 rounded text-xs"
                                      style={{ backgroundColor: '#FFEBEE', color: '#C62828', border: '1px solid #EF9A9A' }}
                                    >
                                      {req.name} ({req.weight} pkt)
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Inne dopasowania */}
                            {candidate.matches.length > 1 && (
                              <div className="mt-3 pt-3 border-t" style={{ borderColor: '#E0D8CF' }}>
                                <p className="text-xs font-medium mb-2" style={{ color: '#666' }}>
                                  Inne dopasowania:
                                </p>
                                <div className="flex flex-wrap gap-2">
                                  {candidate.matches.slice(1).map((match, i) => (
                                    <span
                                      key={i}
                                      className="px-2 py-1 rounded text-xs"
                                      style={{ backgroundColor: '#F5F1ED', color: '#8B6F47' }}
                                    >
                                      {match.jobTitle} - {match.score}%
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Odrzuceni kandydaci */}
          {rejectedCandidates.length > 0 && (
            <div>
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2" style={{ color: '#DC2626' }}>
                <AlertCircle size={24} />
                Odrzuceni kandydaci
              </h3>

              <div className="space-y-3">
                {rejectedCandidates.map(candidate => (
                  <div
                    key={candidate.id}
                    className="bg-red-50 rounded-lg p-4 border border-red-200"
                  >
                    <div className="flex items-center gap-3">
                      <FileText size={20} style={{ color: '#DC2626' }} />
                      <span className="font-medium">{candidate.fileName}</span>
                      <span className="text-sm" style={{ color: '#666' }}>
                        - nie pasuje do żadnej oferty
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}