import React from 'react';
import { rowStyle, tableStyle, highlightedRowStyle } from './OriginalAudioTable.styling';

function OriginalAudioTable({ data, onRowClick, selectedRow }) {
    if (data === "Loading data...") {
        return <p>Loading data...</p>;
    }

    const isEmpty = data.length === 0 || (data.length === 1 && data[0].url === "" && data[0].type === "");
    const rowsToShow = isEmpty ? 10 : Math.max(data.length, 10);

    // Create an array for the rows, including empty rows if needed
    const rows = Array.from({ length: rowsToShow }, (_, index) => {
        const item = data[index] || { type: '', url: '' };
        const isSelected = selectedRow === index;
        const currentRowStyle = isSelected ? highlightedRowStyle : rowStyle;

        return (
            <tr 
                key={index} 
                onClick={() => onRowClick(item, index)} 
                style={currentRowStyle}
            >
                <td>{item.type}</td>
                <td>
                    {item.url ? (
                        <a href={item.url} target="_blank" rel="noopener noreferrer">
                            {item.url}
                        </a>
                    ) : (
                        <span>&nbsp;</span>
                    )}
                </td>
            </tr>
        );
    });

    return (
        <table style={tableStyle}>
            <thead>
                <tr>
                    <th style={rowStyle}>Type</th>
                    <th style={rowStyle}>Url</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    );
}

export default OriginalAudioTable