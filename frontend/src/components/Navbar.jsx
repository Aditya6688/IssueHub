import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logoutUser } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logoutUser();
    navigate("/login");
  };

  if (!user) return null;

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/" className="navbar-brand">IssueHub</Link>
        <Link to="/">Projects</Link>
      </div>
      <div className="navbar-right">
        <span className="navbar-user">{user.name}</span>
        <button onClick={handleLogout} className="btn btn-sm">Logout</button>
      </div>
    </nav>
  );
}
