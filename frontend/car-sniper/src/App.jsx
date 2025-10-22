import React, { useState } from "react";

const App = () => {
  const [make, setMake] = useState("");
  const [model, setModel] = useState("");
  const [maxPrice, setMaxPrice] = useState("15000");
  const [site, setSite] = useState("both");

  const [limit, setLimit] = useState("");
  const [maxPages, setMaxPages] = useState("");
  const [maxKm, setMaxKm] = useState("");
  const [minYear, setMinYear] = useState("");
  const [minCc, setMinCc] = useState("");
  const [minHp, setMinHp] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState([]);

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
      if (maxKm) params.set("max_km", String(maxKm));
      if (minYear) params.set("min_year", String(minYear));
      if (minCc) params.set("min_cc", String(minCc));
      if (minHp) params.set("min_hp", String(minHp));

      const res = await fetch(`http://127.0.0.1:8000/api/search?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
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
          <input
            type="text"
            placeholder="Ex: BMW"
            value={make}
            onChange={(e) => setMake(e.target.value)}
          />
        </div>

        <div>
          <label>Model</label>
          <input
            type="text"
            placeholder="Ex: 320d"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          />
        </div>

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