import { useState, useEffect, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { getIssue, updateIssue } from "../api/issues";
import { getProject } from "../api/projects";
import { listComments, createComment } from "../api/comments";
import { useAuth } from "../context/AuthContext";
import toast from "react-hot-toast";

const STATUSES = ["open", "in_progress", "resolved", "closed"];
const PRIORITIES = ["low", "medium", "high", "critical"];
const STATUS_LABELS = { open: "Open", in_progress: "In Progress", resolved: "Resolved", closed: "Closed" };
const PRIORITY_COLORS = { low: "#6b7280", medium: "#f59e0b", high: "#f97316", critical: "#ef4444" };

export default function IssueDetailPage() {
  const { issueId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [issue, setIssue] = useState(null);
  const [project, setProject] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentBody, setCommentBody] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const fetchIssue = useCallback(async () => {
    try {
      const res = await getIssue(issueId);
      setIssue(res.data);
      const projRes = await getProject(res.data.project_id);
      setProject(projRes.data);
    } catch {
      toast.error("Failed to load issue");
      navigate("/");
    } finally {
      setLoading(false);
    }
  }, [issueId, navigate]);

  const fetchComments = useCallback(async () => {
    try {
      const res = await listComments(issueId);
      setComments(res.data);
    } catch {
      // silent
    }
  }, [issueId]);

  useEffect(() => { fetchIssue(); fetchComments(); }, [fetchIssue, fetchComments]);

  const membership = project?.members?.find((m) => m.user_id === user?.id);
  const isMaintainer = membership?.role === "maintainer";

  const handleStatusChange = async (newStatus) => {
    try {
      const res = await updateIssue(issueId, { status: newStatus });
      setIssue(res.data);
      toast.success("Status updated");
    } catch (err) {
      toast.error(err.response?.data?.detail?.message || "Failed to update status");
    }
  };

  const handleAssigneeChange = async (assigneeId) => {
    try {
      const res = await updateIssue(issueId, { assignee_id: assigneeId || null });
      setIssue(res.data);
      toast.success("Assignee updated");
    } catch (err) {
      toast.error(err.response?.data?.detail?.message || "Failed to update assignee");
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentBody.trim()) { toast.error("Comment cannot be empty"); return; }
    setSubmitting(true);
    try {
      await createComment(issueId, { body: commentBody });
      setCommentBody("");
      fetchComments();
      toast.success("Comment added");
    } catch {
      toast.error("Failed to add comment");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (!issue) return null;

  return (
    <div className="page">
      <div className="breadcrumb">
        <Link to="/">Projects</Link> / <Link to={`/projects/${issue.project_id}`}>{project?.name}</Link> / <span>{issue.title}</span>
      </div>

      <div className="issue-detail">
        <div className="issue-detail-main">
          <h1>{issue.title}</h1>

          <div className="issue-badges">
            <span className={`badge badge-status badge-${issue.status}`}>{STATUS_LABELS[issue.status]}</span>
            <span className="badge badge-priority" style={{ borderColor: PRIORITY_COLORS[issue.priority] }}>{issue.priority}</span>
          </div>

          {issue.description && (
            <div className="issue-description">
              <p>{issue.description}</p>
            </div>
          )}

          {/* Comments Section */}
          <div className="comments-section">
            <h2>Comments ({comments.length})</h2>
            {comments.length === 0 ? (
              <p className="text-muted">No comments yet.</p>
            ) : (
              <div className="comments-list">
                {comments.map((c) => (
                  <div key={c.id} className="comment">
                    <div className="comment-header">
                      <strong>{c.author.name}</strong>
                      <span className="text-muted">{new Date(c.created_at).toLocaleString()}</span>
                    </div>
                    <p className="comment-body">{c.body}</p>
                  </div>
                ))}
              </div>
            )}
            <form onSubmit={handleAddComment} className="comment-form">
              <textarea
                value={commentBody}
                onChange={(e) => setCommentBody(e.target.value)}
                placeholder="Add a comment..."
                rows={3}
              />
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? "Posting..." : "Add Comment"}
              </button>
            </form>
          </div>
        </div>

        {/* Sidebar */}
        <div className="issue-detail-sidebar">
          <div className="sidebar-section">
            <h3>Details</h3>
            <div className="sidebar-field">
              <label>Status</label>
              {isMaintainer ? (
                <select value={issue.status} onChange={(e) => handleStatusChange(e.target.value)}>
                  {STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                </select>
              ) : (
                <span className={`badge badge-status badge-${issue.status}`}>{STATUS_LABELS[issue.status]}</span>
              )}
            </div>
            <div className="sidebar-field">
              <label>Priority</label>
              <span className="badge badge-priority" style={{ borderColor: PRIORITY_COLORS[issue.priority] }}>{issue.priority}</span>
            </div>
            <div className="sidebar-field">
              <label>Assignee</label>
              {isMaintainer ? (
                <select value={issue.assignee_id || ""} onChange={(e) => handleAssigneeChange(e.target.value ? Number(e.target.value) : null)}>
                  <option value="">Unassigned</option>
                  {project?.members?.map((m) => <option key={m.user_id} value={m.user_id}>{m.user_name}</option>)}
                </select>
              ) : (
                <span>{issue.assignee?.name || "Unassigned"}</span>
              )}
            </div>
            <div className="sidebar-field">
              <label>Reporter</label>
              <span>{issue.reporter?.name}</span>
            </div>
            <div className="sidebar-field">
              <label>Created</label>
              <span>{new Date(issue.created_at).toLocaleString()}</span>
            </div>
            <div className="sidebar-field">
              <label>Updated</label>
              <span>{new Date(issue.updated_at).toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
