import React from 'react';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from './components/Header';
import Contents from './components/Contents';
import Footer from './components/Footer';
import Text from './components/Text';
import MultiStepForm from './components/MultiStepForm';

function App() {
  const containerStyle = {
    display: 'flex',
    flexDirection: 'row', // Ensure components are aligned horizontally
    gap: '0px',
  };

  return (
    <Router> {/* ✅ Wrap the entire app in Router */}
      <Header />
      
      <div style={containerStyle}>  
        <Text />
        <Contents />
      </div>

      {/* ✅ MultiStepForm must be inside Routes */}
      <div style={{ marginTop: '40px', display: 'flex', justifyContent: 'center' }}>
        <Routes>
          <Route path="/*" element={<MultiStepForm />} />
        </Routes>
      </div>

      <Footer />
    </Router>
  );
}

export default App;
