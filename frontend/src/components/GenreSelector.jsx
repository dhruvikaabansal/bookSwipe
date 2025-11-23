import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './GenreSelector.css';

const GENRES = [
    "Fiction", "Non-Fiction", "Mystery", "Sci-Fi", "Fantasy",
    "Romance", "Thriller", "Biography", "History", "Self-Help",
    "Business", "Young Adult", "Classics", "Horror", "Poetry"
];

const GenreSelector = ({ user, onFinish }) => {
    const [selectedGenres, setSelectedGenres] = useState([]);
    const navigate = useNavigate();

    const toggleGenre = (genre) => {
        if (selectedGenres.includes(genre)) {
            setSelectedGenres(selectedGenres.filter(g => g !== genre));
        } else {
            setSelectedGenres([...selectedGenres, genre]);
        }
    };

    const handleContinue = () => {
        // In a real app, save these to the backend
        console.log("Selected Genres:", selectedGenres);
        onFinish(selectedGenres);
        navigate('/');
    };

    return (
        <div className="genre-container">
            <h1>What do you like to read?</h1>
            <p>Select a few genres to help us find your next favorite book.</p>

            <div className="genre-grid">
                {GENRES.map(genre => (
                    <button
                        key={genre}
                        className={`genre-btn ${selectedGenres.includes(genre) ? 'selected' : ''}`}
                        onClick={() => toggleGenre(genre)}
                    >
                        {genre}
                    </button>
                ))}
            </div>

            <button
                className="btn-continue"
                disabled={selectedGenres.length === 0}
                onClick={handleContinue}
            >
                Start Swiping
            </button>
        </div>
    );
};

export default GenreSelector;
