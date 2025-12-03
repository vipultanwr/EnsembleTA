document.addEventListener('DOMContentLoaded', () => {
    const dashboardDiv = document.getElementById('dashboard');
    const resultsContentDiv = document.getElementById('results-content');
    let allResultsData = [];

    // Function to fetch data
    async function fetchResultsData() {
        try {
            const response = await fetch('results_data.json');
            allResultsData = await response.json();
            populateDropdowns(allResultsData);
            displayResults(); // Display initial results
        } catch (error) {
            console.error('Error fetching results data:', error);
            resultsContentDiv.innerHTML = '<p>Error loading results. Please ensure results_data.json exists and is accessible.</p>';
        }
    }

    // Function to get unique values for a parameter
    function getUniqueValues(data, param) {
        const values = data.map(item => item.params[param]);
        return [...new Set(values)].sort();
    }

    // Function to create and populate dropdowns
    function populateDropdowns(data) {
        const params = ['asset', 'timeframe', 'top_n', 'shifts'];
        const dropdowns = {};

        params.forEach(param => {
            const label = document.createElement('label');
            label.setAttribute('for', param);
            label.textContent = param.replace('_', ' ').toUpperCase() + ': ';
            dashboardDiv.appendChild(label);

            const select = document.createElement('select');
            select.id = param;
            select.addEventListener('change', displayResults);
            dashboardDiv.appendChild(select);
            dropdowns[param] = select;

            const uniqueValues = getUniqueValues(data, param);
            uniqueValues.forEach(value => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = value;
                select.appendChild(option);
            });
        });
    }

    // Function to display results based on selected dropdowns
    function displayResults() {
        const selectedAsset = document.getElementById('asset')?.value;
        const selectedTimeframe = document.getElementById('timeframe')?.value;
        const selectedTopN = document.getElementById('top_n')?.value;
        const selectedShifts = document.getElementById('shifts')?.value;

        const filteredResults = allResultsData.filter(item => {
            return (!selectedAsset || item.params.asset === selectedAsset) &&
                   (!selectedTimeframe || item.params.timeframe === selectedTimeframe) &&
                   (!selectedTopN || item.params.top_n === selectedTopN) &&
                   (!selectedShifts || item.params.shifts === selectedShifts);
        });

        resultsContentDiv.innerHTML = ''; // Clear previous results

        if (filteredResults.length > 0) {
            const result = filteredResults[0]; // Display the first matching result
            resultsContentDiv.innerHTML += `<h2>Results for: ${result.folder}</h2>`;
            result.files.forEach(file => {
                const filePath = `results/${result.folder}/${file}`;
                if (file.endsWith('.png') || file.endsWith('.jpg') || file.endsWith('.jpeg') || file.endsWith('.gif')) {
                    resultsContentDiv.innerHTML += `<img src="${filePath}" alt="${file}" style="max-width: 100%; height: auto; margin-bottom: 1rem;">`;
                } else if (file.endsWith('.csv')) {
                    // For CSVs, we might want to display a link or a preview
                    resultsContentDiv.innerHTML += `<p><a href="${filePath}" target="_blank">${file}</a></p>`;
                } else {
                    resultsContentDiv.innerHTML += `<p>${file}</p>`;
                }
            });
        } else {
            resultsContentDiv.innerHTML = '<p>No results found for the selected criteria.</p>';
        }
    }

    fetchResultsData();
});