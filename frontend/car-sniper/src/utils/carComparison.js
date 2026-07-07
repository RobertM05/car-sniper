const COMPARE_KEY = 'carsniper_compare';
const MAX_COMPARE = 3;

export function getComparedCars() {
    try {
        return JSON.parse(localStorage.getItem(COMPARE_KEY) || '[]');
    } catch {
        return [];
    }
}

export function toggleCompareCar(car) {
    const cars = getComparedCars();
    const exists = cars.findIndex(c => c.id === car.id || c.link === car.link);
    if (exists >= 0) {
        cars.splice(exists, 1);
    } else if (cars.length < MAX_COMPARE) {
        cars.push({
            id: car.id || car.link,
            title: car.title || car.name,
            price: car.price,
            year: car.year,
            km: car.km,
            fuel: car.fuel,
            transmission: car.transmission || car.trans,
            deal_score: car.deal_score,
            link: car.link || car.url,
            image: car.image,
        });
    }
    localStorage.setItem(COMPARE_KEY, JSON.stringify(cars));
    return cars;
}

export function clearComparedCars() {
    localStorage.removeItem(COMPARE_KEY);
}

export function isCarCompared(car) {
    const cars = getComparedCars();
    return cars.some(c => c.id === car.id || c.link === (car.link || car.url));
}
