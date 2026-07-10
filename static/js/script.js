document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("recommendation-form");
    const skillSelects = document.querySelectorAll(".skill-select");
    const validationMessage = document.getElementById("validation-message");
    const submitBtn = document.getElementById("submit-btn");
    const statusBadge = document.getElementById("status-badge");
    const resultsContainer = document.getElementById("results-container");

    let allSkills = [];

    // Fetch and populate available skills
    fetch("/api/skills")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to load skills from server.");
            }
            return response.json();
        })
        .then(data => {
            allSkills = data.skills;
            populateDropdowns();
        })
        .catch(err => {
            showGlobalError("Failed to initialize skills. Is the server running?");
        });

    // Populate dropdowns with skills
    function populateDropdowns() {
        skillSelects.forEach(select => {
            // Keep the first default option
            const defaultOption = select.options[0];
            select.innerHTML = "";
            select.appendChild(defaultOption);

            allSkills.forEach(skill => {
                const option = document.createElement("option");
                option.value = skill;
                option.textContent = skill;
                select.appendChild(option);
            });
        });
    }

    // Dynamic filtering to prevent duplicate selection
    skillSelects.forEach(select => {
        select.addEventListener("change", () => {
            clearError();
            updateSelectOptions();
        });
    });

    function updateSelectOptions() {
        // Collect current selections
        const selectedValues = Array.from(skillSelects).map(s => s.value).filter(val => val !== "");

        skillSelects.forEach(select => {
            const currentValue = select.value;
            Array.from(select.options).forEach(option => {
                if (option.value === "") return; // Don't disable the placeholder
                
                // Disable if selected in another dropdown, but keep enabled if it's the current selection of this dropdown
                if (selectedValues.includes(option.value) && option.value !== currentValue) {
                    option.disabled = true;
                } else {
                    option.disabled = false;
                }
            });
        });
    }

    // Submit handler
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        clearError();

        const selectedSkills = Array.from(skillSelects).map(s => s.value).filter(val => val !== "");

        // Enforce exact 3 skills selection constraint
        if (selectedSkills.length !== 3) {
            showError("Please select exactly 3 different skills.");
            return;
        }

        // Set UI loading state
        submitBtn.disabled = true;
        submitBtn.textContent = "Matching...";
        statusBadge.textContent = "Processing";
        statusBadge.className = "badge badge-active";

        // AJAX POST request
        fetch("/api/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ skills: selectedSkills })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || "A server error occurred.");
                });
            }
            return response.json();
        })
        .then(data => {
            renderRecommendations(data.recommendations);
            statusBadge.textContent = "Success";
            statusBadge.className = "badge badge-success";
        })
        .catch(err => {
            showError(err.message);
            statusBadge.textContent = "Error";
            statusBadge.className = "badge badge-error";
            resultsContainer.innerHTML = `
                <div class="placeholder-state">
                    <p>Recommendation request failed. Check input parameters or server status.</p>
                </div>
            `;
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = "Find Matches";
        });
    });

    // Render results dynamically
    function renderRecommendations(recommendations) {
        if (!recommendations || recommendations.length === 0) {
            resultsContainer.innerHTML = `
                <div class="placeholder-state">
                    <p>No matching roles found.</p>
                </div>
            `;
            return;
        }

        resultsContainer.innerHTML = "";

        recommendations.forEach(rec => {
            const card = document.createElement("div");
            card.className = "recommendation-card";

            // Map skills array to tags
            const tagsHTML = rec.skills.map(skill => `<span class="tag">${escapeHTML(skill)}</span>`).join("");

            card.innerHTML = `
                <div class="card-header">
                    <h3 class="job-title">${escapeHTML(rec.title)}</h3>
                    <span class="match-score">${rec.match_percentage}% Match</span>
                </div>
                <div class="skill-tags">
                    ${tagsHTML}
                </div>
            `;
            resultsContainer.appendChild(card);
        });
    }

    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    function showError(msg) {
        validationMessage.textContent = msg;
        validationMessage.classList.remove("hidden");
    }

    function clearError() {
        validationMessage.textContent = "";
        validationMessage.classList.add("hidden");
    }

    function showGlobalError(msg) {
        showError(msg);
        statusBadge.textContent = "Offline";
        statusBadge.className = "badge badge-error";
    }
});
