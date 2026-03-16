import React, { useState, useEffect } from "react";
import SearchForm from "./components/SearchForm";
import ResultsList from "./components/ResultsList";
import AlertModal from "./components/AlertModal";
import ContactModal from "./components/ContactModal";
import AuthModal from "./components/AuthModal";
import PriceStats from "./components/PriceStats";
import Pagination from "./components/Pagination";
import SkeletonCard from "./components/SkeletonCard";
import emptyStateImg from "./assets/empty-state.png";
import { useLanguage } from "./LanguageContext";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const App = () => {
  const { t, lang, setLang } = useLanguage();

  const [formData, setFormData] = useState({
    make: "",
    model: "",
    minPrice: "",
    maxPrice: "15000",
    site: "both",
    minYear: "",
    maxYear: "",
    maxKm: "",
    minCc: "",
    minHp: "",
    limit: "50",
    maxPages: "5"
  });


  const [brands, setBrands] = useState([]);
  const [models, setModels] = useState([]);
  const [loadingBrands, setLoadingBrands] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);


  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState(null);


  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);
  const [sortBy, setSortBy] = useState("price-asc");


  const fetchBrands = async () => {
    setLoadingBrands(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/brands`);
      const data = await response.json();
      if (data.brands) setBrands(data.brands);
    } catch (err) {
      console.error('Error loading brands:', err);
    } finally {
      setLoadingBrands(false);
    }
  };

  const fetchModels = async (brand) => {
    if (!brand) {
      setModels([]);
      return;
    }
    setLoadingModels(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/models/${encodeURIComponent(brand)}`);
      const data = await response.json();
      setModels(data.models || []);
    } catch (err) {
      console.error('Error loading models:', err);
      setModels([]);
    } finally {
      setLoadingModels(false);
    }
  };




  useEffect(() => {
    fetchBrands();
  }, []);

  useEffect(() => {
    if (formData.make) {
      fetchModels(formData.make);
      setFormData(prev => ({ ...prev, model: "" }));
    } else {
      setModels([]);
    }
  }, [formData.make]);


  const handleSearch = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    setError("");
    setLoading(true);
    setResults([]);
    setCurrentPage(1);

    try {
      const params = new URLSearchParams();

      if (formData.make) params.append("make", formData.make);
      if (formData.model) params.append("model", formData.model);
      if (formData.minPrice) params.append("min_price", formData.minPrice);
      if (formData.maxPrice) params.append("max_price", formData.maxPrice);
      if (formData.minYear) params.append("min_year", formData.minYear);
      if (formData.maxYear) params.append("max_year", formData.maxYear);
      if (formData.maxKm) params.append("max_km", formData.maxKm);
      params.append("site", formData.site);
      params.append("limit", formData.limit);
      params.append("max_pages", formData.maxPages);

      const url = `${API_BASE_URL}/api/search?${params.toString()}`;

      const res = await fetch(url);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail ? `Eroare server: ${JSON.stringify(errorData.detail)}` : `HTTP ${res.status}`);
      }

      const data = await res.json();
      setResults(Array.isArray(data.results) ? data.results : []);

      if (formData.make && formData.model) {
        try {
          const statsRes = await fetch(`${API_BASE_URL}/api/stats/${formData.make}/${formData.model}`);
          if (statsRes.ok) {
            const statsData = await statsRes.json();
            if (!statsData.error) {
              setStats(statsData);
            } else {
              setStats(null);
            }
          }
        } catch (e) {
          console.error("Failed to fetch stats", e);
          setStats(null);
        }
      } else {
        setStats(null);
      }
    } catch (err) {
      console.error("Catch Error:", err);
      setError(err.message || t('search', 'searching'));
    } finally {
      setLoading(false);
    }
  };


  const [isAlertOpen, setIsAlertOpen] = useState(false);
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const handleCreateAlert = async (email) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/alert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_email: email,
          make: formData.make,
          model: formData.model,
          min_price: parseInt(formData.minPrice) || null,
          max_price: parseInt(formData.maxPrice) || null,
          min_year: parseInt(formData.minYear) || null,
          max_year: parseInt(formData.maxYear) || null,
          max_km: parseInt(formData.maxKm) || null
        })
      });

      if (!response.ok) throw new Error("Nu s-a putut salva alerta.");

      alert("Alertă salvată cu succes! Vei primi notificări pe email.");
    } catch (err) {
      console.error(err);
      alert("Eroare la salvarea alertei.");
    }
  };

  const handleLogout = (e) => {
    e.preventDefault();
    setCurrentUser(null);
  };

  const getSortedResults = () => {
    const sorted = [...results];
    switch (sortBy) {
      case "price-asc":
        return sorted.sort((a, b) => a.price - b.price);
      case "price-desc":
        return sorted.sort((a, b) => b.price - a.price);
      case "year-desc":
        return sorted.sort((a, b) => (b.year || 0) - (a.year || 0));
      case "year-asc":
        return sorted.sort((a, b) => (a.year || 0) - (b.year || 0));
      case "km-asc":
        return sorted.sort((a, b) => (a.km || 0) - (b.km || 0));
      default:
        return sorted;
    }
  };


  const sortedResults = getSortedResults();
  const indexOfLastCar = currentPage * itemsPerPage;
  const indexOfFirstCar = indexOfLastCar - itemsPerPage;
  const currentCars = sortedResults.slice(indexOfFirstCar, indexOfLastCar);

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 800, behavior: 'smooth' });
  };

  return (
    <div>
      <nav className="top-nav">
        <div className="nav-brand">
          <span>C</span> CARSNIPER
        </div>
        <div className="nav-links">
          <a href="#">{t('nav', 'browse')}</a>
          <a href="#">{t('nav', 'partnerNetwork')}</a>
          <a href="#" className="partner-link" onClick={(e) => { e.preventDefault(); setIsContactOpen(true); }}>{t('nav', 'partner')}</a>

          {currentUser ? (
            <div className="user-menu" style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
              <span style={{ color: 'var(--primary-color)', fontSize: '13px' }}>{currentUser}</span>
              <a href="#" onClick={handleLogout} style={{ color: '#ef4444' }}>Ieșire</a>
            </div>
          ) : (
            <a href="#" onClick={(e) => { e.preventDefault(); setIsAuthOpen(true); }}>{t('nav', 'account')}</a>
          )}

          <div className="lang-selector" style={{ display: 'flex', gap: '8px', marginLeft: '1rem', alignItems: 'center' }}>
            <button onClick={() => setLang('ro')} style={{ background: 'none', border: 'none', color: lang === 'ro' ? 'var(--primary-color)' : 'var(--text-secondary)', cursor: 'pointer', fontWeight: lang === 'ro' ? 'bold' : 'normal' }}>RO</button>
            <span style={{ color: 'var(--text-secondary)' }}>|</span>
            <button onClick={() => setLang('en')} style={{ background: 'none', border: 'none', color: lang === 'en' ? 'var(--primary-color)' : 'var(--text-secondary)', cursor: 'pointer', fontWeight: lang === 'en' ? 'bold' : 'normal' }}>EN</button>
          </div>
        </div>
      </nav>

      <div className="hero-section">
        <div className="container">
          <h1 className="hero-title">{t('hero', 'title')}</h1>
          <p className="hero-subtitle">
            {t('hero', 'subtitle')}
          </p>
        </div>
      </div>

      <div className="container" style={{ marginTop: '-80px', position: 'relative', zIndex: 10 }}>

        <SearchForm
          formData={formData}
          setFormData={setFormData}
          brands={brands}
          models={models}
          loadingBrands={loadingBrands}
          loadingModels={loadingModels}
          onSubmit={handleSearch}
          loading={loading}
          onAlertClick={() => setIsAlertOpen(true)}
        />

        <AlertModal
          isOpen={isAlertOpen}
          onClose={() => setIsAlertOpen(false)}
          onSubmit={handleCreateAlert}
          searchParams={formData}
        />

        <ContactModal
          isOpen={isContactOpen}
          onClose={() => setIsContactOpen(false)}
        />

        <AuthModal
          isOpen={isAuthOpen}
          onClose={() => setIsAuthOpen(false)}
          onLoginSuccess={(email) => setCurrentUser(email)}
        />

        {error && <div className="error-message">{error}</div>}


        <div id="results-area">
          {loading ? (
            <div className="results-grid">
              {[...Array(8)].map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : (
            <>
              {results.length > 0 && (
                <div className="results-header">
                  <span className="results-count">
                    {t('results', 'foundPrefix')} <strong>{results.length}</strong> {t('results', 'foundSuffix')}
                  </span>

                  <div className="sort-controls">
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="sort-select"
                    >
                      <option value="price-asc">{t('results', 'sortPriceAsc')}</option>
                      <option value="price-desc">{t('results', 'sortPriceDesc')}</option>
                      <option value="year-desc">{t('results', 'sortYearDesc')}</option>
                      <option value="year-asc">{t('results', 'sortYearAsc')}</option>
                      <option value="km-asc">{t('results', 'sortKmAsc')}</option>
                    </select>
                  </div>
                </div>
              )}

              {stats && <PriceStats stats={stats} currentSearch={formData} />}

              <ResultsList results={currentCars} />

              {results.length > 0 && (
                <Pagination
                  carsPerPage={itemsPerPage}
                  totalCars={results.length}
                  paginate={paginate}
                  currentPage={currentPage}
                />
              )}

              {results.length === 0 && !error && formData.make && (
                <div style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-secondary)' }}>
                  <h3>{t('results', 'noResultsTitle')}</h3>
                  <p>{t('results', 'noResultsSubtitle')}</p>
                </div>
              )}
            </>
          )}
        </div>

        <footer style={{ textAlign: 'center', marginTop: '4rem', color: 'var(--text-secondary)', padding: '2rem' }}>
          <p>{t('footer', null, { year: new Date().getFullYear() })}</p>
        </footer>
      </div>
    </div>
  );
};

export default App;