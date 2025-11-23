import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Recommendations.css';

const Recommendations = ({ user }) => {
    const [books, setBooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchTopPicks = async () => {
            try {
                // Fetch more precise recommendations for the "Buy" list
                const response = await fetch(`${API_BASE_URL}/recommend?user_id=${user.id}&n=6`);
                const data = await response.json();
                setBooks(data);
            } catch (error) {
                console.error('Error fetching top picks:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchTopPicks();
    }, [user.id]);

    const handleRate = async (bookId, action) => {
        // Optimistic remove
        setBooks(books.filter(b => b.book_id !== bookId));

        try {
            await fetch(`${API_BASE_URL}/user/${user.id}/${action}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.id, book_id: bookId }),
            });
        } catch (error) {
            console.error(`Error sending ${action}:`, error);
        }
    };

    if (loading) return <div className="rec-container">Loading your curated list...</div>;

    return (
        <div className="rec-container">
            <header className="rec-header">
                <h1>Your Curated Collection</h1>
                <p>Based on your recent swipes, we think you'll love these.</p>
            </header>

            <div className="rec-grid">
                {books.map(book => (
                    <div key={book.book_id} className="rec-card glass-card">
                        <div className="rec-cover">
                            <span className="rec-initial">{book.title[0]}</span>
                            <div className="rec-score">
                                {(book.score * 100).toFixed(0)}% Match
                            </div>
                        </div>
                        <div className="rec-info">
                            <h3>{book.title}</h3>
                            <h4>{book.author}</h4>
                            <div className="rec-actions">
                                <button className="btn-buy">Buy Now</button>
                                <div className="rate-actions">
                                    <button className="btn-icon-small pass" onClick={() => handleRate(book.book_id, 'pass')}>✕</button>
                                    <button className="btn-icon-small like" onClick={() => handleRate(book.book_id, 'like')}>♥</button>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <button className="btn-back" onClick={() => navigate('/')}>
                <span className="icon">↩</span> Keep Swiping
            </button>
        </div>
    );
};

export default Recommendations;
