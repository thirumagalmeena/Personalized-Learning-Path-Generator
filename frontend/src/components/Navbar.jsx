import { useNavigate } from 'react-router-dom';
import { FiCompass, FiStar, FiLogOut } from 'react-icons/fi';

export default function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  const token = localStorage.getItem('token');
  if (!token) return null;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <FiCompass size={22} />
        Learning Path
      </div>
      <div className="navbar-links">
        <button className="btn btn-ghost" onClick={() => navigate('/home')}>
          <FiCompass size={16} /> Home
        </button>
        <button className="btn btn-ghost" onClick={() => navigate('/my-skills')}>
          <FiStar size={16} /> Skills
        </button>
        <button className="btn btn-ghost" onClick={() => navigate('/saved-roadmaps')}>
          <FiCompass size={16} /> Roadmap
        </button>
        <button className="btn btn-ghost" onClick={() => navigate('/my-reviews')}>
          <FiStar size={16} /> My Reviews
        </button>
        <button className="btn btn-ghost" onClick={handleLogout}>
          <FiLogOut size={16} /> Logout
        </button>
      </div>
    </nav>
  );
}
