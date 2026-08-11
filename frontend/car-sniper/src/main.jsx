import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import './index.css'
import App from './App.jsx'
import { LanguageProvider } from './LanguageContext';

import { AuthProvider } from './contexts/AuthContext';
import { SearchProvider } from './contexts/SearchContext';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HelmetProvider>
      <BrowserRouter>
        <AuthProvider>
          <SearchProvider>
            <LanguageProvider>
              <App />
            </LanguageProvider>
          </SearchProvider>
        </AuthProvider>
      </BrowserRouter>
    </HelmetProvider>
  </StrictMode>,
)
