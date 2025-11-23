import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './History.css';

const History = ({ user }) => {
    const [history, setHistory] = useState([]);
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/user/${user.id}/history`);
                const data = await response.json();
                setHistory(data);
            } catch (error) {
                console.error('Error fetching history:', error);
            }
        };
        fetchHistory();
    }, [user.id]);

    return (
        <div className="history-container">
            <div className="header">
                <Link to="/" className="back-link">← Back to Swipe</Link>
                <h1>Your History</h1>
            </div>

            <div className="history-list">
                {history.length === 0 ? (
                    <p>No history yet. Start swiping!</p>
                ) : (
                    history.map((item, index) => (
                        <div key={index} className={`history-item ${item.action}`}>
                            <span className="book-id">Book #{item.book_id}</span>
                            <span className="action-badge">
                                {item.action === 'like' ? '❤️ Liked' : '⛔ Passed'}
                            </span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default History;
