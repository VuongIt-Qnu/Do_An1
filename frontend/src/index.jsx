/**
 * Application Entry Point
 * Initializes React, i18n, and renders the root component
 */
import React from 'react';
import ReactDOM from 'react-dom/client';

// Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
// Toast notifications CSS
import 'react-toastify/dist/ReactToastify.css';
// Custom global styles
import './styles/global.css';

// Initialize i18n (must be before App render)
import './i18n/index';

import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
