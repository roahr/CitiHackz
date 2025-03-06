import React from 'react';
import logo from './fintrust-logo.png';
import searchIcon from './search.png';
import profileIcon from './profile.png';
import bellIcon from './bell.png';

function Header() {
  return (
    <header style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '99%',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      backgroundColor: 'white',
      padding: '10px 20px',
      color: 'black',
      boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.1)',
      zIndex: 1000
    }}>
      
      {/* Left: Logo & System Name */}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <img src={logo} alt="FinTrust Logo" style={{ height: '60px', marginRight: '10px' }} />
      </div>

      {/* Center: Navigation Links */}
      <nav>
        {["Dashboard", "Reports", "Loan Requests"].map((text, index) => (
          <a key={index} href="#" style={{ 
            color: 'black', 
            margin: '0 15px', 
            textDecoration: 'none', 
            fontWeight: 'bold' 
          }}>
            {text}
          </a>
        ))}
      </nav>

      {/* Right: Search & User Icons */}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <input 
          type="text" 
          placeholder="Search by Business ID..." 
          style={{
            padding: '5px 10px',
            borderRadius: '20px',
            border: '1px solid #ccc',
            marginRight: '15px'
          }} 
        />
        <img src={searchIcon} alt="Search" style={{ height: '25px', marginRight: '15px', cursor: 'pointer' }} />
        <img src={bellIcon} alt="Notifications" style={{ height: '25px', marginRight: '15px', cursor: 'pointer' }} />
        <img src={profileIcon} alt="Profile" style={{ height: '30px', cursor: 'pointer' }} />
      </div>
      
    </header>
  );
}

export default Header;
