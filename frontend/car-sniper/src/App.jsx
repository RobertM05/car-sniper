import React, { useState, useEffect } from "react";
import SearchForm from "./components/SearchForm";
import ResultsList from "./components/ResultsList";
import AlertModal from "./components/AlertModal";
import PriceStats from "./components/PriceStats";
import Pagination from "./components/Pagination";
import SkeletonCard from "./components/SkeletonCard";
import "./App.css";

const App = () => {
  // Centralized State
  const [formData, setFormData] = useState({
    make: "",
    model: "",
    generation: "",
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

  // Dropdown Data
  const [brands, setBrands] = useState([]);
  const [models, setModels] = useState([]);
  const [generations, setGenerations] = useState([]);
  const [loadingBrands, setLoadingBrands] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);
  const [loadingGenerations, setLoadingGenerations] = useState(false);

  // Search & UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState(null);

  // Pagination & Sorting State
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);
  const [sortBy, setSortBy] = useState("price-asc"); // price-asc, price-desc, year-desc, year-asc, km-asc

  // Data Fetching
  const fetchBrands = async () => {
    setLoadingBrands(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/brands');
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
      const response = await fetch(`http://127.0.0.1:8000/api/models/${encodeURIComponent(brand)}`);
      const data = await response.json();
      setModels(data.models || []);
    } catch (err) {
      console.error('Error loading models:', err);
      setModels([]);
    } finally {
      setLoadingModels(false);
    }
  };

  const fetchGenerations = async (brand, model) => {
    if (!brand || !model) {
      setGenerations([]);
      return;
    }
    setLoadingGenerations(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/generations/${encodeURIComponent(brand)}/${encodeURIComponent(model)}`);
      const data = await response.json();
      setGenerations(data.generations || []);
    } catch (err) {
      console.error('Error loading generations:', err);
      setGenerations([]);
    } finally {
      setLoadingGenerations(false);
    }
  };

  // Effects
  useEffect(() => {
    fetchBrands();
  }, []);

  useEffect(() => {
    if (formData.make) {
      fetchModels(formData.make);
      setFormData(prev => ({ ...prev, model: "", generation: "" }));
    } else {
      setModels([]);
    }
  }, [formData.make]);

  useEffect(() => {
    if (formData.make && formData.model) {
      fetchGenerations(formData.make, formData.model);
      setFormData(prev => ({ ...prev, generation: "" }));
    } else {
      setGenerations([]);
    }
  }, [formData.make, formData.model]);

  // Search Handler
  const handleSearch = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResults([]);
    setCurrentPage(1); // Reset to page 1 on new search

    try {
      const params = new URLSearchParams();
      // Map formData to API params
      if (formData.make) params.append("make", formData.make);
      if (formData.model) params.append("model", formData.model);
      if (formData.generation) params.append("generation", formData.generation);
      if (formData.minPrice) params.append("min_price", formData.minPrice);
      if (formData.maxPrice) params.append("max_price", formData.maxPrice);
      if (formData.minYear) params.append("min_year", formData.minYear);
      if (formData.maxYear) params.append("max_year", formData.maxYear);
      if (formData.maxKm) params.append("max_km", formData.maxKm);
      params.append("site", formData.site);
      params.append("limit", formData.limit);
      params.append("max_pages", formData.maxPages);

      const url = `http://127.0.0.1:8000/api/search?${params.toString()}`;

      const res = await fetch(url);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail ? `Eroare server: ${JSON.stringify(errorData.detail)}` : `HTTP ${res.status}`);
      }

      const data = await res.json();
      setResults(Array.isArray(data.results) ? data.results : []);

      // Fetch stats for this model
      if (formData.make && formData.model) {
        try {
          const statsRes = await fetch(`http://127.0.0.1:8000/api/stats/${formData.make}/${formData.model}`);
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
      setError(err.message || "A apărut o eroare la conexiunea cu serverul.");
    } finally {
      setLoading(false);
    }
  };

  // Alert Handler
  const [isAlertOpen, setIsAlertOpen] = useState(false);

  const handleCreateAlert = async (email) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/alert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_email: email,
          make: formData.make,
          model: formData.model,
          max_price: parseInt(formData.maxPrice) || 0
        })
      });

      if (!response.ok) throw new Error("Nu s-a putut salva alerta.");

      alert("Alertă salvată cu succes! Vei primi notificări pe email.");
    } catch (err) {
      console.error(err);
      alert("Eroare la salvarea alertei.");
    }
  };

  // Logic for Sorting
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

  // Logic for Pagination
  const sortedResults = getSortedResults();
  const indexOfLastCar = currentPage * itemsPerPage;
  const indexOfFirstCar = indexOfLastCar - itemsPerPage;
  const currentCars = sortedResults.slice(indexOfFirstCar, indexOfLastCar);

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 800, behavior: 'smooth' }); // Auto-scroll to results
  };

  return (
    <div className="container">
      <div className="hero-section">
        <h1 className="hero-title">Car Sniper 🎯</h1>
        <p className="hero-subtitle">
          Găsește cea mai bună ofertă din mii de anunțuri verificate de pe OLX și Autovit.
        </p>
      </div>

      <SearchForm
        formData={formData}
        setFormData={setFormData}
        brands={brands}
        models={models}
        generations={generations}
        loadingBrands={loadingBrands}
        loadingModels={loadingModels}
        loadingGenerations={loadingGenerations}
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

      {error && <div className="error-message">{error}</div>}

      {/* Results Area */}
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
                  Am găsit <strong>{results.length}</strong> rezultate
                </span>

                <div className="sort-controls">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="sort-select"
                  >
                    <option value="price-asc">Preț (Crescător)</option>
                    <option value="price-desc">Preț (Descrescător)</option>
                    <option value="year-desc">An (Cel mai nou)</option>
                    <option value="year-asc">An (Cel mai vechi)</option>
                    <option value="km-asc">Km (Cei mai puțini)</option>
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
          </>
        )}
      </div>

      <footer style={{ textAlign: 'center', marginTop: '4rem', color: 'var(--text-secondary)', padding: '2rem' }}>
        <p>&copy; {new Date().getFullYear()} Car Sniper. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;