import React from 'react';

export default function ImageLoader({bytes, alt, className}: { bytes: string, alt: string, className: string }) {
    if (bytes !== "") {
        return <img src={`data:image/png;base64,${bytes}`} alt={alt} className={className} />;
    } else {
        return <img src="./default.png" alt={alt} className={className} />;
    }
}