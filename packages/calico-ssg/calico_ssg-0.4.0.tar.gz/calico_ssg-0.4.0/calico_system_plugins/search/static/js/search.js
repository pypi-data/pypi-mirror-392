/**
 * Calico Search - Client-side search functionality
 */
(function() {
    'use strict';

    // Store search index once loaded
    let searchIndex = null;
    let documents = null;

    /**
     * Initialize the search functionality
     */
    function initSearch() {
        const searchForm = document.getElementById('search-form');
        const searchInput = document.getElementById('search-input');
        const searchResults = document.getElementById('search-results');
        const resultsContainer = document.getElementById('results-container');

        if (!searchForm || !searchInput || !searchResults || !resultsContainer) {
            return;
        }

        // Load the search index
        loadSearchIndex().then(() => {
            // Add event listeners
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const query = searchInput.value.trim();
                if (query.length > 0) {
                    const results = performSearch(query);
                    displayResults(results, resultsContainer);
                    searchResults.hidden = false;
                } else {
                    searchResults.hidden = true;
                }
            });

            // Add input event to handle changes
            searchInput.addEventListener('input', function() {
                const query = searchInput.value.trim();
                if (query.length > 0) {
                    const results = performSearch(query);
                    displayResults(results, resultsContainer);
                    searchResults.hidden = false;
                } else {
                    searchResults.hidden = true;
                }
            });
        }).catch(error => {
            console.error('Error loading search index:', error);
        });
    }

    /**
     * Load the search index
     */
    function loadSearchIndex() {
        return fetch('/calico-lunr.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                documents = data.documents;
                
                // Build the lunr index
                searchIndex = lunr(function() {
                    // Set up the reference field
                    this.ref(data.schema.ref);
                    
                    // Add the fields
                    data.schema.fields.forEach(field => {
                        const boost = data.schema.boost[field] || 1;
                        this.field(field, { boost: boost });
                    });
                    
                    // Add the documents
                    documents.forEach(doc => {
                        this.add(doc);
                    });
                });
                
                return searchIndex;
            });
    }

    /**
     * Perform search with the given query
     */
    function performSearch(query) {
        if (!searchIndex || !documents) {
            return [];
        }
        
        try {
            // Get the search results
            const searchResults = searchIndex.search(query);
            
            // Map the results to the original documents
            return searchResults.map(result => {
                const doc = documents.find(d => d.url === result.ref);
                return {
                    ...doc,
                    score: result.score
                };
            });
        } catch (e) {
            console.error('Search error:', e);
            return [];
        }
    }

    /**
     * Display the search results
     */
    function displayResults(results, container) {
        // Clear the container
        container.innerHTML = '';

        if (results.length === 0) {
            container.innerHTML = '<p>No results found.</p>';
            return;
        }

        // Create a list of results
        const list = document.createElement('ul');

        results.forEach(result => {
            const item = document.createElement('li');

            const link = document.createElement('a');
            link.href = result.url;
            link.textContent = result.title || result.url;

            item.appendChild(link);

            // Add excerpt if we have content
            if (result.content) {
                const excerpt = document.createElement('p');

                // Create a simple excerpt from the content
                const maxLength = 150;
                let content = result.content;
                if (content.length > maxLength) {
                    content = content.substring(0, maxLength) + '...';
                }

                excerpt.textContent = content;
                item.appendChild(excerpt);
            }

            list.appendChild(item);
        });

        container.appendChild(list);
    }

    // Initialize search when DOM is loaded
    document.addEventListener('DOMContentLoaded', initSearch);

})();