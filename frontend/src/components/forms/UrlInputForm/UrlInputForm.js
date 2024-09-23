import React, { useState } from 'react';
import { formStyle, inputStyle, buttonStyle } from './UrlInputForm.styling';

function UrlInputForm({ onFormSubmit }) {
  const [url, setUrl] = useState('');
  const [label, setLabel] = useState('');
  const [urlError, setUrlError] = useState('');
  const [labelError, setLabelError] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setUrlError('');
    setLabelError('');
    setResponseMessage('');
    
    let hasError = false;
    
    if (!url) {
      setUrlError('URL is required');
      hasError = true;
    }
    
    if (!label) {
      setLabelError('Label is required');
      hasError = true;
    }
    
    if (hasError) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`http://127.0.0.1:5000/api/audio/storeaudio/${label}?url=${encodeURIComponent(url)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error from Flask:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response from Flask:', data);
      setResponseMessage(data.message);

      onFormSubmit();
      } catch (error) {
      console.error('Error:', error);
      setUrlError('An error occurred while submitting.');
    }finally {
      setLoading(false);
    }
  };

  return (
    <div>
        <form onSubmit={handleSubmit} style={formStyle}>
            <label>Enter video URL:
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder={urlError || "Enter URL"}
                style={{ ...inputStyle, borderColor: urlError ? 'red' : 'black' }}
              />
            </label>
            <br/>
            <label>Enter label (POI, NPOI, Multiple):
              <input
                type="text"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder={labelError || "Enter Label"}
                style={{ ...inputStyle, borderColor: labelError ? 'red' : 'black' }}
              />
            </label>
            <br/>
            <button type="submit" style={buttonStyle} disabled={loading}>
            {loading ? 'Submitting...' : 'Submit'}
            </button>
        </form>
        {responseMessage && (
          <div style={{ marginTop: '20px', color: 'green' }}>
            {responseMessage}
          </div>
        )}
    </div>
  );
}

export default UrlInputForm;