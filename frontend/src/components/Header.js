import React from 'react';

const Header = ({ isDarkMode, toggleTheme }) => {
    return (
        <header className="app-header">
            <div className="header-top">
                <div className="logo-container">
                    <span className="logo-icon">🏥</span>
                    <h1>Medical Report Simplifier</h1>
                </div>

                <button
                    onClick={toggleTheme}
                    className="theme-toggle"
                    aria-label="Toggle Dark Mode"
                >
                    {isDarkMode ? '☀️' : '🌙'}
                </button>
            </div>
            <p className="header-subtitle">Upload your lab report to get easy-to-understand explanations</p>
        </header>
    );
};

export default Header;
