import React, { useState, useEffect, useMemo, useCallback } from "react";
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
import TrustStats from "./components/TrustStats";
import BrandGrid from "./components/BrandGrid";
import FilterSidebar from "./components/FilterSidebar";
import LegalPage from "./components/LegalPage";
import PartnerDashboard from "./components/PartnerDashboard";
import DealerProfile from "./components/DealerProfile";
import PricingPage from "./components/PricingPage";
import AlertManager from "./components/AlertManager";
import Breadcrumbs from "./components/Breadcrumbs";
import { useLanguage } from "./LanguageContext";
import { initGA, logPageView, logEvent } from "./utils/analytics";
import { getSearchHistory, addSearchHistory, clearSearchHistory } from "./utils/searchHistory";
import { getComparedCars, clearComparedCars, toggleCompareCar } from "./utils/carComparison";
import { Sun, Moon, SlidersHorizontal } from "lucide-react";
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
    limit: "25000",
    maxPages: "15"
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
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    if (savedTheme === 'dark') document.documentElement.classList.add('dark');
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

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
    const storedEmail = localStorage.getItem('user_email');
    const storedRole = localStorage.getItem('user_role');
    if (storedEmail) {
      setCurrentUser({ email: storedEmail, role: storedRole || 'user' });
    }
    fetchBrands();
    fetch(API_BASE_URL + '/api/site/stats').then(r => r.json()).then(d => setSiteStats(d)).catch(() => {});
  }, []);

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const qMake = queryParams.get('make');
    const qModel = queryParams.get('model');
    if (qMake && !urlMake) {
      const restored = {
        make: qMake,
        model: qModel || '',
        maxPrice: queryParams.get('max_price') || '15000',
        minYear: queryParams.get('min_year') || '',
        maxYear: queryParams.get('max_year') || '',
        maxKm: queryParams.get('max_km') || '',
        minPrice: '',
        site: 'both',
        minCc: '',
        minHp: '',
        limit: '25000',
        maxPages: '15',
      };
      setFormData(restored);
      if (qMake && qModel) {
        handleSearch(null, restored);
      }
    }
  }, [location.search]);

  useEffect(() => {
    if (formData.make) {
      fetchModels(formData.make);
    } else {
      setModels([]);
    }
  }, [formData.make]);

  // Sync sidebar filters from formData — intentional two-way binding
  useEffect(() => {
    setSidebarFilters({
      minPrice: formData.minPrice || '',
      maxPrice: formData.maxPrice || '',
      minYear: formData.minYear || '',
      maxYear: formData.maxYear || '',
      maxKm: formData.maxKm || '',
      fuel: formData.fuel ? formData.fuel.split(',').filter(Boolean) : [],
      transmission: formData.transmission ? formData.transmission.split(',').filter(Boolean) : [],
      source: formData.site && formData.site !== 'both' ? formData.site.split(',').filter(Boolean) : [],
    });
  }, [formData.minPrice, formData.maxPrice, formData.minYear, formData.maxYear, formData.maxKm, formData.fuel, formData.transmission, formData.site]);

  useEffect(() => {
    initGA();
    setComparedCars(getComparedCars());
  }, []); // Init once on mount

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
      if (searchData.fuel) params.append("fuel", searchData.fuel);
      if (searchData.transmission) params.append("transmission", searchData.transmission);
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

      if (searchData.make || searchData.model) {
        const urlParams = new URLSearchParams();
        if (searchData.make) urlParams.set('make', searchData.make);
        if (searchData.model) urlParams.set('model', searchData.model);
        if (searchData.maxPrice) urlParams.set('max_price', searchData.maxPrice);
        if (searchData.minYear) urlParams.set('min_year', searchData.minYear);
        if (searchData.maxYear) urlParams.set('max_year', searchData.maxYear);
        if (searchData.maxKm) urlParams.set('max_km', searchData.maxKm);
        const qs = urlParams.toString();
        const newPath = searchData.make && searchData.model
          ? `/masini/${encodeURIComponent(searchData.make)}/${encodeURIComponent(searchData.model)}${qs ? '?' + qs : ''}`
          : `/${qs ? '?' + qs : ''}`;
        navigate(newPath, { replace: true });
      }

      if (searchData.make || searchData.model) { addSearchHistory({ make: searchData.make || "", model: searchData.model || "" }); setSearchHistory(getSearchHistory()); }

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
      setError(err.message || 'A aparut o eroare. Incearca din nou.');
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

  const handleBrandSelect = (brand) => {
    const updated = { ...formData, make: brand, model: '' };
    setFormData(updated);
    handleSearch(null, updated);
  };

  const handleFilterApply = () => {
    const updated = {
      ...formData,
      minPrice: sidebarFilters.minPrice,
      maxPrice: sidebarFilters.maxPrice,
      minYear: sidebarFilters.minYear,
      maxYear: sidebarFilters.maxYear,
      maxKm: sidebarFilters.maxKm,
      fuel: sidebarFilters.fuel.join(','),
      transmission: sidebarFilters.transmission.join(','),
      site: sidebarFilters.source.length > 0 ? sidebarFilters.source.join(',') : 'both',
    };
    setFormData(updated);
    handleSearch(null, updated);
  };

  const [isAlertOpen, setIsAlertOpen] = useState(false);
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [searchHistory, setSearchHistory] = useState(getSearchHistory());
  const [comparedCars, setComparedCars] = useState(getComparedCars());
  const [showCompare, setShowCompare] = useState(false);
  const [siteStats, setSiteStats] = useState({});
  const [sidebarFilters, setSidebarFilters] = useState({
    minPrice: '',
    maxPrice: '',
    minYear: '',
    maxYear: '',
    maxKm: '',
    fuel: [],
    transmission: [],
    source: [],
  });
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
          localStorage.removeItem('user_role');
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

  // Shared logout — also used in PartnerDashboard
  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_role');
    setCurrentUser(null);
  };

  const getSortedResults = () => {
    const parsePrice = (p) => {
      if (typeof p === 'number') return p;
      if (typeof p === 'string') return Number(p.replace(/[^0-9.-]+/g, ""));
      return 0;
    };

    const sorted = [...results];
    switch (sortBy) {
      case "price-asc":
        return sorted.sort((a, b) => parsePrice(a.price) - parsePrice(b.price));
      case "price-desc":
        return sorted.sort((a, b) => parsePrice(b.price) - parsePrice(a.price));
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


  const sortedResults = useMemo(() => getSortedResults(), [results, sortBy]);
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
          <script type="application/ld+json">{JSON.stringify({"@context":"https://schema.org","@type":"SearchResultsPage","name":`${decodeURIComponent(urlMake)} ${decodeURIComponent(urlModel)} de vanzare`,"url":`https://carsniper.ro/masini/${urlMake}/${urlModel}`})}</script>
        </Helmet>
      )}
      {!urlMake && !urlModel && (
        <Helmet>
          <title>CarSniper - Găsește mașina dorită</title>
          <meta name="description" content="Caută și găsește cele mai bune mașini second hand și noi." />
          <meta property="og:title" content="CarSniper - Găsește mașina dorită" />
          <meta property="og:description" content="Caută și găsește cele mai bune mașini second hand și noi." />
          <meta property="og:type" content="website" />
          <meta property="og:url" content="https://carsniper.ro" />
          <link rel="canonical" href="https://carsniper.ro" />
          <script type="application/ld+json">
            {JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebSite",
              "name": "CarSniper",
              "url": "https://carsniper.ro",
              "description": "Cauta si gaseste cele mai bune masini second hand si noi.",
              "potentialAction": {
                "@type": "SearchAction",
                "target": "https://carsniper.ro/?make={search_term_string}",
                "query-input": "required name=search_term_string"
              }
            })}
          </script>
        </Helmet>
      )}
      <nav className="top-nav">
        <div className="nav-brand">
          <span>C</span> CARSNIPER
        </div>
        <div className="nav-links">
          <a href="#">{t('nav', 'browse')}</a>
          <a href="#" className="partner-link" onClick={(e) => { e.preventDefault(); setIsContactOpen(true); }}>{t('nav', 'partner')}</a>

          {currentUser ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              {(currentUser.role === 'admin' || currentUser.role === 'dealer') && (
                <a href="/partner-dashboard" style={{ color: 'var(--primary-color)', fontWeight: 'bold' }}>Dashboard</a>
              )}
              <span style={{ color: 'var(--text-secondary)' }}>{t('nav', 'greeting', { email: currentUser.email })}</span>
              <button onClick={handleLogout} style={{ background: 'none', border: '1px solid var(--border-shell)', color: '#ef4444', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer' }}>
                Logout
              </button>
            </div>
          ) : (
            <button onClick={() => setIsAuthOpen(true)} className="login-btn">{t('nav', 'account')}</button>
          )}

          <div className="lang-selector" style={{ display: 'flex', gap: '8px', marginLeft: '1rem', alignItems: 'center' }}>
            <button onClick={() => setLang('ro')} style={{ background: 'none', border: 'none', color: lang === 'ro' ? 'var(--primary-color)' : 'var(--text-secondary)', cursor: 'pointer', fontWeight: lang === 'ro' ? 'bold' : 'normal' }}>RO</button>
            <span style={{ color: 'var(--text-secondary)' }}>|</span>
            <button onClick={() => setLang('en')} style={{ background: 'none', border: 'none', color: lang === 'en' ? 'var(--primary-color)' : 'var(--text-secondary)', cursor: 'pointer', fontWeight: lang === 'en' ? 'bold' : 'normal' }}>EN</button>
          </div>

          <button onClick={toggleTheme} className="theme-toggle-btn" style={{ marginLeft: '1rem' }} aria-label="Toggle Theme">
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>
      </nav>

      <div className="hero-section">
        <div className="container">
          <h1 className="hero-title">{t('hero', 'title')}</h1>
          <p className="hero-subtitle">
            {t('hero', 'subtitle')}
          </p>
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
        </div>
      </div>

      <TrustStats stats={siteStats} />
      <Breadcrumbs />

      <div className="container">

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
          onLoginSuccess={(email, token, role) => setCurrentUser({ email, role })}
        />

        {!loading && !error && results.length === 0 && !formData.make && (
          <>
            <BrandGrid onBrandSelect={handleBrandSelect} />
            <DealOfTheDay />
          </>
        )}

        {error && <div className="error-message" role="alert">{error}</div>}


        <div id="results-area">
          {loading ? (
            <div className="results-grid">
              {[...Array(8)].map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : (
            <>
              {results.length > 0 && (
                <div className="results-layout">
                  <FilterSidebar
                    filters={sidebarFilters}
                    onFilterChange={setSidebarFilters}
                    onApply={handleFilterApply}
                    isOpen={isFilterOpen}
                    onClose={() => setIsFilterOpen(false)}
                  />
                  <div className="results-main">
                    <div className="results-header">
                      <span className="results-count">
                        {t('results', 'foundPrefix')} <strong>{results.length}</strong> {t('results', 'foundSuffix')}
                      </span>
                      <div className="sort-controls">
                        <button
                          className="filter-toggle-btn"
                          onClick={() => setIsFilterOpen(true)}
                          aria-label="Open filters"
                        >
                          <SlidersHorizontal size={18} />
                          Filtre
                        </button>
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
                    {stats && <PriceStats stats={stats} currentSearch={formData} />}
                    <ResultsList results={currentCars} />
                    <Pagination
                      carsPerPage={itemsPerPage}
                      totalCars={results.length}
                      paginate={paginate}
                      currentPage={currentPage}
                    />
                  </div>
                </div>
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

        {showCompare && comparedCars.length >= 2 && (
        <div className="container" style={{ marginTop: '2rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>Car Comparison</h2>
          <div className="alerts-table-wrap">
            <table className="compare-table">
              <thead>
                <tr>
                  <th>Feature</th>
                  {comparedCars.map(c => <th key={c.id || c.link}>{c.title}</th>)}
                </tr>
              </thead>
              <tbody>
                {[
                  ['Price', 'price'],
                  ['Year', 'year'],
                  ['Km', 'km'],
                  ['Fuel', 'fuel'],
                  ['Transmission', 'transmission'],
                  ['Deal Score', 'deal_score'],
                ].map(([label, key]) => (
                  <tr key={key}>
                    <td>{label}</td>
                    {comparedCars.map(c => (
                      <td key={(c.id || c.link) + key}>{c[key] != null ? String(c[key]) : '-'}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {comparedCars.length > 0 && (
        <div className="compare-bar">
          <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{comparedCars.length} cars selected</span>
          <div className="compare-bar-cars">
            {comparedCars.map(car => (
              <span key={car.id || car.link} className="compare-bar-car">{car.title}</span>
            ))}
          </div>
          <button className="secondary-btn" onClick={() => setShowCompare(!showCompare)}>{showCompare ? "Hide" : "Compare"}</button>
          <button className="filter-clear-btn" onClick={() => { clearComparedCars(); setComparedCars([]); setShowCompare(false); }}>Clear</button>
        </div>
      )}
      <footer className="site-footer">
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
      <Route path="/pricing" element={<div><nav className="top-nav"><div className="nav-brand"><a href="/" style={{textDecoration: 'none', color: 'inherit'}}><span>C</span> CARSNIPER</a></div></nav><PricingPage /></div>} />
          <Route path="/dealer/:email" element={<div><nav className="top-nav"><div className="nav-brand"><a href="/" style={{textDecoration: 'none', color: 'inherit'}}><span>C</span> CARSNIPER</a></div></nav><DealerProfile /></div>} />
      <Route path="/alerts" element={<div><nav className="top-nav"><div className="nav-brand"><a href="/" style={{textDecoration: 'none', color: 'inherit'}}><span>C</span> CARSNIPER</a></div></nav><AlertManager /></div>} />
      <Route path="*" element={
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)', color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif' }}>
          <h1 style={{ fontSize: '4rem', fontWeight: 800, margin: 0, color: 'var(--primary-color)' }}>404</h1>
          <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', margin: '1rem 0' }}>Pagina nu a fost gasita</p>
          <a href="/" style={{ color: 'var(--primary-color)', fontWeight: 600, textDecoration: 'none', marginTop: '1rem' }}>Inapoi acasa</a>
        </div>
      } />
    </Routes>
  );
};

export default App;