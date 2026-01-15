import React, { useState } from 'react';

// Sub-component for visualizations
const HealthGauge = ({ test, value }) => {
    // Basic logic to determine status based on string matching or simple parsing
    // In a real app, we'd need structured data from backend
    let status = 'normal';
    let width = '50%';

    // Very naive heuristic for demonstration
    // Ideally backend returns: { value: 140, status: 'high', range: '70-100' }
    const numValue = parseFloat(value);

    if (!isNaN(numValue)) {
        if (test.includes('cholesterol') && numValue > 200) { status = 'danger'; width = '100%'; }
        else if (test.includes('glucose') && numValue > 140) { status = 'warning'; width = '80%'; }
        else if (test.includes('hemoglobin') && (numValue < 12 || numValue > 18)) { status = 'warning'; width = '20%'; }
        else if (test.includes('blood_pressure')) {
            // specialized logic for BP usually needed
            status = 'normal'; width = '50%';
        }
    }

    return (
        <div className="health-meter-container">
            <div className="meter-label">
                <span>Low</span>
                <span>Normal</span>
                <span>High</span>
            </div>
            <div className="health-bar-bg">
                <div className={`health-bar-fill ${status}`} style={{ width }}></div>
            </div>
            <span className={`status-badge ${status}`}>
                {status === 'danger' ? 'High Risk' : status === 'warning' ? 'Attention' : 'Normal'}
            </span>
        </div>
    );
};

const Results = ({ result }) => {
    const [speaking, setSpeaking] = useState(false);

    if (!result) return null;

    const { explanation, lab_values } = result;

    const handleSpeak = () => {
        if (speaking) {
            window.speechSynthesis.cancel();
            setSpeaking(false);
            return;
        }

        const textToRead = `Overall Summary. ${explanation.summary}. Your test results are as follows. ${Object.entries(lab_values).map(([k, v]) => `${k} is ${v}`).join('. ')}`;
        const utterance = new SpeechSynthesisUtterance(textToRead);
        utterance.onend = () => setSpeaking(false);
        setSpeaking(true);
        window.speechSynthesis.speak(utterance);
    };

    const handlePrint = () => {
        window.print();
    };

    return (
        <div className="results-section fade-in">
            <div className="section-header">
                <h2>📋 Your Report Summary</h2>
                <div className="underline"></div>
            </div>

            <div className="accessibility-controls">
                <button
                    onClick={handleSpeak}
                    className={`action-btn ${speaking ? 'speaking' : ''}`}
                >
                    <span>{speaking ? '🔇 Stop Reading' : '🔊 Listen to Report'}</span>
                </button>
                <button onClick={handlePrint} className="action-btn">
                    <span>🖨️ Save/Print</span>
                </button>
            </div>

            {explanation.summary && (
                <div className="result-card summary-card glass-card">
                    <div className="card-header">
                        <h3>Overall Summary</h3>
                    </div>
                    <p>{explanation.summary}</p>
                </div>
            )}

            {Object.keys(lab_values).length > 0 && (
                <div className="result-card values-card glass-card">
                    <div className="card-header">
                        <h3>Test Values Found</h3>
                    </div>
                    <div className="values-grid">
                        {Object.entries(lab_values).map(([test, value]) => (
                            <div key={test} className="value-item">
                                <span className="test-name">{test.charAt(0).toUpperCase() + test.slice(1)}</span>
                                <span className="test-value">{value}</span>
                                <HealthGauge test={test} value={value} />
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {explanation.test_explanations && Object.keys(explanation.test_explanations).length > 0 && (
                <div className="result-card explanations-card glass-card">
                    <div className="card-header">
                        <h3>What These Tests Mean</h3>
                    </div>
                    <div className="explanations-list">
                        {Object.entries(explanation.test_explanations).map(([test, expl]) => (
                            <div key={test} className="explanation-item">
                                <h4>{test.charAt(0).toUpperCase() + test.slice(1)}</h4>
                                <p>{expl}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {explanation.lifestyle_tips && explanation.lifestyle_tips.length > 0 && (
                <div className="result-card tips-card glass-card">
                    <div className="card-header">
                        <h3>💡 Healthy Living Tips</h3>
                    </div>
                    <ul className="tips-list">
                        {explanation.lifestyle_tips.map((tip, index) => (
                            <li key={index}>{tip}</li>
                        ))}
                    </ul>
                </div>
            )}

            {explanation.when_to_see_doctor && (
                <div className="result-card doctor-card glass-card warning">
                    <div className="card-header">
                        <h3>⚠️ Important Note</h3>
                    </div>
                    <p>{explanation.when_to_see_doctor}</p>
                </div>
            )}
        </div>
    );
};

export default Results;
