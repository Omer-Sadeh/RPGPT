import React from 'react';
import './ProgressBar.css';

function ProgressBar({precentage, color='aliceblue'} : {precentage: number, color?: string}) {
    return (
        <div className="progress-container">
            <div className="progress-bar" style={{width: `${precentage}%`, background: color}}></div>
        </div>
    );
}

export default ProgressBar;