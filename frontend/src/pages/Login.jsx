import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../firebase';
import {
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword
} from "firebase/auth";
import './Login.css';

const Login = ({ onLogin }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState('');

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  const handleGoogleLogin = async () => {
    const provider = new GoogleAuthProvider();
    try {
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      onLogin({ id: user.uid, token: await user.getIdToken(), name: user.displayName, photo: user.photoURL });
      navigate('/');
    } catch (error) {
      console.error("Google Login Error:", error);
      setError("Google Login failed. Try again.");
    }
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      let userCredential;
      if (isSignUp) {
        userCredential = await createUserWithEmailAndPassword(auth, email, password);
      } else {
        userCredential = await signInWithEmailAndPassword(auth, email, password);
      }
      const user = userCredential.user;
      onLogin({ id: user.uid, token: await user.getIdToken(), name: user.email });
      navigate('/');
    } catch (error) {
      console.error("Email Auth Error:", error);
      setError(error.message);
    }
  };

  const handleDemoLogin = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/demo-login`, {
        method: 'POST',
      });
      const data = await response.json();
      onLogin({ id: data.user_id, token: data.token, name: "Demo User" });
      navigate('/');
    } catch (error) {
      console.error('Login failed:', error);
      setError('Demo login failed. Is the backend running?');
    }
  };

  return (
    <div className="login-container">
      <div className="login-glass-card">
        <div className="logo-section">
          <div className="logo-icon">📚</div>
          <h1>Welcome to BookSwipe</h1>
          <p className="subtitle">Discover your next favorite read with AI.</p>
        </div>

        <form onSubmit={handleEmailLogin} className="login-form">
          <div className="input-group">
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="glass-input"
            />
          </div>
          <div className="input-group">
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="glass-input"
            />
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button type="submit" className="btn-primary">
            {isSignUp ? 'Create Account' : 'Sign In'}
          </button>
        </form>

        <div className="auth-divider">
          <span>or continue with</span>
        </div>

        <div className="social-actions">
          <button className="btn-social google" onClick={handleGoogleLogin}>
            <span className="icon">G</span> Google
          </button>
          <button className="btn-social demo" onClick={handleDemoLogin}>
            <span className="icon">👤</span> Demo User
          </button>
        </div>

        <div className="toggle-auth">
          <div className="toggle-auth-content">
            <p className="toggle-text">{isSignUp ? "Already have an account?" : "New to BookSwipe?"}</p>
            <button className="btn-link" onClick={() => setIsSignUp(!isSignUp)}>
              {isSignUp ? 'Sign In' : 'Create Account'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
