import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectService, indicatorService, evidenceService, complianceService } from '../services/api';
import EvidencePanel from '../components/EvidencePanel';

interface Project {
  id: number;
  name: string;
  google_drive_linked: boolean;
}

interface Indicator {
  id: number;
  requirement: string;
  evidence_mode: string;
  evidence_count: number;
  status: string;
  section_name: string;
  standard_name: string;
}

const EvidenceLibrary: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [selectedIndicator, setSelectedIndicator] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      loadProject();
      loadIndicators();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      const response = await projectService.get(Number(projectId));
      setProject(response.data);
    } catch (err) {
      console.error('Failed to load project', err);
    }
  };

  const loadIndicators = async () => {
    try {
      setLoading(true);
      const response = await indicatorService.getAll(Number(projectId));
      setIndicators(response.data);
    } catch (err) {
      console.error('Failed to load indicators', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading...</div>;
  }

  if (!project) {
    return <div style={{ padding: '20px' }}>Project not found</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Evidence Library - {project.name}</h1>
          <p style={{ color: '#666', marginTop: '5px' }}>
            {project.google_drive_linked ? '✓ Google Drive Linked' : '⚠ Google Drive Not Linked'}
          </p>
        </div>
        <button onClick={() => navigate('/projects')} style={{ padding: '10px 20px' }}>
          Back to Projects
        </button>
      </div>

      {!project.google_drive_linked && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#fff3cd', 
          border: '1px solid #ffc107', 
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <strong>Google Drive Not Linked:</strong> Please link Google Drive to enable file uploads.
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px' }}>
        <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '4px', border: '1px solid #ddd' }}>
          <h3 style={{ marginTop: 0 }}>Indicators</h3>
          <div style={{ maxHeight: '70vh', overflowY: 'auto' }}>
            {indicators.length === 0 ? (
              <p>No indicators found</p>
            ) : (
              indicators.map((indicator) => (
                <div
                  key={indicator.id}
                  onClick={() => setSelectedIndicator(indicator.id)}
                  style={{
                    padding: '10px',
                    marginBottom: '8px',
                    cursor: 'pointer',
                    backgroundColor: selectedIndicator === indicator.id ? '#e3f2fd' : '#f5f5f5',
                    border: selectedIndicator === indicator.id ? '2px solid #2196f3' : '1px solid #ddd',
                    borderRadius: '4px',
                  }}
                >
                  <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '5px' }}>
                    {indicator.requirement.substring(0, 50)}...
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {indicator.section_name} / {indicator.standard_name}
                  </div>
                  <div style={{ fontSize: '12px', marginTop: '5px' }}>
                    <span style={{ 
                      padding: '2px 6px', 
                      borderRadius: '3px',
                      backgroundColor: indicator.status === 'compliant' ? '#4caf50' : 
                                      indicator.status === 'in_process' ? '#ff9800' : '#f44336',
                      color: 'white',
                      fontSize: '11px'
                    }}>
                      {indicator.status}
                    </span>
                    <span style={{ marginLeft: '8px', fontSize: '11px' }}>
                      {indicator.evidence_count} evidence
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '4px', border: '1px solid #ddd' }}>
          {selectedIndicator ? (
            <EvidencePanel 
              indicatorId={selectedIndicator}
              projectId={Number(projectId)}
              onEvidenceAdded={loadIndicators}
            />
          ) : (
            <div style={{ textAlign: 'center', color: '#999', padding: '40px' }}>
              Select an indicator to view and manage evidence
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EvidenceLibrary;

