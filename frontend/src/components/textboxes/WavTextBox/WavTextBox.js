import React, { useState, useEffect } from 'react';

const WavTextBox = ({ boxType, initialText }) => {
  const [text, setText] = useState(initialText || 'N/A');

    useEffect(() => {
      if (initialText) {
          setText(initialText);
      }
  }, [initialText]);
  
    return (
      <div>
        <p>{ boxType } {text}</p>
      </div>
    );
  };

export default WavTextBox