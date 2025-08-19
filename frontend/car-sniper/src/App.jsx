import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [make, setMake] = useState("");
  const [model, setModel] = useState("");
  const [cars, setCars] = useState([]);
  const [maxKm, setMaxKm] = useState("");
  const [minYear, setMinYear] = useState("");
  const [minCc, setMinCc] = useState("");
  const [minHp, setMinHp] = useState("");
  const [limit, setLimit] = useState("60");
  const [maxPages, setMaxPages] = useState("8");
  const [loading, setLoading] = useState(false);

  const searchCars = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ make, model, max_price: "100000", site: "autovit" });
      if (maxKm) params.append("max_km", maxKm);
      if (minYear) params.append("min_year", minYear);
      if (minCc) params.append("min_cc", minCc);
      if (minHp) params.append("min_hp", minHp);
      if (limit) params.append("limit", limit);
      if (maxPages) params.append("max_pages", maxPages);
      const response = await fetch(`http://localhost:8000/api/search?${params.toString()}`);
      const data = await response.json();
      setCars(data.results);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };


  return (

      <div classname = "container">
        <h1>Car Sniper</h1>
        <input
        type = "text"
        placeholder = "Marca"
        value = {make}
        onChange={(e) => setMake(e.target.value)}
        />
        <input
        type = "text"
        placeholder = "Model"
        value ={model}
        onChange={(e) => setModel(e.target.value)}
        />
        <input
        type = "number"
        placeholder = "Limit rezultate"
        value ={limit}
        onChange={(e) => setLimit(e.target.value)}
        />
        <input
        type = "number"
        placeholder = "Max pagini"
        value ={maxPages}
        onChange={(e) => setMaxPages(e.target.value)}
        />
        <input
        type = "number"
        placeholder = "Km max"
        value ={maxKm}
        onChange={(e) => setMaxKm(e.target.value)}
        />
        <input
        type = "number"
        placeholder = "An minim"
        value ={minYear}
        onChange={(e) => setMinYear(e.target.value)}
        />
        <input
        type = "number"
        placeholder = "CC minim"
        value ={minCc}
        onChange={(e) => setMinCc(e.target.value)}
        />
        <input
        type = "number"
        placeholder = "CP minim"
        value ={minHp}
        onChange={(e) => setMinHp(e.target.value)}
        />
        <button onClick ={searchCars}>Cauta masini</button>
        

        {loading && <p>Se cauta...</p>}

        <ul>
          {cars.map((car,index) => (
            <li key={index}>
              <strong>{car.title}</strong> - {car.price} EUR {" "}
              {car.year && <>| {car.year}</>} {car.km && <>| {car.km}</>} {car.cc && <>| {car.cc}</>} {car.hp && <>| {car.hp}</>}{" "}
              <a href={car.link || car.url} target="_blank" rel="noreferrer">
                Link
              </a>
            </li>
          ))}
        </ul>
      </div>
  );
}

export default App;
