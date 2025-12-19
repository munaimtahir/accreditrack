import React, { useState, useEffect } from 'react';
import { indicatorService, evidenceService, complianceService, aiService } from '../services/api';

interface Evidence {
  id: number;
  title: string;
  evidence_type: string;
  evidence_type_display: string;
  google_drive_file_url?: string;
  evidence_text?: string;
  period_start?: string;
  period_end?: string;
  uploaded_by_name?: string;
  uploaded_at: string;
}

interface Indicator {
  id: number;
  requirement: string;
  evidence_mode: string;
  evidence_required: string;
  normalized_frequency?: string;
}

interface ComplianceStatus {
  status: string;
  evidence_count: number;
  expected_count?: number;
  missing_periods: Array<{ start: string; end: string }>;
  last_submitted?: string;
  next_due_date?: string;
}

interface Props {
  indicatorId: number;
  projectId: number;
  onEvidenceAdded: () => void;
}

const EvidencePanel: React.FC<Props> = ({ indicatorId, projectId, onEvidenceAdded }) => {
  const [indicator, setIndicator] = useState<Indicator | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [compliance, setCompliance] = useState<ComplianceStatus | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [evidenceType, setEvidenceType] = useState<'file' | 'text_declaration' | 'hybrid'>('file');
  const [formData, setFormData] = useState({
    title: '',
    evidence_text: '',
    period_start: '',
    period_end: '',
    notes: '',
  });
  const [file, setFile] = useState<File | null>(null);
  const [aiSuggestions, setAiSuggestions] = useState<any>(null);
  const [showAIPanel, setShowAIPanel] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIndicator();
    loadEvidence();
    loadCompliance();
  }, [indicatorId]);

  const loadIndicator = async () => {
    try {
      const response = await indicatorService.get(indicatorId);
      setIndicator(response.data);
    } catch (err) {
      console.error('Failed to load indicator', err);
    }
  };

  const loadEvidence = async () => {
    try {
      const response = await evidenceService.getAll(indicatorId);
      setEvidence(response.data);
    } catch (err) {
      console.error('Failed to load evidence', err);
    }
  };

  const loadCompliance = async () => {
    try {
      const response = await complianceService.getComplianceStatus(indicatorId);
      setCompliance(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load compliance', err);
      setLoading(false);
    }
  };

  const handleSubmitEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = new FormData();
      submitData.append('indicator', indicatorId.toString());
      submitData.append('title', formData.title);
      submitData.append('evidence_type', evidenceType);
      submitData.append('notes', formData.notes);

      if (evidenceType === 'text_declaration' || evidenceType === 'hybrid') {
        submitData.append('evidence_text', formData.evidence_text);
      }

      if (formData.period_start) {
        submitData.append('period_start', formData.period_start);
      }
      if (formData.period_end) {
        submitData.append('period_end', formData.period_end);
      }

      if (file && (evidenceType === 'file' || evidenceType === 'hybrid')) {
        submitData.append('file', file);
      }

      await evidenceService.create(submitData);
      
      // Reset form
      setFormData({
        title: '',
        evidence_text: '',
        period_start: '',
        period_end: '',
        notes: '',
      });
      setFile(null);
      setShowAddForm(false);
      
      // Reload data
      loadEvidence();
      loadCompliance();
      onEvidenceAdded();
    } catch (err: any) {
      alert('Failed to submit evidence: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleAskAI = async () => {
    try {
      const response = await aiService.getEvidenceAssistance(indicatorId, 'suggestions');
      setAiSuggestions(response.data);
      setShowAIPanel(true);
    } catch (err) {
      console.error('Failed to get AI suggestions', err);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!indicator) {
    return <div>Indicator not found</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ marginTop: 0 }}>{indicator.requirement}</h2>
        <p style={{ color: '#666', marginBottom: '10px' }}>{indicator.evidence_required}</p>
        
        {compliance && (
          <div style={{ 
            padding: '10px', 
            backgroundColor: compliance.status === 'compliant' ? '#e8f5e9' : 
                            compliance.status === 'in_process' ? '#fff3e0' : '#ffebee',
            borderRadius: '4px',
            marginBottom: '15px'
          }}>
            <strong>Compliance Status:</strong> {compliance.status} 
            ({compliance.evidence_count} / {compliance.expected_count || 'N/A'} evidence)
            {compliance.missing_periods.length > 0 && (
              <div style={{ marginTop: '5px', fontSize: '14px' }}>
                Missing periods: {compliance.missing_periods.length}
              </div>
            )}
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <button 
            onClick={() => setShowAddForm(!showAddForm)}
            style={{ padding: '8px 16px', backgroundColor: '#2196f3', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            {showAddForm ? 'Cancel' : 'Add Evidence'}
          </button>
          <button 
            onClick={handleAskAI}
            style={{ padding: '8px 16px', backgroundColor: '#9c27b0', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Ask AI for Help
          </button>
        </div>
      </div>

      {showAIPanel && aiSuggestions && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#f3e5f5', 
          borderRadius: '4px', 
          marginBottom: '20px',
          border: '1px solid #9c27b0'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h3 style={{ margin: 0 }}>AI Suggestions</h3>
            <button onClick={() => setShowAIPanel(false)}>×</button>
          </div>
          {aiSuggestions.suggestions && Array.isArray(aiSuggestions.suggestions) && (
            <ul>
              {aiSuggestions.suggestions.map((suggestion: any, idx: number) => (
                <li key={idx} style={{ marginBottom: '8px' }}>
                  <strong>{suggestion.title}:</strong> {suggestion.description}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {showAddForm && (
        <form onSubmit={handleSubmitEvidence} style={{ 
          padding: '20px', 
          backgroundColor: '#f9f9f9', 
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <h3>Add Evidence</h3>
          
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Evidence Type:</label>
            <select
              value={evidenceType}
              onChange={(e) => setEvidenceType(e.target.value as any)}
              style={{ width: '100%', padding: '8px' }}
            >
              <option value="file">File Upload</option>
              <option value="text_declaration">Text Declaration (Physical Evidence)</option>
              <option value="hybrid">Hybrid (Text + File)</option>
            </select>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Title:</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
              required
            />
          </div>

          {(evidenceType === 'text_declaration' || evidenceType === 'hybrid') && (
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                Evidence Text (Physical Evidence Declaration):
              </label>
              <textarea
                value={formData.evidence_text}
                onChange={(e) => setFormData({ ...formData, evidence_text: e.target.value })}
                style={{ width: '100%', padding: '8px', minHeight: '100px' }}
                placeholder="e.g., Hard files are stored in a locked cabinet in the Principal Office."
                required={evidenceType === 'text_declaration'}
              />
              {evidenceType === 'text_declaration' && (
                <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
                  ⚠ Physical evidence declared – subject to inspection
                </small>
              )}
            </div>
          )}

          {(evidenceType === 'file' || evidenceType === 'hybrid') && (
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>File:</label>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                style={{ width: '100%', padding: '8px' }}
                required={evidenceType === 'file'}
              />
            </div>
          )}

          {indicator.normalized_frequency && (
            <>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Period Start:</label>
                <input
                  type="date"
                  value={formData.period_start}
                  onChange={(e) => setFormData({ ...formData, period_start: e.target.value })}
                  style={{ width: '100%', padding: '8px' }}
                />
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Period End:</label>
                <input
                  type="date"
                  value={formData.period_end}
                  onChange={(e) => setFormData({ ...formData, period_end: e.target.value })}
                  style={{ width: '100%', padding: '8px' }}
                />
              </div>
            </>
          )}

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Notes:</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              style={{ width: '100%', padding: '8px', minHeight: '60px' }}
            />
          </div>

          <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#4caf50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Submit Evidence
          </button>
        </form>
      )}

      <div>
        <h3>Evidence List ({evidence.length})</h3>
        {evidence.length === 0 ? (
          <p>No evidence submitted yet</p>
        ) : (
          <div>
            {evidence.map((ev) => (
              <div key={ev.id} style={{ 
                padding: '15px', 
                marginBottom: '10px', 
                backgroundColor: '#f9f9f9', 
                borderRadius: '4px',
                border: '1px solid #ddd'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 5px 0' }}>{ev.title}</h4>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                      Type: {ev.evidence_type_display} | 
                      Uploaded by: {ev.uploaded_by_name} | 
                      {new Date(ev.uploaded_at).toLocaleDateString()}
                    </div>
                    {ev.evidence_text && (
                      <div style={{ 
                        padding: '10px', 
                        backgroundColor: '#fff3cd', 
                        borderRadius: '4px',
                        marginBottom: '8px',
                        fontSize: '14px'
                      }}>
                        <strong>Physical Evidence:</strong> {ev.evidence_text}
                      </div>
                    )}
                    {ev.google_drive_file_url && (
                      <a 
                        href={ev.google_drive_file_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ color: '#2196f3', textDecoration: 'none' }}
                      >
                        View File →
                      </a>
                    )}
                  </div>
                  <button 
                    onClick={async () => {
                      if (window.confirm('Delete this evidence?')) {
                        try {
                          await evidenceService.delete(ev.id);
                          loadEvidence();
                          loadCompliance();
                          onEvidenceAdded();
                        } catch (err) {
                          alert('Failed to delete evidence');
                        }
                      }
                    }}
                    style={{ padding: '5px 10px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default EvidencePanel;

