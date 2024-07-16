import React from 'react';
import './MessageScreen.css';
import ClipLoader from "react-spinners/ClipLoader";

export function LoadingScreen() {
    return (
        <div className="messageScreen">
            <ClipLoader
                color={"aliceblue"}
                loading={true}
                size={150}
                aria-label="Loading Spinner"
                data-testid="loader"
            />
        </div>
    );
}

function MessageScreen({message} : {message: string}) {
    return (
        <div className="messageScreen">
            {message}
        </div>
    );
}

export default MessageScreen;