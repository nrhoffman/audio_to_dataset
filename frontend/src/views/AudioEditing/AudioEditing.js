import React, { useEffect, useState } from 'react';
import { UrlInputForm } from '../../components/forms';
import { OriginalAudioTable } from '../../components/tables';

function DataEditing() {
  const [tableData, setTableData] = useState([]);
  const fetchData = async () => {
    setTableData("Loading data...");
    try {
      const response = await fetch('http://127.0.0.1:5000/api/audio/getoriginalwavs');
      const data = await response.json();
      console.log(data);
      setTableData(data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div>
        <h1>Audio Editing</h1>
        <UrlInputForm onFormSubmit={fetchData}/>
        <OriginalAudioTable data={tableData}/>
    </div>
  );
}

export default DataEditing;