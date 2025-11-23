import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './SwipeDeck.css';

const SwipeDeck = ({ user, genres }) => {
    const [recommendations, setRecommendations] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(false);
    const [swipeCount, setSwipeCount] = useState(0);
    const navigate = useNavigate();
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

    const fetchRecommendations = async () => {
        setLoading(true);
        try {
            const genreParam = genres && genres.length > 0 ? `&genres=${encodeURIComponent(genres.join(','))}` : '';
            const response = await fetch(`${API_BASE_URL}/recommend?user_id=${user.id}&n=10${genreParam}`);
            const data = await response.json();
            setRecommendations(data);
            setCurrentIndex(0);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRecommendations();
    }, [user.id]);

    const handleSwipe = async (action) => {
        if (currentIndex >= recommendations.length) return;

        const book = recommendations[currentIndex];
        const endpoint = action === 'like' ? 'like' : 'pass';

        // Optimistic UI update
        const nextIndex = currentIndex + 1;
        setCurrentIndex(nextIndex);

        // Update swipe count and check for threshold
        const newCount = swipeCount + 1;
        setSwipeCount(newCount);

        if (newCount >= 10) {
            navigate('/recommendations');
            return;
        }

        // API Call
        try {
            await fetch(`${API_BASE_URL}/user/${user.id}/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.id, book_id: book.book_id }),
            });
        } catch (error) {
            console.error(`Error sending ${action}:`, error);
        }

        // Fetch more if near end
        if (nextIndex >= recommendations.length - 2) {
            if (nextIndex >= recommendations.length) {
                fetchRecommendations();
            }
        }
    };

    if (loading && recommendations.length === 0) {
        return <div className="deck-container">Loading books...</div>;
    }

    if (currentIndex >= recommendations.length) {
        return (
            <div className="deck-container empty-state">
                <h2>No more books!</h2>
                <button className="btn-refresh" onClick={fetchRecommendations}>Refresh</button>
            </div>
        );
    }

    const currentBook = recommendations[currentIndex];

    return (
        <div className="deck-container">
            <div className="card-stack">
                <div className="card glass-card">
                    <div className="card-content">
                        <div className="book-cover-placeholder">
                            <span className="cover-initial">{currentBook.title[0]}</span>
                        </div>

                        <div className="book-info">
                            <div className="book-header">
                                <h2>{currentBook.title}</h2>
                                <h3>{currentBook.author}</h3>
                            </div>



                            <div className="tags">
                                {currentBook.genres.split(' ').slice(0, 3).map((g, i) => (
                                    <span key={i} className="tag">{g}</span>
                                ))}
                            </div>

                            {currentBook.description && currentBook.description !== '<no description>' && (
                                <p className="description">{currentBook.description}</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <div className="actions">
                <button className="btn-action btn-pass" onClick={() => handleSwipe('pass')}>
                    <span className="icon">✕</span>
                </button>
                <button className="btn-action btn-like" onClick={() => handleSwipe('like')}>
                    <span className="icon">♥</span>
                </button>
            </div>
        </div>
    );
};

export default SwipeDeck;
