import { Form } from 'antd';
import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import Login from './views/login/Login';
import Office from './views/office/Office';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/office-view" element={<Office />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
