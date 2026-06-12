import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate, useParams, useLocation } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import SearchForm from "./components/SearchForm";
import ResultsList from "./components/ResultsList";
import AlertModal from "./components/AlertModal";
import ContactModal from "./components/ContactModal";
import AuthModal from "./components/AuthModal";
import PriceStats from "./components/PriceStats";
import Pagination from "./components/Pagination";
import SkeletonCard from "./components/SkeletonCard";
import DealOfTheDay from "./components/DealOfTheDay";
import LegalPage from "./components/LegalPage";
import PartnerDashboard from "./components/PartnerDashboard";
import emptyStateImg from "./assets/empty-state.png";
import { useLanguage } from "./LanguageContext";
import { initGA, logPageView, logEvent } from "./utils/analytics";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const AppContent = () => {
  const { t, lang, setLang } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();
  const { make: urlMake, model: urlModel } = useParams();

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
    const storedToken = localStorage.getItem('jwt_token');
    const storedEmail = localStorage.getItem('user_email');
    if (storedToken && storedEmail) {
      setCurrentUser(storedEmail);
    }
  }, []);

  useEffect(() => {
    if (formData.make) {
      fetchModels(formData.make);
    } else {
      setModels([]);
    }
  }, [formData.make]);

  useEffect(() => {
    initGA();
  }, []);

  useEffect(() => {
    logPageView(location.pathname + location.search);
  }, [location]);

  useEffect(() => {
    if (urlMake && urlModel) {
      const make = decodeURIComponent(urlMake);
      const model = decodeURIComponent(urlModel);
      
      setFormData(prev => ({ ...prev, make, model }));
      fetchModels(make);
      handleSearch(null, { ...formData, make, model });
    }
  }, [urlMake, urlModel]);


  const handleSearch = async (e, overrideData = null) => {
    if (e && e.preventDefault) e.preventDefault();
    setError("");
    setLoading(true);
    setResults([]);
    setCurrentPage(1);

    const searchData = overrideData || formData;

    try {
      const params = new URLSearchParams();

      if (searchData.make) params.append("make", searchData.make);
      if (searchData.model) params.append("model", searchData.model);
      if (searchData.minPrice) params.append("min_price", searchData.minPrice);
      if (searchData.maxPrice) params.append("max_price", searchData.maxPrice);
      if (searchData.minYear) params.append("min_year", searchData.minYear);
      if (searchData.maxYear) params.append("max_year", searchData.maxYear);
      if (searchData.maxKm) params.append("max_km", searchData.maxKm);
      params.append("site", searchData.site);
      params.append("limit", searchData.limit);
      params.append("max_pages", searchData.maxPages);

      const url = `${API_BASE_URL}/api/search?${params.toString()}`;

      const res = await fetch(url);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail ? `Eroare server: ${JSON.stringify(errorData.detail)}` : `HTTP ${res.status}`);
      }

      const data = await res.json();
      setResults(Array.isArray(data.results) ? data.results : []);

      logEvent("Search", "Performed Search", `${searchData.make || 'Any'} ${searchData.model || ''}`, Array.isArray(data.results) ? data.results.length : 0);

      if (searchData.make && searchData.model) {
        try {
          const statsRes = await fetch(`${API_BASE_URL}/api/stats/${searchData.make}/${searchData.model}`);
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

  const handleSearchSubmit = (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (formData.make && formData.model) {
      const targetUrl = `/masini/${encodeURIComponent(formData.make)}/${encodeURIComponent(formData.model)}`;
      if (location.pathname === targetUrl) {
        handleSearch();
      } else {
        navigate(targetUrl);
      }
    } else {
      if (location.pathname !== "/") {
        navigate("/");
      } else {
        handleSearch();
      }
    }
  };


  const [isAlertOpen, setIsAlertOpen] = useState(false);
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const handleCreateAlert = async (email) => {
    try {
      const token = localStorage.getItem('jwt_token');
      if (!token) {
        alert("Eroare de sesiune. Te rugăm să te loghezi din nou.");
        setCurrentUser(null);
        setIsAuthOpen(true);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/alert`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
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

      if (response.status === 401) {
          localStorage.removeItem('jwt_token');
          localStorage.removeItem('user_email');
          setCurrentUser(null);
          setIsAuthOpen(true);
          throw new Error("Sesiunea a expirat. Te rugăm să te conectezi din nou.");
      }

      if (!response.ok) throw new Error("Nu s-a putut salva alerta.");

      logEvent("Alert", "Created Price Alert", `${formData.make || 'Any'} ${formData.model || ''} - Max: ${formData.maxPrice}`);
      alert("Alertă salvată cu succes! Vei primi notificări pe email.");
    } catch (err) {
      console.error(err);
      alert("Eroare la salvarea alertei.");
    }
  };

  const handleLogout = (e) => {
    e.preventDefault();
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_email');
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
      {urlMake && urlModel && (
        <Helmet>
          <title>{`${decodeURIComponent(urlMake)} ${decodeURIComponent(urlModel)} de vânzare - Cele mai bune prețuri | CarSniper`}</title>
          <meta name="description" content={`Găsește cele mai bune oferte pentru ${decodeURIComponent(urlMake)} ${decodeURIComponent(urlModel)} de vânzare. Prețuri excelente și mașini verificate.`} />
        </Helmet>
      )}
      {!urlMake && !urlModel && (
        <Helmet>
          <title>CarSniper - Găsește mașina dorită</title>
          <meta name="description" content="Caută și găsește cele mai bune mașini second hand și noi." />
        </Helmet>
      )}
      <nav className="top-nav">
        <div className="nav-brand">
          <span>C</span> CARSNIPER
        </div>
        <div className="nav-links">
          <a href="#">{t('nav', 'browse')}</a>
          <a href="/partner-dashboard" style={{ color: 'var(--primary-color)' }}>Dashboard</a>
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
          onSubmit={handleSearchSubmit}
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
          onLoginSuccess={(email, token) => setCurrentUser(email)}
        />

        {!loading && !error && results.length === 0 && !formData.make && (
          <DealOfTheDay />
        )}

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
          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '1rem' }}>
             <a href="/termeni" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>{t('legal', 'termsTitle')}</a>
             <a href="/confidentialitate" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>{t('legal', 'privacyTitle')}</a>
          </div>
          <p>{t('footer', null, { year: new Date().getFullYear() })}</p>
        </footer>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<AppContent />} />
      <Route path="/masini/:make/:model" element={<AppContent />} />
      <Route path="/termeni" element={<div><nav className="top-nav"><div className="nav-brand"><a href="/" style={{textDecoration: 'none', color: 'inherit'}}><span>C</span> CARSNIPER</a></div></nav><LegalPage type="terms" /></div>} />
      <Route path="/confidentialitate" element={<div><nav className="top-nav"><div className="nav-brand"><a href="/" style={{textDecoration: 'none', color: 'inherit'}}><span>C</span> CARSNIPER</a></div></nav><LegalPage type="privacy" /></div>} />
      <Route path="/partner-dashboard" element={<PartnerDashboard />} />
    </Routes>
  );
};

export default App;