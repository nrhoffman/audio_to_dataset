import React, { useEffect, useState } from 'react';
import { UrlInputForm } from '../../components/forms';
import { OriginalAudioTable } from '../../components/tables';
import { WavTextBox } from '../../components/textboxes';
import { AudioEditingTool } from '../../components/tools';
import { editingContainer, tableEditingContainer } from './AudioEditing.styling';

function AudioEditing() {
  const [tableData, setTableData] = useState([]);
  const [selectedType, setSelectedType] = useState('N/A');
  const [selectedUrl, setSelectedUrl] = useState('N/A');
  const [selectedRow, setSelectedRow] = useState(null);
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

  const handleRowClick = (item, index) => {
    setSelectedType(item.type || 'N/A');
    setSelectedUrl(item.url || 'N/A');
    setSelectedRow(index);
  };

  return (
    <div>
        <h1>Audio Editing</h1>
        <UrlInputForm onFormSubmit={fetchData}/>
        <div id = "table-editing-container" style={tableEditingContainer}>
            <OriginalAudioTable data={tableData} onRowClick={handleRowClick} selectedRow={selectedRow}/>
            <div id = "editing-container" style={editingContainer}>
                <WavTextBox boxType={"Type: "} initialText={selectedType}/>
                <WavTextBox boxType={"Url: "} initialText={selectedUrl}/>
            </div>
        </div>
    </div>
  );
}

export default AudioEditing;