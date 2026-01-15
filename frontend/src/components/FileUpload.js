import React from 'react';

const FileUpload = ({ file, onFileChange, onUpload, loading }) => {
    return (
        <div className="upload-section glass-card">
            <div className="file-input-wrapper">
                <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={onFileChange}
                    className="file-input"
                    id="file-upload"
                />
                <label htmlFor="file-upload" className={`file-label ${file ? 'file-selected' : ''}`}>
                    <div className="icon-wrapper">
                        {file ? '📄' : '☁️'}
                    </div>
                    <span className="file-name">
                        {file ? file.name : 'Choose PDF or Image file'}
                    </span>
                    <span className="file-instruction">
                        {file ? 'Click to change' : 'or drag and drop here'}
                    </span>
                </label>
            </div>

            <button
                onClick={onUpload}
                disabled={loading || !file}
                className={`upload-btn ${loading ? 'loading' : ''}`}
            >
                {loading ? (
                    <span className="loading-spinner"></span>
                ) : (
                    <>
                        <span>Analyze Report</span>
                        <span className="btn-icon">✨</span>
                    </>
                )}
            </button>
        </div>
    );
};

export default FileUpload;
