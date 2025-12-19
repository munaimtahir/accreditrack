import React, { useState, useEffect } from 'react';
import { indicatorService, projectService } from '../services/api';

interface Indicator {
  id: number;
  project: number;
  area: string;
  regulation_or_standard: string;
  requirement: string;
  evidence_required: string;
  responsible_person: string;
  frequency: string;
  status: string;
  assigned_to: string;
  evidence_count: number;
}

/**
 * The Indicators page component.
 *
 * This component provides a CRUD (Create, Read, Update, Delete) interface
 * for managing compliance indicators. It displays a list of indicators and
 * includes a form for creating and editing them.
 *
 * @state
 * @property {Indicator[]} indicators - The list of indicators fetched from the API.
 * @property {any[]} projects - The list of projects for the project selection dropdown.
 * @property {boolean} showForm - Toggles the visibility of the create/edit form.
 * @property {object} formData - Holds the data for the indicator being created or edited.
 * @property {number|null} editingId - The ID of the indicator currently being edited, or null if creating a new one.
 *
 * @returns {React.ReactElement} The rendered Indicators page.
 */
const Indicators: React.FC = () => {
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    project: '',
    area: '',
    regulation_or_standard: '',
    requirement: '',
    evidence_required: '',
    responsible_person: '',
    frequency: '',
    status: 'pending',
    assigned_to: '',
  });
  const [editingId, setEditingId] = useState<number | null>(null);

  useEffect(() => {
    loadIndicators();
    loadProjects();
  }, []);

  const loadIndicators = async () => {
    try {
      const response = await indicatorService.getAll();
      setIndicators(response.data);
    } catch (err) {
      console.error('Failed to load indicators', err);
    }
  };

  const loadProjects = async () => {
    try {
      const response = await projectService.getAll();
      setProjects(response.data);
    } catch (err) {
      console.error('Failed to load projects', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await indicatorService.update(editingId, formData);
      } else {
        await indicatorService.create(formData);
      }
      resetForm();
      loadIndicators();
    } catch (err) {
      console.error('Failed to save indicator', err);
    }
  };

  const resetForm = () => {
    setFormData({
      project: '',
      area: '',
      regulation_or_standard: '',
      requirement: '',
      evidence_required: '',
      responsible_person: '',
      frequency: '',
      status: 'pending',
      assigned_to: '',
    });
    setEditingId(null);
    setShowForm(false);
  };

  const handleEdit = (indicator: Indicator) => {
    setFormData({
      project: indicator.project.toString(),
      area: indicator.area,
      regulation_or_standard: indicator.regulation_or_standard,
      requirement: indicator.requirement,
      evidence_required: indicator.evidence_required,
      responsible_person: indicator.responsible_person,
      frequency: indicator.frequency,
      status: indicator.status,
      assigned_to: indicator.assigned_to,
    });
    setEditingId(indicator.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this indicator?')) {
      try {
        await indicatorService.delete(id);
        loadIndicators();
      } catch (err) {
        console.error('Failed to delete indicator', err);
      }
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Indicators</h1>
      
      <button onClick={() => setShowForm(!showForm)} style={{ marginBottom: '20px' }}>
        {showForm ? 'Cancel' : 'Create New Indicator'}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ccc' }}>
          <h3>{editingId ? 'Edit Indicator' : 'New Indicator'}</h3>
          
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Project:</label>
            <select
              value={formData.project}
              onChange={(e) => setFormData({ ...formData, project: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
              required
            >
              <option value="">Select a project</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Area:</label>
            <input
              type="text"
              value={formData.area}
              onChange={(e) => setFormData({ ...formData, area: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Regulation/Standard:</label>
            <input
              type="text"
              value={formData.regulation_or_standard}
              onChange={(e) => setFormData({ ...formData, regulation_or_standard: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Requirement:</label>
            <textarea
              value={formData.requirement}
              onChange={(e) => setFormData({ ...formData, requirement: e.target.value })}
              style={{ width: '100%', padding: '8px', minHeight: '80px' }}
              required
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Evidence Required:</label>
            <textarea
              value={formData.evidence_required}
              onChange={(e) => setFormData({ ...formData, evidence_required: e.target.value })}
              style={{ width: '100%', padding: '8px', minHeight: '60px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Responsible Person:</label>
            <input
              type="text"
              value={formData.responsible_person}
              onChange={(e) => setFormData({ ...formData, responsible_person: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Frequency:</label>
            <input
              type="text"
              value={formData.frequency}
              onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Status:</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
            >
              <option value="pending">Pending</option>
              <option value="partial">Partial</option>
              <option value="compliant">Compliant</option>
              <option value="non_compliant">Non-Compliant</option>
            </select>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Assigned To:</label>
            <input
              type="text"
              value={formData.assigned_to}
              onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <button type="submit" style={{ padding: '10px 20px', marginRight: '10px' }}>
            Save
          </button>
          <button type="button" onClick={resetForm} style={{ padding: '10px 20px' }}>
            Cancel
          </button>
        </form>
      )}

      <div>
        {indicators.length === 0 ? (
          <p>No indicators found. Create one to get started!</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #ccc' }}>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Requirement</th>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Area</th>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Status</th>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Responsible</th>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Evidence</th>
                  <th style={{ textAlign: 'left', padding: '10px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {indicators.map((indicator) => (
                  <tr key={indicator.id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '10px' }}>{indicator.requirement.substring(0, 100)}...</td>
                    <td style={{ padding: '10px' }}>{indicator.area}</td>
                    <td style={{ padding: '10px' }}>{indicator.status}</td>
                    <td style={{ padding: '10px' }}>{indicator.responsible_person}</td>
                    <td style={{ padding: '10px' }}>{indicator.evidence_count}</td>
                    <td style={{ padding: '10px' }}>
                      <button onClick={() => handleEdit(indicator)} style={{ marginRight: '5px' }}>Edit</button>
                      <button onClick={() => handleDelete(indicator.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Indicators;
