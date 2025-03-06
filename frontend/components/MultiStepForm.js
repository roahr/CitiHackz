import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const FinancialDataForm = ({ onNext }) => {
  const [formData, setFormData] = useState({
    transaction_level_banking: "",
    credit_trade_line: "",
    demand_deposit_account: ""
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    const response = await fetch("/api/financial-score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    const data = await response.json();
    onNext(data.score);
  };

  return (
    <div>
      <h2>Financial Data</h2>
      {Object.keys(formData).map((key) => (
        <div key={key}>
          <label>{key.replace(/_/g, " ")}</label>
          <input type="number" name={key} value={formData[key]} onChange={handleChange} />
        </div>
      ))}
      <button onClick={handleSubmit}>Next</button>
    </div>
  );
};

const BillPaymentForm = ({ onNext }) => {
  const [formData, setFormData] = useState({
    telco: "",
    utility: "",
    retailers: "",
    rent: ""
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    const response = await fetch("/api/bill-score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    const data = await response.json();
    onNext(data.score);
  };

  return (
    <div>
      <h2>Bill Payment Data</h2>
      {Object.keys(formData).map((key) => (
        <div key={key}>
          <label>{key.replace(/_/g, " ")}</label>
          <input type="number" name={key} value={formData[key]} onChange={handleChange} />
        </div>
      ))}
      <button onClick={handleSubmit}>Next</button>
    </div>
  );
};

const PsychometricTest = ({ onComplete }) => {
  const [score, setScore] = useState(0);
  const questions = [
    "I prefer structured over flexible work environments",
    "I take calculated risks when making decisions",
    "I am comfortable with uncertainty"
  ];

  const handleAnswer = (value) => {
    setScore(score + value);
  };

  const handleSubmit = async () => {
    const response = await fetch("/api/psychometric-score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ score })
    });
    const data = await response.json();
    onComplete(data.score);
  };

  return (
    <div>
      <h2>Psychometric Test</h2>
      {questions.map((q, index) => (
        <div key={index}>
          <p>{q}</p>
          <button onClick={() => handleAnswer(1)}>Agree</button>
          <button onClick={() => handleAnswer(0)}>Neutral</button>
          <button onClick={() => handleAnswer(-1)}>Disagree</button>
        </div>
      ))}
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
};

const ResultPage = ({ finalScore, riskFactor }) => (
  <div>
    <h2>Final Results</h2>
    <p>Credit Score: {finalScore}</p>
    <p>Risk Factor: {riskFactor}</p>
  </div>
);

const MultiStepForm = () => {
  const navigate = useNavigate();
  const [scores, setScores] = useState({ financial: 0, bill: 0, psychometric: 0 });
  const [finalScore, setFinalScore] = useState(null);
  const [riskFactor, setRiskFactor] = useState(null);

  const handleFinalCalculation = async () => {
    const response = await fetch("/api/final-score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scores)
    });
    const data = await response.json();
    setFinalScore(data.finalScore);
    setRiskFactor(data.riskFactor);
    navigate("/result");
  };

  return (
    <div>
      <FinancialDataForm onNext={(score) => { setScores({ ...scores, financial: score }); navigate("/bill"); }} />
      <BillPaymentForm onNext={(score) => { setScores({ ...scores, bill: score }); navigate("/psychometric"); }} />
      <PsychometricTest onComplete={(score) => { setScores({ ...scores, psychometric: score }); handleFinalCalculation(); }} />
      {finalScore !== null && <ResultPage finalScore={finalScore} riskFactor={riskFactor} />}
    </div>
  );
};

export default MultiStepForm;
