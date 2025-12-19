import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectService } from '../services/api';

interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
  indicators_count: number;
}

const Projects: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [editingId, setEditingId] = useState<number | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

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
        await projectService.update(editingId, formData);
      } else {
        await projectService.create(formData);
      }
      setFormData({ name: '', description: '' });
      setEditingId(null);
      setShowForm(false);
      loadProjects();
    } catch (err) {
      console.error('Failed to save project', err);
    }
  };

  const handleEdit = (project: Project) => {
    setFormData({ name: project.name, description: project.description });
    setEditingId(project.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await projectService.delete(id);
        loadProjects();
      } catch (err) {
        console.error('Failed to delete project', err);
      }
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Projects</h1>
      
      <button onClick={() => setShowForm(!showForm)} style={{ marginBottom: '20px' }}>
        {showForm ? 'Cancel' : 'Create New Project'}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ccc' }}>
          <h3>{editingId ? 'Edit Project' : 'New Project'}</h3>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Name:</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              style={{ width: '100%', padding: '8px' }}
              required
            />
          </div>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Description:</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              style={{ width: '100%', padding: '8px', minHeight: '100px' }}
            />
          </div>
          <button type="submit" style={{ padding: '10px 20px', marginRight: '10px' }}>
            Save
          </button>
          <button type="button" onClick={() => { setShowForm(false); setEditingId(null); }} style={{ padding: '10px 20px' }}>
            Cancel
          </button>
        </form>
      )}

      <div>
        {projects.length === 0 ? (
          <p>No projects found. Create one to get started!</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ccc' }}>
                <th style={{ textAlign: 'left', padding: '10px' }}>Name</th>
                <th style={{ textAlign: 'left', padding: '10px' }}>Description</th>
                <th style={{ textAlign: 'left', padding: '10px' }}>Indicators</th>
                <th style={{ textAlign: 'left', padding: '10px' }}>Created</th>
                <th style={{ textAlign: 'left', padding: '10px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '10px' }}>{project.name}</td>
                  <td style={{ padding: '10px' }}>{project.description}</td>
                  <td style={{ padding: '10px' }}>{project.indicators_count}</td>
                  <td style={{ padding: '10px' }}>{new Date(project.created_at).toLocaleDateString()}</td>
                  <td style={{ padding: '10px' }}>
                    <button 
                      onClick={() => navigate(`/projects/${project.id}/evidence`)}
                      style={{ marginRight: '5px', backgroundColor: '#2196f3', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      Evidence Library
                    </button>
                    <button onClick={() => handleEdit(project)} style={{ marginRight: '5px' }}>Edit</button>
                    <button onClick={() => handleDelete(project.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Projects;
