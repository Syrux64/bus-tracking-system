import React, { useEffect, useState } from 'react';
import supabase from './db';
import './App.css';

const App = () => {
  const [busData, setBusData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch from db
  const fetchBusData = async () => {
    try {
      const { data, error } = await supabase
        .from('CapturedData')
        .select('bus_number, bus_stop');

      if (error) throw error;

      setBusData(data);
    } catch (error) {
      console.error('Error fetching bus data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBusData();
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    fetchBusData();
  };

  return (
    <div className='container'>
      <h1>Bus Information</h1>
      <button onClick={handleRefresh} className='refresh-button'>
        Refresh
      </button>
      { loading ? (
        <p>Loading...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Bus Number</th>
              <th>Bus Stop</th>
            </tr>
          </thead>
          <tbody>
            {busData.map((row) => (
              <tr key={row.id}>
                <td>{row.bus_number}</td>
                <td>{row.bus_stop}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default App;
