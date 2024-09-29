async function fetchPets() {
    const response = await fetch('https://your-backend-url/pets'); // Replace with your backend URL
    const pets = await response.json();
    const petsDiv = document.getElementById('pets');
    petsDiv.innerHTML = pets.map(pet => `<p>${pet.name} - ${pet.breed}</p>`).join('');
}

fetchPets();
