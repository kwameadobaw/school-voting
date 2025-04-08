document.addEventListener('DOMContentLoaded', function() {
    const candidatesList = document.getElementById('candidates-list');
    const submitVoteBtn = document.getElementById('submit-vote-btn');
    const votingMessage = document.getElementById('voting-message');
    const positionIndicators = document.querySelectorAll('.position-indicator');
    
    let selectedCandidate = null;
    
    // Load candidates for the current position
    if (candidatesList) {
        const positionId = candidatesList.dataset.positionId;
        loadCandidates(positionId);
    }
    
    // Position indicator click handling
    positionIndicators.forEach(indicator => {
        indicator.addEventListener('click', function() {
            const positionId = this.dataset.positionId;
            const isCurrent = this.classList.contains('current');
            const isCompleted = this.classList.contains('completed');
            
            // Only allow clicking on the current position
            if (isCurrent && !isCompleted) {
                loadCandidates(positionId);
            }
        });
    });
    
    function loadCandidates(positionId) {
        if (!positionId) return;
        
        // Show loading
        candidatesList.innerHTML = '<div class="loading">Loading candidates...</div>';
        
        // Fetch candidates for selected position
        fetch('/get_candidates/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ position_id: positionId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayCandidates(data.candidates);
            } else {
                showMessage(data.message, 'error');
                candidatesList.innerHTML = '<div class="error">Error loading candidates</div>';
            }
        })
        .catch(error => {
            showMessage('An error occurred. Please try again.', 'error');
            candidatesList.innerHTML = '<div class="error">Error loading candidates</div>';
            console.error('Error:', error);
        });
    }
    
    function displayCandidates(candidates) {
        candidatesList.innerHTML = '';
        selectedCandidate = null;
        submitVoteBtn.disabled = true;
        
        if (candidates.length === 0) {
            candidatesList.innerHTML = '<div class="no-candidates">No candidates available for this position</div>';
            return;
        }
        
        candidates.forEach(candidate => {
            const candidateItem = document.createElement('div');
            candidateItem.className = 'candidate-item';
            candidateItem.dataset.id = candidate.id;
            
            let photoHtml = '';
            if (candidate.photo_url) {
                photoHtml = `
                    <div class="candidate-photo">
                        <img src="${candidate.photo_url}" alt="${candidate.name}">
                    </div>
                `;
            } else {
                photoHtml = `
                    <div class="candidate-photo">
                        <img src="/static/images/default-avatar.png" alt="${candidate.name}">
                    </div>
                `;
            }
            
            candidateItem.innerHTML = `
                ${photoHtml}
                <div class="candidate-name">${candidate.name}</div>
            `;
            
            candidateItem.addEventListener('click', function() {
                // Deselect all candidates
                document.querySelectorAll('.candidate-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // Select clicked candidate
                this.classList.add('selected');
                selectedCandidate = this.dataset.id;
                submitVoteBtn.disabled = false;
            });
            
            candidatesList.appendChild(candidateItem);
        });
    }
    
    if (submitVoteBtn) {
        submitVoteBtn.addEventListener('click', function() {
            if (!selectedCandidate) {
                showMessage('Please select a candidate', 'error');
                return;
            }
            
            const positionId = candidatesList.dataset.positionId;
            
            // Submit vote
            fetch('/submit_vote/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    position_id: positionId,
                    candidate_id: selectedCandidate
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showMessage(data.message, 'success');
                    
                    // Update progress bar
                    const progressFill = document.querySelector('.progress-fill');
                    if (progressFill) {
                        progressFill.style.width = data.progress + '%';
                    }
                    
                    // Update progress text
                    const percentage = document.querySelector('.percentage');
                    if (percentage) {
                        percentage.textContent = Math.round(data.progress) + '%';
                    }
                    
                    // Mark current position as completed
                    document.querySelectorAll('.position-indicator').forEach(indicator => {
                        if (indicator.classList.contains('current')) {
                            indicator.classList.remove('current');
                            indicator.classList.add('completed');
                        }
                    });
                    
                    // If voting is complete, redirect after a delay
                    if (data.complete) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    } else if (data.next_position) {
                        // Set next position as current
                        document.querySelectorAll('.position-indicator').forEach(indicator => {
                            if (indicator.dataset.positionId == data.next_position.id) {
                                indicator.classList.add('current');
                                
                                // Update position title
                                const positionTitle = document.querySelector('.position-title');
                                if (positionTitle) {
                                    positionTitle.textContent = data.next_position.title;
                                }
                                
                                // Update candidates list data attribute
                                candidatesList.dataset.positionId = data.next_position.id;
                                
                                // Load candidates for next position
                                setTimeout(() => {
                                    loadCandidates(data.next_position.id);
                                }, 1000);
                            }
                        });
                    }
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(error => {
                showMessage('An error occurred. Please try again.', 'error');
                console.error('Error:', error);
            });
        });
    }
    
    function showMessage(message, type) {
        votingMessage.textContent = message;
        votingMessage.className = 'voting-message ' + type;
        votingMessage.style.display = 'block';
        
        // Clear message after 5 seconds
        setTimeout(() => {
            votingMessage.textContent = '';
            votingMessage.className = 'voting-message';
            votingMessage.style.display = 'none';
        }, 5000);
    }
});