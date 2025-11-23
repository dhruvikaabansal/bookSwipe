import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import SwipeDeck from './components/SwipeDeck';
import History from './pages/History';
import GenreSelector from './components/GenreSelector';
import Recommendations from './pages/Recommendations';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [hasOnboarded, setHasOnboarded] = useState(false);

  const [selectedGenres, setSelectedGenres] = useState([]);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleOnboardingFinish = (genres) => {
    setHasOnboarded(true);
    setSelectedGenres(genres);
  };

  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />

          <Route
            path="/onboarding"
            element={
              user ? (
                <GenreSelector user={user} onFinish={handleOnboardingFinish} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />

          <Route
            path="/"
            element={
              user ? (
                hasOnboarded ? <SwipeDeck user={user} genres={selectedGenres} /> : <Navigate to="/onboarding" />
              ) : (
                <Navigate to="/login" />
              )
            }
          />

          <Route
            path="/recommendations"
            element={user ? <Recommendations user={user} /> : <Navigate to="/login" />}
          />

          <Route
            path="/history"
            element={user ? <History user={user} /> : <Navigate to="/login" />}
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
