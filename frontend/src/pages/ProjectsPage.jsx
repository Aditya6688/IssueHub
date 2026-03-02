import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { listProjects, createProject } from "../api/projects";
import toast from "react-hot-toast";

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: "", key: "", description: "" });
  const [creating, setCreating] = useState(false);

  const fetchProjects = async () => {
    try {
      const res = await listProjects();
      setProjects(res.data);
    } catch {
      toast.error("Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchProjects(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.name || !form.key) {
      toast.error("Name and key are required");
      return;
    }
    setCreating(true);
    try {
      await createProject(form);
      toast.success("Project created!");
      setShowModal(false);
      setForm({ name: "", key: "", description: "" });
      fetchProjects();
    } catch (err) {
      toast.error(err.response?.data?.detail?.message || "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div className="loading">Loading projects...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Projects</h1>
        <button onClick={() => setShowModal(true)} className="btn btn-primary">New Project</button>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state">
          <p>No projects yet. Create your first project to get started.</p>
        </div>
      ) : (
        <div className="project-grid">
          {projects.map((p) => (
            <Link key={p.id} to={`/projects/${p.id}`} className="project-card">
              <div className="project-card-key">{p.key}</div>
              <h3>{p.name}</h3>
              <p>{p.description || "No description"}</p>
              <span className="project-card-date">
                Created {new Date(p.created_at).toLocaleDateString()}
              </span>
            </Link>
          ))}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create Project</h2>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Project Name</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="My Project" />
              </div>
              <div className="form-group">
                <label>Key (2-10 chars, uppercase)</label>
                <input type="text" value={form.key} onChange={(e) => setForm({ ...form, key: e.target.value.toUpperCase() })} placeholder="PROJ" maxLength={10} />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="What is this project about?" rows={3} />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn">Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? "Creating..." : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
