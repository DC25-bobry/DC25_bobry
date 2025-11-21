import React, { useState, useRef } from 'react';
import {
  Upload,
  X,
  FileText,
  Mail,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  UserCheck,
  Briefcase,
  Send
} from 'lucide-react';

export default function CVPage() {
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [sendingEmails, setSendingEmails] = useState(false);
  const [results, setResults] = useState(null);
  const [topCandidatesCount, setTopCandidatesCount] = useState(3);
  const [emailsSent, setEmailsSent] = useState(new Set());
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (!e.target.files) return;

    const selectedFiles = Array.from(e.target.files).filter(
      (f) =>
        f.type === 'application/pdf' ||
        f.type ===
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );

    setFiles((prev) => [...prev, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFilesToBackend = async (filesToUpload, topN) => {
    const formData = new FormData();
    filesToUpload.forEach((file) => {
      formData.append('files', file);
    });

    let response;
    try {
      response = await fetch(
        `http://localhost:8000/upload?top_n=${encodeURIComponent(topN)}`,
        {
          method: 'POST',
          body: formData
        }
      );
    } catch (err) {
      console.error('❌ Błąd sieci przy wywołaniu /upload:', err);
      throw new Error('Nie udało się połączyć z backendem /upload');
    }

    const textBody = await response.text().catch(() => '');
    let data = null;

    try {
      data = textBody ? JSON.parse(textBody) : null;
    } catch (jsonErr) {
      console.error('❌ Nie udało się sparsować JSON z /upload:', jsonErr);
      console.error('Odpowiedź tekstowa z backendu:', textBody);
      throw new Error('Backend zwrócił nieprawidłowy JSON');
    }

    if (!response.ok) {
      console.error(
        `❌ Backend /upload zwrócił błąd ${response.status}:`,
        data || textBody
      );
      throw new Error(
        data?.detail || `Backend /upload zwrócił ${response.status}`
      );
    }

    console.log('✅ Odpowiedź /upload:', data);
    return data;
  };

  const processCV = async () => {
    if (files.length === 0) {
      alert('Dodaj przynajmniej jedno CV');
      return;
    }

    setProcessing(true);
    setResults(null);
    setEmailsSent(new Set());
    setError(null);

    try {
      const data = await uploadFilesToBackend(files, topCandidatesCount);
      setResults(data);
    } catch (err) {
      console.error(err);
      setError(
        err.message ||
          'Wystąpił błąd podczas przetwarzania CV. Sprawdź, czy backend na http://localhost:8000/upload działa poprawnie.'
      );
    } finally {
      setProcessing(false);
    }
  };

  const sendEmailToTopCandidates = async () => {
    if (!results || !results.jobs) return;

    setSendingEmails(true);
    setError(null);

    try {
      const payload = {
        top_n: topCandidatesCount,
        jobs: results.jobs,
        rejected: results.rejected || []
      };

      const response = await fetch(
        'http://localhost:8000/notifications/send-emails',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        }
      );

      const textBody = await response.text().catch(() => '');
      let data = null;

      try {
        data = textBody ? JSON.parse(textBody) : null;
      } catch (jsonErr) {
        console.error(
          '❌ Nie udało się sparsować JSON z /notifications:',
          jsonErr
        );
        console.error('Odpowiedź tekstowa z backendu:', textBody);
        throw new Error('Backend /notifications zwrócił nieprawidłowy JSON');
      }

      if (!response.ok) {
        console.error(
          `❌ Backend /notifications/send-emails zwrócił błąd ${response.status}:`,
          data || textBody
        );
        throw new Error(
          data?.detail ||
            `Backend /notifications/send-emails zwrócił ${response.status}`
        );
      }

      console.log('✅ Odpowiedź /notifications/send-emails:', data);

      const newEmailsSent = new Set(emailsSent);

      (results.jobs || []).forEach((job) => {
        (job.candidates || [])
          .filter((c) => c.is_top)
          .forEach((candidate) => {
            newEmailsSent.add(candidate.candidate_id || candidate.file_name);
          });
      });

      (results.rejected || []).forEach((candidate) => {
        if (candidate.candidate_id || candidate.file_name) {
          newEmailsSent.add(candidate.candidate_id || candidate.file_name);
        }
      });

      setEmailsSent(newEmailsSent);

      const sentAccept = data?.sent_accept ?? 0;
      const sentReject = data?.sent_reject ?? 0;

      alert(
        `Wysłano ${sentAccept} maili z informacją o zakwalifikowaniu i ${sentReject} maili z odmową.`
      );
    } catch (err) {
      console.error(err);
      setError(
        err.message ||
          'Nie udało się wysłać maili. Sprawdź, czy backend na http://localhost:8000/notifications/send-emails działa poprawnie.'
      );
    } finally {
      setSendingEmails(false);
    }
  };

  const totalCv = results?.total_cv ?? 0;
  const matchedCv = results?.matched_cv ?? 0;
  const rejectedCv = results?.rejected_cv ?? 0;

  const jobs = results?.jobs || [];
  const rejectedCandidates = results?.rejected || [];

  const anyMatched =
    jobs.reduce(
      (sum, job) => sum + (job.candidates ? job.candidates.length : 0),
      0
    ) > 0;

  const anyRejected = rejectedCandidates.length > 0;

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

      <div
        className="bg-white rounded-lg shadow-sm p-6 mb-6 border"
        style={{ borderColor: '#E0D8CF' }}
      >
        <h3
          className="text-lg font-semibold mb-4"
          style={{ color: '#8B6F47' }}
        >
          1. Przesyłanie CV
        </h3>

        <div
          className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50 transition"
          style={{ borderColor: '#E0D8CF' }}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload
            size={48}
            className="mx-auto mb-4"
            style={{ color: '#8B6F47' }}
          />
          <p
            className="text-lg font-medium mb-2"
            style={{ color: '#2D2D2D' }}
          >
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
                style={{
                  borderColor: '#E0D8CF',
                  backgroundColor: '#F5F1ED'
                }}
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

      <div
        className="bg-white rounded-lg shadow-sm p-6 mb-6 border"
        style={{ borderColor: '#E0D8CF' }}
      >
        <h3
          className="text-lg font-semibold mb-4"
          style={{ color: '#8B6F47' }}
        >
          2. Konfiguracja
        </h3>

        <div className="flex items-center gap-4">
          <label
            className="text-sm font-medium"
            style={{ color: '#2D2D2D' }}
          >
            Liczba najlepszych kandydatów (na ofertę):
          </label>
          <input
            type="number"
            min="1"
            max="20"
            value={topCandidatesCount}
            onChange={(e) =>
              setTopCandidatesCount(Math.max(1, Number(e.target.value) || 1))
            }
            className="w-24 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
            style={{ borderColor: '#E0D8CF' }}
          />
        </div>
      </div>

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

        {results && (anyMatched || anyRejected) && (
          <button
            onClick={sendEmailToTopCandidates}
            disabled={sendingEmails}
            className="flex items-center gap-2 px-6 py-3 rounded-lg text-white font-medium hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: '#4A7C59' }}
          >
            {sendingEmails ? (
              <>
                <Clock size={20} className="animate-spin" />
                Wysyłanie maili...
              </>
            ) : (
              <>
                <Send size={20} />
                Wyślij maile do top {topCandidatesCount} i odrzuconych
              </>
            )}
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {processing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-3">
            <Clock size={24} className="animate-spin text-blue-600" />
            <div>
              <p className="font-medium text-blue-900">
                Przetwarzanie w toku...
              </p>
              <p className="text-sm text-blue-700">
                Analizuję CV i dopasowuję do ofert pracy
              </p>
            </div>
          </div>
        </div>
      )}

      {results && !processing && (
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-4">
            <div
              className="bg-white rounded-lg shadow-sm p-6 border"
              style={{ borderColor: '#E0D8CF' }}
            >
              <div className="flex items-center gap-3 mb-2">
                <FileText size={24} style={{ color: '#8B6F47' }} />
                <span
                  className="text-2xl font-bold"
                  style={{ color: '#8B6F47' }}
                >
                  {totalCv}
                </span>
              </div>
              <p className="text-sm" style={{ color: '#666' }}>
                Przetworzonych CV
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
                  {matchedCv}
                </span>
              </div>
              <p className="text-sm" style={{ color: '#666' }}>
                Dopasowanych
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
                  {rejectedCv}
                </span>
              </div>
              <p className="text-sm" style={{ color: '#666' }}>
                Odrzuconych
              </p>
            </div>
          </div>

          {jobs.length > 0 && (
            <div>
              <h3
                className="text-xl font-bold mb-4"
                style={{ color: '#8B6F47' }}
              >
                Dopasowani kandydaci
              </h3>

              {jobs.map((job) => {
                const candidates = job.candidates || [];
                return (
                  <div key={job.job_id} className="mb-6">
                    <div className="flex items-center gap-2 mb-3">
                      <Briefcase size={20} style={{ color: '#8B6F47' }} />
                      <h4
                        className="text-lg font-semibold"
                        style={{ color: '#2D2D2D' }}
                      >
                        {job.job_title} ({job.job_id})
                      </h4>
                      <span
                        className="text-sm px-2 py-1 rounded"
                        style={{
                          backgroundColor: '#F5F1ED',
                          color: '#666'
                        }}
                      >
                        {candidates.length} kandydatów
                      </span>
                    </div>

                    <div className="space-y-3">
                      {candidates.map((candidate) => {
                        const key =
                          candidate.candidate_id || candidate.file_name;
                        const isTop = candidate.is_top;
                        const emailAlreadySent = emailsSent.has(key);

                        return (
                          <div
                            key={key}
                            className={`rounded-lg p-4 border ${
                              isTop ? 'border-2' : ''
                            }`}
                            style={{
                              borderColor: isTop ? '#4A7C59' : '#E0D8CF',
                              backgroundColor: isTop
                                ? '#F0F9F4'
                                : '#FFFFFF'
                            }}
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <div className="flex items-center gap-2">
                                  <span
                                    className="font-semibold text-lg"
                                    style={{ color: '#2D2D2D' }}
                                  >
                                    #{candidate.rank}
                                  </span>
                                  <FileText
                                    size={20}
                                    style={{ color: '#8B6F47' }}
                                  />
                                  <span className="font-medium">
                                    {candidate.file_name}
                                  </span>
                                </div>

                                {isTop && (
                                  <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                                    TOP {topCandidatesCount}
                                  </span>
                                )}

                                {emailAlreadySent && (
                                  <div className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                    <Mail size={12} />
                                    Mail wysłany
                                  </div>
                                )}
                              </div>

                              <div className="text-right">
                                <div
                                  className="text-2xl font-bold"
                                  style={{ color: '#4A7C59' }}
                                >
                                  {candidate.score}%
                                </div>
                                <div
                                  className="text-xs"
                                  style={{ color: '#666' }}
                                >
                                  {candidate.total_score}/
                                  {candidate.max_score} pkt
                                </div>
                              </div>
                            </div>

                            {candidate.matched_requirements &&
                              candidate.matched_requirements.length > 0 && (
                                <div className="mb-2">
                                  <p
                                    className="text-sm font-medium mb-1"
                                    style={{ color: '#4A7C59' }}
                                  >
                                    ✓ Spełnione wymagania (
                                    {candidate.matched_requirements.length}):
                                  </p>
                                  <div className="flex flex-wrap gap-2">
                                    {candidate.matched_requirements.map(
                                      (req, i) => (
                                        <span
                                          key={i}
                                          className="px-2 py-1 rounded text-xs"
                                          style={{
                                            backgroundColor: '#E8F5E9',
                                            color: '#2E7D32',
                                            border:
                                              '1px solid #A5D6A7'
                                          }}
                                        >
                                          {req.name} ({req.weight} pkt)
                                        </span>
                                      )
                                    )}
                                  </div>
                                </div>
                              )}

                            {candidate.unmatched_requirements &&
                              candidate.unmatched_requirements.length > 0 && (
                                <div>
                                  <p
                                    className="text-sm font-medium mb-1"
                                    style={{ color: '#DC2626' }}
                                  >
                                    ✗ Brakujące wymagania (
                                    {
                                      candidate.unmatched_requirements
                                        .length
                                    }
                                    ):
                                  </p>
                                  <div className="flex flex-wrap gap-2">
                                    {candidate.unmatched_requirements.map(
                                      (req, i) => (
                                        <span
                                          key={i}
                                          className="px-2 py-1 rounded text-xs"
                                          style={{
                                            backgroundColor: '#FFEBEE',
                                            color: '#C62828',
                                            border:
                                              '1px solid #EF9A9A'
                                          }}
                                        >
                                          {req.name} ({req.weight} pkt)
                                        </span>
                                      )
                                    )}
                                  </div>
                                </div>
                              )}

                            {candidate.other_matches &&
                              candidate.other_matches.length > 0 && (
                                <div
                                  className="mt-3 pt-3 border-t"
                                  style={{ borderColor: '#E0D8CF' }}
                                >
                                  <p
                                    className="text-xs font-medium mb-2"
                                    style={{ color: '#666' }}
                                  >
                                    Inne dopasowania:
                                  </p>
                                  <div className="flex flex-wrap gap-2">
                                    {candidate.other_matches.map(
                                      (match, i) => (
                                        <span
                                          key={i}
                                          className="px-2 py-1 rounded text-xs"
                                          style={{
                                            backgroundColor: '#F5F1ED',
                                            color: '#8B6F47'
                                          }}
                                        >
                                          {match.job_title} - {match.score}%
                                        </span>
                                      )
                                    )}
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

          {rejectedCandidates.length > 0 && (
            <div>
              <h3
                className="text-xl font-bold mb-4 flex items-center gap-2"
                style={{ color: '#DC2626' }}
              >
                <AlertCircle size={24} />
                Odrzuceni kandydaci
              </h3>

              <div className="space-y-3">
                {rejectedCandidates.map((candidate) => {
                  const key =
                    candidate.candidate_id || candidate.file_name;
                  return (
                    <div
                      key={key}
                      className="bg-red-50 rounded-lg p-4 border border-red-200"
                    >
                      <div className="flex items-center gap-3">
                        <FileText
                          size={20}
                          style={{ color: '#DC2626' }}
                        />
                        <span className="font-medium">
                          {candidate.file_name}
                        </span>
                        <span
                          className="text-sm"
                          style={{ color: '#666' }}
                        >
                          - nie pasuje do żadnej oferty
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
