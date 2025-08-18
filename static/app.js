// Copy message to clipboard
function copyMessage(button) {
    // Find the textarea in the same message container
    const messageContainer = button.closest('.mb-4');
    const textarea = messageContainer.querySelector('.message-text');
    const text = textarea.value;
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.classList.remove('bg-gray-100', 'hover:bg-gray-200');
        button.classList.add('bg-green-100', 'text-green-700', 'border-green-300');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('bg-green-100', 'text-green-700', 'border-green-300');
            button.classList.add('bg-gray-100', 'hover:bg-gray-200');
        }, 2000);
    }).catch(() => {
        alert('Failed to copy message');
    });
}

// Copy message and open Facebook Messenger
function copyAndOpenMessenger(button, messengerLink) {
    // Find the textarea in the same message container
    const messageContainer = button.closest('.mb-4');
    const textarea = messageContainer.querySelector('.message-text');
    const text = textarea.value;
    
    // First copy the message
    navigator.clipboard.writeText(text).then(() => {
        // Show feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/></svg>Copied & Opening...';
        button.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        button.classList.add('bg-green-600');
        
        // Then open Facebook Messenger
        window.open(messengerLink, '_blank');
        
        // Reset button after 2 seconds
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-600');
            button.classList.add('bg-blue-600', 'hover:bg-blue-700');
        }, 2000);
    }).catch(() => {
        alert('Failed to copy message to clipboard');
    });
}

// Edit address functionality
function editAddress(guestId) {
    const displayDiv = document.getElementById(`address-display-${guestId}`);
    const editDiv = document.getElementById(`address-edit-${guestId}`);
    
    displayDiv.classList.add('hidden');
    editDiv.classList.remove('hidden');
    
    // Focus on input
    const input = document.getElementById(`address-input-${guestId}`);
    input.focus();
    input.select();
}

function cancelEditAddress(guestId) {
    const displayDiv = document.getElementById(`address-display-${guestId}`);
    const editDiv = document.getElementById(`address-edit-${guestId}`);
    
    displayDiv.classList.remove('hidden');
    editDiv.classList.add('hidden');
    
    // Reset input to original value
    const input = document.getElementById(`address-input-${guestId}`);
    const originalValue = displayDiv.textContent.trim();
    input.value = originalValue === 'No address on file' ? '' : originalValue;
}

async function saveAddress(guestId) {
    const input = document.getElementById(`address-input-${guestId}`);
    const newAddress = input.value.trim();
    
    try {
        const response = await fetch(`/update-guest-address/${guestId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ address: newAddress })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update display
            const displayDiv = document.getElementById(`address-display-${guestId}`);
            const editDiv = document.getElementById(`address-edit-${guestId}`);
            
            displayDiv.textContent = newAddress || 'No address on file';
            displayDiv.className = newAddress ? '' : 'text-gray-400 italic';
            
            displayDiv.classList.remove('hidden');
            editDiv.classList.add('hidden');
            
            // Update status badge
            const card = document.querySelector(`[data-guest-id="${guestId}"]`);
            const badge = card.querySelector('.inline-flex');
            
            badge.textContent = data.new_status.replace('_', ' ').split(' ').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
            
            // Update badge colors
            badge.classList.remove('bg-yellow-100', 'text-yellow-800', 'bg-green-100', 'text-green-800');
            if (data.new_status === 'has_address') {
                badge.classList.add('bg-green-100', 'text-green-800');
            } else {
                badge.classList.add('bg-yellow-100', 'text-yellow-800');
            }
            
            // Update edit button text
            const editButton = displayDiv.parentElement.querySelector('button');
            editButton.textContent = newAddress ? 'Edit' : 'Add';
            
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert('Failed to update address');
    }
}

// Mark guest with action via AJAX
async function markGuest(guestId, action) {
    try {
        const response = await fetch(`/mark/${guestId}/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update the status badge
            const card = document.querySelector(`[data-guest-id="${guestId}"]`);
            const badge = card.querySelector('.inline-flex');
            
            // Update badge text and classes
            badge.textContent = data.new_status.replace('_', ' ').split(' ').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
            
            // Remove old color classes
            badge.classList.remove('bg-yellow-100', 'text-yellow-800', 'bg-blue-100', 'text-blue-800', 'bg-gray-100', 'text-gray-800');
            
            // Add new color classes
            if (data.new_status === 'requested') {
                badge.classList.add('bg-blue-100', 'text-blue-800');
            } else if (data.new_status === 'not_on_fb') {
                badge.classList.add('bg-gray-100', 'text-gray-800');
            }
            
            // Hide action buttons if guest is marked
            const buttons = card.querySelector('.flex.gap-2');
            if (buttons) {
                buttons.style.display = 'none';
            }
            
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert('Failed to update guest status');
    }
}

// Keyboard shortcuts for review page
document.addEventListener('DOMContentLoaded', function() {
    let focusedCard = null;
    
    // Track focused card
    document.querySelectorAll('.guest-card').forEach(card => {
        card.addEventListener('focus', () => {
            focusedCard = card;
            card.classList.add('ring-2', 'ring-primary');
        });
        
        card.addEventListener('blur', () => {
            card.classList.remove('ring-2', 'ring-primary');
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (!focusedCard) return;
        
        const guestId = parseInt(focusedCard.dataset.guestId);
        
        switch (e.key.toLowerCase()) {
            case 'enter':
                e.preventDefault();
                const messengerLink = focusedCard.querySelector('a[href*="facebook.com/messages"]');
                if (messengerLink) {
                    window.open(messengerLink.href, '_blank');
                }
                break;
                
            case 'c':
                e.preventDefault();
                const copyButton = focusedCard.querySelector('button[onclick*="copyMessage"]');
                if (copyButton) {
                    copyMessage(copyButton);
                }
                break;
                
            case 'r':
                e.preventDefault();
                const requestButton = focusedCard.querySelector('button[onclick*="requested"]');
                if (requestButton) {
                    markGuest(guestId, 'requested');
                }
                break;
                
            case 'n':
                e.preventDefault();
                const notOnFbButton = focusedCard.querySelector('button[onclick*="not_on_fb"]');
                if (notOnFbButton) {
                    markGuest(guestId, 'not_on_fb');
                }
                break;
        }
    });
    
    // Auto-focus first card if none focused
    const firstCard = document.querySelector('.guest-card');
    if (firstCard) {
        firstCard.focus();
    }
});