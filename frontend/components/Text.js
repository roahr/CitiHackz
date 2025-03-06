import React from 'react';

function Contents() {
  return (
    <main style={{ 
      padding: '60px', 
      textAlign: 'left', 
      backgroundColor: 'white', 
      flex: '1' 
    }}>
      
      {/* Introduction Section */}
      <section style={{ marginBottom: '50px' }}>
        <h1 style={{ 
          color: 'black', 
          fontSize: '2.8em', 
          fontWeight: 'bold', 
          marginBottom: '15px' 
        }}>
          AI-Powered Credit Scoring for Smarter Lending Decisions
        </h1>
        
        <p style={{ 
          color: '#555', 
          fontSize: '1.2em', 
          lineHeight: '1.6', 
          maxWidth: '800px' 
        }}>
          FinTrust analyzes businesses' creditworthiness using AI-driven insights
          and alternative financial data. Get real-time risk assessments and make 
          informed lending decisions with confidence.
        </p>

        <button style={{
          backgroundColor: '#007BFF', 
          color: 'white',
          padding: '14px 28px',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '18px',
          fontWeight: 'bold',
          marginTop: '25px',
          transition: 'background 0.3s'
        }}
        onMouseOver={(e) => e.target.style.backgroundColor = '#0056b3'}
        onMouseOut={(e) => e.target.style.backgroundColor = '#007BFF'}>
          Calculate your Credit Score
        </button>
      </section>

      {/* Key Features Section */}
      <section style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: '30px', 
        marginTop: '50px'
      }}>
        
        {/* Feature 1 */}
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <img src="https://cdn-icons-png.flaticon.com/128/2910/2910768.png" alt="AI Scoring" style={{ height: '50px' }} />
          <h3 style={{ marginTop: '10px', fontSize: '1.5em' }}>AI-Driven Scoring</h3>
          <p style={{ color: '#777', fontSize: '1em' }}>
            Uses machine learning to assess credit risks more accurately.
          </p>
        </div>

        {/* Feature 2 */}
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <img src="https://cdn-icons-png.flaticon.com/128/1055/1055644.png" alt="Real-time Insights" style={{ height: '50px' }} />
          <h3 style={{ marginTop: '10px', fontSize: '1.5em' }}>Real-Time Insights</h3>
          <p style={{ color: '#777', fontSize: '1em' }}>
            Get instant credit scores based on real-time financial behavior.
          </p>
        </div>

        {/* Feature 3 */}
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <img src="https://cdn-icons-png.flaticon.com/128/2333/2333117.png" alt="Risk Prediction" style={{ height: '50px' }} />
          <h3 style={{ marginTop: '10px', fontSize: '1.5em' }}>Risk Prediction</h3>
          <p style={{ color: '#777', fontSize: '1em' }}>
            Forecast potential loan defaults with AI-powered risk models.
          </p>
        </div>

      </section>
      
    </main>
  );
}

export default Contents;
