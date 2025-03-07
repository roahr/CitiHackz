import React from 'react';

function Footer() {
  return (
    <footer style={{
      backgroundColor: '#222', 
      color: 'white', 
      padding: '20px 50px', 
      textAlign: 'center',
      marginTop: '50px'
    }}>
      
      {/* Footer Content */}
      <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        
        {/* About Section */}
        <div style={{ maxWidth: '300px', textAlign: 'left' }}>
          <h3>About FinTrust</h3>
          <p style={{ fontSize: '14px', color: '#bbb' }}>
            FinTrust uses AI-powered insights to evaluate business creditworthiness, 
            helping lenders make smarter financial decisions.
          </p>
        </div>

        {/* Quick Links */}
        <div style={{ textAlign: 'left' }}>
          <h3>Quick Links</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {["Dashboard", "Reports", "Loan Requests"].map((link, index) => (
              <li key={index}>
                <a href="#" style={{ color: '#bbb', textDecoration: 'none' }}>{link}</a>
              </li>
            ))}
          </ul>
        </div>

        {/* Legal */}
        <div style={{ textAlign: 'left' }}>
          <h3>Legal</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {["Privacy Policy", "Terms of Service", "Regulations"].map((link, index) => (
              <li key={index}>
                <a href="#" style={{ color: '#bbb', textDecoration: 'none' }}>{link}</a>
              </li>
            ))}
          </ul>
        </div>

        {/* Contact Section */}
        <div style={{ textAlign: 'left' }}>
          <h3>Contact Us</h3>
          <p style={{ fontSize: '14px', color: '#bbb' }}>Email: support@fintrust.com</p>
        </div>

      </div>

      {/* Copyright */}
      <div style={{ marginTop: '20px', fontSize: '12px', color: '#bbb' }}>
        © {new Date().getFullYear()} FinTrust. All Rights Reserved.
      </div>

    </footer>
  );
}

export default Footer;
