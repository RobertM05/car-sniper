import React, { useState, useEffect } from "react";

const App = () => {
  const [make, setMake] = useState("");
  const [model, setModel] = useState("");
  const [generation, setGeneration] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("15000");
  const [site, setSite] = useState("both");

  const [limit, setLimit] = useState("");
  const [maxPages, setMaxPages] = useState("");
  const [maxKm, setMaxKm] = useState("");
  const [minYear, setMinYear] = useState("");
  const [maxYear, setMaxYear] = useState("");
  const [minCc, setMinCc] = useState("");
  const [minHp, setMinHp] = useState("");

  // State pentru dropdown-uri
  const [brands, setBrands] = useState([]);
  const [models, setModels] = useState([]);
  const [generations, setGenerations] = useState([]);
  const [loadingBrands, setLoadingBrands] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);
  const [loadingGenerations, setLoadingGenerations] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState([]);

  // Funcții pentru încărcarea datelor
  const fetchBrands = async () => {
    setLoadingBrands(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/brands');
      const data = await response.json();
      if (data.brands) {
        setBrands(data.brands);
      }
    } catch (err) {
      console.error('Eroare la încărcarea mărcilor:', err);
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
      if (data.models) {
        setModels(data.models);
      } else {
        setModels([]);
      }
    } catch (err) {
      console.error('Eroare la încărcarea modelelor:', err);
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
      if (data.generations) {
        setGenerations(data.generations);
      } else {
        setGenerations([]);
      }
    } catch (err) {
      console.error('Eroare la încărcarea generațiilor:', err);
      setGenerations([]);
    } finally {
      setLoadingGenerations(false);
    }
  };

  // useEffect pentru încărcarea mărcilor la montarea componentului
  useEffect(() => {
    fetchBrands();
  }, []);

  // useEffect pentru încărcarea modelelor când se schimbă marca
  useEffect(() => {
    if (make) {
      fetchModels(make);
      setModel(""); // Resetăm modelul când se schimbă marca
      setGeneration(""); // Resetăm generația
    } else {
      setModels([]);
      setModel("");
      setGeneration("");
    }
  }, [make]);

  // useEffect pentru încărcarea generațiilor când se schimbă modelul
  useEffect(() => {
    if (make && model) {
      fetchGenerations(make, model);
      setGeneration(""); // Resetăm generația când se schimbă modelul
    } else {
      setGenerations([]);
      setGeneration("");
    }
  }, [make, model]);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResults([]);
    try {
      const params = new URLSearchParams({
        make: make || "",
        model: model || "",
        max_price: String(maxPrice || 0),
        site,
        limit: String(limit || 50),
        max_pages: String(maxPages || 5),
      });
      if (minPrice) params.set("min_price", String(minPrice));
      if (maxKm) params.set("max_km", String(maxKm));
      if (minYear) params.set("min_year", String(minYear));
      if (maxYear) params.set("max_year", String(maxYear));
      if (minCc) params.set("min_cc", String(minCc));
      if (minHp) params.set("min_hp", String(minHp));
      if (generation) params.set("generation", String(generation));

      const url = `http://127.0.0.1:8000/api/search?${params.toString()}`;
      console.log('Request URL:', url);
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      console.log('Response data:', data);
      setResults(Array.isArray(data.results) ? data.results : []);
    } catch (err) {
      setError("Eroare la cautare. Verifica backend-ul si parametrii.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Car Search</h1>
      <form onSubmit={onSubmit}>
        <div>
          <label>Marca</label>
          <select 
            value={make} 
            onChange={(e) => setMake(e.target.value)}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "10px 12px",
              border: "1px solid #d1d5db",
              borderRadius: 8,
              background: "#ffffff",
            }}
          >
            <option value="">Selectează marca</option>
            {brands.map((brand) => (
              <option key={brand} value={brand}>
                {brand}
              </option>
            ))}
          </select>
          {loadingBrands && <small>Se încarcă mărcile...</small>}
        </div>

        <div>
          <label>Model</label>
          <select 
            value={model} 
            onChange={(e) => setModel(e.target.value)}
            disabled={!make || loadingModels}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "10px 12px",
              border: "1px solid #d1d5db",
              borderRadius: 8,
              background: make ? "#ffffff" : "#f9fafb",
            }}
          >
            <option value="">Selectează modelul</option>
            {models.map((modelName) => (
              <option key={modelName} value={modelName}>
                {modelName}
              </option>
            ))}
          </select>
          {loadingModels && <small>Se încarcă modelele...</small>}
        </div>

        {generations.length > 0 && (
          <div>
            <label>Generația</label>
            <select 
              value={generation} 
              onChange={(e) => setGeneration(e.target.value)}
              disabled={!model || loadingGenerations}
              style={{
                width: "100%",
                boxSizing: "border-box",
                padding: "10px 12px",
                border: "1px solid #d1d5db",
                borderRadius: 8,
                background: model ? "#ffffff" : "#f9fafb",
              }}
            >
              <option value="">Selectează generația (opțional)</option>
              {generations.map((gen) => (
                <option key={gen.generation} value={gen.generation}>
                  {gen.generation} ({gen.min_year}-{gen.max_year})
                </option>
              ))}
            </select>
            {loadingGenerations && <small>Se încarcă generațiile...</small>}
          </div>
        )}

        <div>
          <label>Pret maxim (€)</label>
          <input
            type="number"
            placeholder="Ex: 10000"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            min="0"
          />
        </div>

        <div>
          <label>Pret minim (€)</label>
          <input
            type="number"
            placeholder="Ex: 5000"
            value={minPrice}
            onChange={(e) => setMinPrice(e.target.value)}
            min="0"
          />
        </div>

        <div>
          <label>Site</label>
          <select value={site} onChange={(e) => setSite(e.target.value)} style={{
            width: "100%",
            boxSizing: "border-box",
            padding: "10px 12px",
            border: "1px solid #d1d5db",
            borderRadius: 8,
            background: "#ffffff",
          }}>
            <option value="both">Ambele</option>
            <option value="autovit">Autovit</option>
            <option value="olx">OLX</option>
          </select>
        </div>

        <div>
          <label>Limit rezultate</label>
          <input
            type="number"
            value={limit}
            onChange={(e) => setLimit(e.target.value)}
            min="0"
          />
        </div>

        <div>
          <label>Max pagini</label>
          <input
            type="number"
            value={maxPages}
            onChange={(e) => setMaxPages(e.target.value)}
            min="0"
          />
        </div>

        <div>
          <label>Km max</label>
          <input
            type="number"
            value={maxKm}
            onChange={(e) => setMaxKm(e.target.value)}
            min="0"
          />
        </div>

        <div>
          <label>An minim</label>
          <input
            type="number"
            value={minYear}
            onChange={(e) => setMinYear(e.target.value)}
            min="0"
          />
        </div>

        <div>
          <label>An maxim</label>
          <input
            type="number"
            value={maxYear}
            onChange={(e) => setMaxYear(e.target.value)}
            min="0"
          />
        </div>

        <div>
          <label>CC minim</label>
          <input
            type="number"
            value={minCc}
            onChange={(e) => setMinCc(e.target.value)}
            min="0"
          />
        </div>

        <div>
          <label>CP minim</label>
          <input
            type="number"
            value={minHp}
            onChange={(e) => setMinHp(e.target.value)}
            min="0"
          />
        </div>

        <button type="submit" disabled={loading}>{loading ? "Caut..." : "Cauta"}</button>
      </form>
      {error && <p style={{ color: "#b91c1c", marginTop: 8 }}>{error}</p>}
      <div style={{ marginTop: 16 }}>
        {results.map((car, idx) => (
          <div key={idx} style={{
            padding: 12,
            border: "1px solid #e5e7eb",
            borderRadius: 8,
            marginBottom: 8,
            background: "#fff"
          }}>
            <div style={{ fontWeight: 600 }}>{car.title || car.name || "Anunt"}</div>
            <div style={{ fontSize: 14, color: "#374151" }}>
              Pret: {car.price}
              {car.km ? ` • Km: ${car.km}` : ""}
              {car.year ? ` • An: ${car.year}` : ""}
            </div>
            {(car.url || car.link) && (
              <a href={car.url || car.link} target="_blank" rel="noreferrer">Deschide anunt</a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;