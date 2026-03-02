import { useState, useEffect, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { getProject, addMember } from "../api/projects";
import { listIssues, createIssue, deleteIssue } from "../api/issues";
import { useAuth } from "../context/AuthContext";
import toast from "react-hot-toast";

const STATUSES = ["open", "in_progress", "resolved", "closed"];
const PRIORITIES = ["low", "medium", "high", "critical"];
const STATUS_LABELS = { open: "Open", in_progress: "In Progress", resolved: "Resolved", closed: "Closed" };
const PRIORITY_COLORS = { low: "#6b7280", medium: "#f59e0b", high: "#f97316", critical: "#ef4444" };

export default function ProjectDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [issues, setIssues] = useState({ items: [], total: 0, page: 1, page_size: 10 });
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ q: "", status: "", priority: "", assignee: "", sort: "created_at", order: "desc", page: 1 });
  const [showNewIssue, setShowNewIssue] = useState(false);
  const [showAddMember, setShowAddMember] = useState(false);
  const [issueForm, setIssueForm] = useState({ title: "", description: "", priority: "medium", assignee_id: "" });
  const [memberForm, setMemberForm] = useState({ email: "", role: "member" });
  const [submitting, setSubmitting] = useState(false);

  const currentMembership = project?.members?.find((m) => m.user_id === user?.id);
  const isMaintainer = currentMembership?.role === "maintainer";

  const fetchProject = useCallback(async () => {
    try {
      const res = await getProject(id);
      setProject(res.data);
    } catch {
      toast.error("Failed to load project");
      navigate("/");
    }
  }, [id, navigate]);

  const fetchIssues = useCallback(async () => {
    try {
      const params = { page: filters.page, page_size: 10, sort: filters.sort, order: filters.order };
      if (filters.q) params.q = filters.q;
      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;
      if (filters.assignee) params.assignee = filters.assignee;
      const res = await listIssues(id, params);
      setIssues(res.data);
    } catch {
      toast.error("Failed to load issues");
    } finally {
      setLoading(false);
    }
  }, [id, filters]);

  useEffect(() => { fetchProject(); }, [fetchProject]);
  useEffect(() => { fetchIssues(); }, [fetchIssues]);

  const handleCreateIssue = async (e) => {
    e.preventDefault();
    if (!issueForm.title) { toast.error("Title is required"); return; }
    setSubmitting(true);
    try {
      const payload = { ...issueForm };
      if (!payload.assignee_id) delete payload.assignee_id;
      else payload.assignee_id = Number(payload.assignee_id);
      await createIssue(id, payload);
      toast.success("Issue created!");
      setShowNewIssue(false);
      setIssueForm({ title: "", description: "", priority: "medium", assignee_id: "" });
      fetchIssues();
    } catch (err) {
      toast.error(err.response?.data?.detail?.message || "Failed to create issue");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    if (!memberForm.email) { toast.error("Email is required"); return; }
    setSubmitting(true);
    try {
      await addMember(id, memberForm);
      toast.success("Member added!");
      setShowAddMember(false);
      setMemberForm({ email: "", role: "member" });
      fetchProject();
    } catch (err) {
      toast.error(err.response?.data?.detail?.message || "Failed to add member");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteIssue = async (issueId) => {
    if (!window.confirm("Delete this issue?")) return;
    try {
      await deleteIssue(issueId);
      toast.success("Issue deleted");
      fetchIssues();
    } catch {
      toast.error("Failed to delete issue");
    }
  };

  const totalPages = Math.ceil(issues.total / issues.page_size);

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="page">
      <div className="breadcrumb">
        <Link to="/">Projects</Link> / <span>{project?.name}</span>
      </div>

      <div className="page-header">
        <div>
          <h1>{project?.name} <span className="badge badge-key">{project?.key}</span></h1>
          <p className="text-muted">{project?.description}</p>
        </div>
        <div className="header-actions">
          {isMaintainer && <button onClick={() => setShowAddMember(true)} className="btn">Add Member</button>}
          <button onClick={() => setShowNewIssue(true)} className="btn btn-primary">New Issue</button>
        </div>
      </div>

      {/* Members */}
      <div className="members-bar">
        <span className="members-label">Members:</span>
        {project?.members?.map((m) => (
          <span key={m.user_id} className={`member-chip ${m.role === "maintainer" ? "maintainer" : ""}`}>
            {m.user_name} {m.role === "maintainer" && "(M)"}
          </span>
        ))}
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <input
          type="text"
          placeholder="Search issues..."
          value={filters.q}
          onChange={(e) => setFilters({ ...filters, q: e.target.value, page: 1 })}
          className="filter-search"
        />
        <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}>
          <option value="">All Statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
        </select>
        <select value={filters.priority} onChange={(e) => setFilters({ ...filters, priority: e.target.value, page: 1 })}>
          <option value="">All Priorities</option>
          {PRIORITIES.map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
        </select>
        <select value={filters.assignee} onChange={(e) => setFilters({ ...filters, assignee: e.target.value, page: 1 })}>
          <option value="">All Assignees</option>
          {project?.members?.map((m) => <option key={m.user_id} value={m.user_id}>{m.user_name}</option>)}
        </select>
        <select value={`${filters.sort}-${filters.order}`} onChange={(e) => {
          const [sort, order] = e.target.value.split("-");
          setFilters({ ...filters, sort, order, page: 1 });
        }}>
          <option value="created_at-desc">Newest First</option>
          <option value="created_at-asc">Oldest First</option>
          <option value="priority-desc">Priority (High-Low)</option>
          <option value="priority-asc">Priority (Low-High)</option>
          <option value="status-asc">Status (A-Z)</option>
          <option value="status-desc">Status (Z-A)</option>
        </select>
      </div>

      {/* Issues List */}
      {issues.items.length === 0 ? (
        <div className="empty-state"><p>No issues found.</p></div>
      ) : (
        <div className="issues-list">
          {issues.items.map((issue) => (
            <div key={issue.id} className="issue-row">
              <Link to={`/issues/${issue.id}`} className="issue-link">
                <div className="issue-title-row">
                  <span className="issue-title">{issue.title}</span>
                  <span className={`badge badge-status badge-${issue.status}`}>{STATUS_LABELS[issue.status]}</span>
                </div>
                <div className="issue-meta">
                  <span className="badge badge-priority" style={{ borderColor: PRIORITY_COLORS[issue.priority] }}>
                    {issue.priority}
                  </span>
                  <span>by {issue.reporter?.name}</span>
                  {issue.assignee && <span>assigned to {issue.assignee.name}</span>}
                  <span>{new Date(issue.created_at).toLocaleDateString()}</span>
                </div>
              </Link>
              {(isMaintainer || issue.reporter_id === user?.id) && (
                <button className="btn btn-sm btn-danger" onClick={() => handleDeleteIssue(issue.id)}>Delete</button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button disabled={filters.page <= 1} onClick={() => setFilters({ ...filters, page: filters.page - 1 })} className="btn btn-sm">Prev</button>
          <span>Page {filters.page} of {totalPages}</span>
          <button disabled={filters.page >= totalPages} onClick={() => setFilters({ ...filters, page: filters.page + 1 })} className="btn btn-sm">Next</button>
        </div>
      )}

      {/* New Issue Modal */}
      {showNewIssue && (
        <div className="modal-overlay" onClick={() => setShowNewIssue(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>New Issue</h2>
            <form onSubmit={handleCreateIssue}>
              <div className="form-group">
                <label>Title</label>
                <input type="text" value={issueForm.title} onChange={(e) => setIssueForm({ ...issueForm, title: e.target.value })} placeholder="Issue title" />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea value={issueForm.description} onChange={(e) => setIssueForm({ ...issueForm, description: e.target.value })} placeholder="Describe the issue..." rows={4} />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Priority</label>
                  <select value={issueForm.priority} onChange={(e) => setIssueForm({ ...issueForm, priority: e.target.value })}>
                    {PRIORITIES.map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Assignee</label>
                  <select value={issueForm.assignee_id} onChange={(e) => setIssueForm({ ...issueForm, assignee_id: e.target.value })}>
                    <option value="">Unassigned</option>
                    {project?.members?.map((m) => <option key={m.user_id} value={m.user_id}>{m.user_name}</option>)}
                  </select>
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowNewIssue(false)} className="btn">Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>{submitting ? "Creating..." : "Create Issue"}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Member Modal */}
      {showAddMember && (
        <div className="modal-overlay" onClick={() => setShowAddMember(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Add Member</h2>
            <form onSubmit={handleAddMember}>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={memberForm.email} onChange={(e) => setMemberForm({ ...memberForm, email: e.target.value })} placeholder="user@example.com" />
              </div>
              <div className="form-group">
                <label>Role</label>
                <select value={memberForm.role} onChange={(e) => setMemberForm({ ...memberForm, role: e.target.value })}>
                  <option value="member">Member</option>
                  <option value="maintainer">Maintainer</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowAddMember(false)} className="btn">Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>{submitting ? "Adding..." : "Add Member"}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
