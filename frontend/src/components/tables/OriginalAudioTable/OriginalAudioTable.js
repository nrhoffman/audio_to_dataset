import React from 'react';

function OriginalAudioTable({ data }) {
    if (data === "Loading data..."){
        return <p>Loading data...</p>
    }

    if (data.length === 0 || (data.length === 1 && data[0].url === "" && data[0].type === "")) {
        return <p>No data available</p>;
    }

    return (
        <table>
        <thead>
            <tr>
            <th>Type</th>
            <th>Url</th>
            </tr>
        </thead>
        <tbody>
            {data.map((item, index) => (
                <tr key={index}>
                    <td>{item.type}</td>
                    <td>
                        <a href={item.url} target="_blank" rel="noopener noreferrer">
                            {item.url}
                        </a>
                    </td>
                </tr>
                ))}
        </tbody>
        </table>
    );
}

export default OriginalAudioTable