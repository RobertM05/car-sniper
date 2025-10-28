// Exemplu de utilizare în Frontend pentru sistemul cu generații

// 1. Obținerea generațiilor pentru un model
async function getGenerations(make, model) {
    const response = await fetch(`/api/generations/${make}/${model}`);
    const data = await response.json();
    return data.generations;
}

// 2. Obținerea anilor pentru o generație specifică
async function getGenerationYears(make, model, generation) {
    const response = await fetch(`/api/generation-years/${make}/${model}/${generation}`);
    const data = await response.json();
    return { min_year: data.min_year, max_year: data.max_year };
}

// 3. Căutare cu generație specifică
async function searchWithGeneration(make, model, generation, maxPrice) {
    const params = new URLSearchParams({
        make,
        model,
        max_price: maxPrice,
        generation,
        site: 'both'
    });
    
    const response = await fetch(`/api/search?${params}`);
    const data = await response.json();
    return data.results;
}

// 4. Exemplu de utilizare completă
async function demonstrateGenerationSearch() {
    console.log('🎯 DEMONSTRAȚIE CĂUTARE CU GENERAȚII');
    
    // Pasul 1: Utilizatorul selectează marca și modelul
    const make = 'bmw';
    const model = 'seria-3';
    
    console.log(`1. Utilizatorul selectează: ${make.toUpperCase()} ${model.toUpperCase()}`);
    
    // Pasul 2: Sistemul afișează generațiile disponibile
    const generations = await getGenerations(make, model);
    console.log('2. Generații disponibile:');
    generations.forEach(gen => {
        console.log(`   - ${gen.generation} (${gen.min_year}-${gen.max_year})`);
    });
    
    // Pasul 3: Utilizatorul selectează o generație
    const selectedGeneration = 'F30';
    console.log(`3. Utilizatorul selectează generația: ${selectedGeneration}`);
    
    // Pasul 4: Sistemul afișează intervalul de ani pentru generația selectată
    const years = await getGenerationYears(make, model, selectedGeneration);
    console.log(`4. Intervalul de ani pentru ${selectedGeneration}: ${years.min_year}-${years.max_year}`);
    
    // Pasul 5: Sistemul caută automat cu parametrii optimizați
    const results = await searchWithGeneration(make, model, selectedGeneration, 15000);
    console.log(`5. Rezultate găsite: ${results.length} mașini`);
    
    // Afișăm primele 3 rezultate
    results.slice(0, 3).forEach((car, index) => {
        console.log(`   ${index + 1}. ${car.title} - ${car.price}€ (${car.year})`);
    });
}

// 5. Componentă React pentru selecția generațiilor
function CarGenerationSelector({ make, model, onGenerationSelect }) {
    const [generations, setGenerations] = useState([]);
    const [selectedGeneration, setSelectedGeneration] = useState('');
    
    useEffect(() => {
        if (make && model) {
            getGenerations(make, model).then(setGenerations);
        }
    }, [make, model]);
    
    const handleGenerationChange = (generation) => {
        setSelectedGeneration(generation);
        onGenerationSelect(generation);
    };
    
    return (
        <div className="generation-selector">
            <label>Generația:</label>
            <select 
                value={selectedGeneration} 
                onChange={(e) => handleGenerationChange(e.target.value)}
            >
                <option value="">Selectează generația</option>
                {generations.map(gen => (
                    <option key={gen.generation} value={gen.generation}>
                        {gen.generation} ({gen.min_year}-{gen.max_year})
                    </option>
                ))}
            </select>
        </div>
    );
}

// 6. Exemplu de integrare în formularul principal
function CarSearchForm() {
    const [make, setMake] = useState('');
    const [model, setModel] = useState('');
    const [generation, setGeneration] = useState('');
    const [maxPrice, setMaxPrice] = useState(15000);
    const [results, setResults] = useState([]);
    
    const handleSearch = async () => {
        if (make && model) {
            const searchResults = await searchWithGeneration(make, model, generation, maxPrice);
            setResults(searchResults);
        }
    };
    
    return (
        <div className="car-search-form">
            <div>
                <label>Marca:</label>
                <input 
                    value={make} 
                    onChange={(e) => setMake(e.target.value)}
                    placeholder="Ex: BMW"
                />
            </div>
            
            <div>
                <label>Model:</label>
                <input 
                    value={model} 
                    onChange={(e) => setModel(e.target.value)}
                    placeholder="Ex: Seria 3"
                />
            </div>
            
            <CarGenerationSelector 
                make={make}
                model={model}
                onGenerationSelect={setGeneration}
            />
            
            <div>
                <label>Preț maxim (€):</label>
                <input 
                    type="number"
                    value={maxPrice} 
                    onChange={(e) => setMaxPrice(e.target.value)}
                />
            </div>
            
            <button onClick={handleSearch}>
                Caută cu Generația Selectată
            </button>
            
            <div className="results">
                {results.map((car, index) => (
                    <div key={index} className="car-result">
                        <h3>{car.title}</h3>
                        <p>Preț: {car.price}€</p>
                        <p>An: {car.year}</p>
                        <p>Km: {car.km}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

// 7. Exemplu de utilizare pentru API calls
const API_EXAMPLES = {
    // Obținerea generațiilor pentru BMW Seria 3
    getGenerations: 'GET /api/generations/bmw/seria-3',
    
    // Obținerea anilor pentru generația F30
    getGenerationYears: 'GET /api/generation-years/bmw/seria-3/F30',
    
    // Căutare cu generație specifică
    searchWithGeneration: 'GET /api/search?make=bmw&model=seria-3&generation=F30&max_price=15000',
    
    // Parametrii optimizați cu generație
    getOptimizedParams: 'GET /api/optimized-search-with-generation/bmw/seria-3?generation=F30'
};

export { 
    getGenerations, 
    getGenerationYears, 
    searchWithGeneration, 
    CarGenerationSelector, 
    CarSearchForm,
    API_EXAMPLES 
};
