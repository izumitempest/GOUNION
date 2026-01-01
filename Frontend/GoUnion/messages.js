// Navigation toggle
function toggleMenu() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
    
    const menuToggle = document.querySelector('.menu-toggle');
    if (navLinks.classList.contains('active')) {
        menuToggle.innerHTML = '✕';
        menuToggle.style.transform = 'rotate(180deg)';
    } else {
        menuToggle.innerHTML = '☰';
        menuToggle.style.transform = 'rotate(0)';
    }
}

// Close menu when clicking outside
document.addEventListener('click', function(event) {
    const navLinks = document.getElementById('navLinks');
    const menuToggle = document.querySelector('.menu-toggle');
    
    if (!navLinks.contains(event.target) && !menuToggle.contains(event.target)) {
        navLinks.classList.remove('active');
        menuToggle.innerHTML = '☰';
        menuToggle.style.transform = 'rotate(0)';
    }
});

// Conversation selection
document.addEventListener('DOMContentLoaded', function() {
    // Select conversation
    const conversations = document.querySelectorAll('.conversation');
    conversations.forEach(conv => {
        conv.addEventListener('click', function() {
            // Remove active class from all conversations
            conversations.forEach(c => c.classList.remove('active'));
            // Add active class to clicked conversation
            this.classList.add('active');
            
            // Update chat header with selected conversation info
            const convName = this.querySelector('h3').textContent;
            const convAvatar = this.querySelector('.avatar img').src;
            updateChatHeader(convName, convAvatar);
            
            // Show typing indicator briefly
            simulateTyping();
        });
    });
    
    // Send message functionality
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendMessage');
    const messagesContainer = document.getElementById('messagesContainer');
    
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            // Create new message element
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message sent';
            messageDiv.innerHTML = `
                <div class="message-content">
                    <p>${message}</p>
                </div>
                <div class="message-meta">
                    <span class="message-time">${getCurrentTime()}</span>
                    <i class="fas fa-check-double read-receipt"></i>
                </div>
            `;
            
            // Add to messages container
            messagesContainer.appendChild(messageDiv);
            
            // Clear input
            messageInput.value = '';
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            // Simulate reply after delay
            setTimeout(simulateReply, 1500);
            
            // Show notification
            showNotification('Message sent');
        }
    }
    
    // Send on button click
    sendBtn.addEventListener('click', sendMessage);
    
    // Send on Enter key
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Search functionality
    const searchInput = document.getElementById('searchMessages');
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const conversations = document.querySelectorAll('.conversation');
        
        conversations.forEach(conv => {
            const convName = conv.querySelector('h3').textContent.toLowerCase();
            const lastMessage = conv.querySelector('.last-message').textContent.toLowerCase();
            
            if (convName.includes(searchTerm) || lastMessage.includes(searchTerm)) {
                conv.style.display = 'flex';
                conv.style.animation = 'slideIn 0.3s ease';
            } else {
                conv.style.display = 'none';
            }
        });
    });
    
    // Initialize chat
    initializeChat();
    
    // DEMO MODE WARNING
    showNotification("Demo Mode: Messaging backend is not yet connected.", "info");
});

// Simulate typing indicator
function simulateTyping() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.classList.add('active');
    
    setTimeout(() => {
        typingIndicator.classList.remove('active');
    }, 2000);
}

// Simulate reply from other user
function simulateReply() {
    const messagesContainer = document.getElementById('messagesContainer');
    const replies = [
        "Thanks for your message!",
        "That's a great idea!",
        "Let me think about that...",
        "Can you tell me more?",
        "I completely agree with you!"
    ];
    
    const randomReply = replies[Math.floor(Math.random() * replies.length)];
    
    const replyDiv = document.createElement('div');
    replyDiv.className = 'message received';
    replyDiv.innerHTML = `
        <div class="message-sender">
            <img src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=400&q=80" alt="Alex">
            <span>Alex Johnson</span>
        </div>
        <div class="message-content">
            <p>${randomReply}</p>
        </div>
        <div class="message-time">${getCurrentTime()}</div>
    `;
    
    messagesContainer.appendChild(replyDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Get current time in HH:MM format
function getCurrentTime() {
    const now = new Date();
    return now.getHours().toString().padStart(2, '0') + ':' + 
           now.getMinutes().toString().padStart(2, '0');
}

// Update chat header
function updateChatHeader(name, avatar) {
    const chatHeader = document.querySelector('.chat-info');
    chatHeader.innerHTML = `
        <div class="chat-avatar">
            <img src="${avatar}" alt="${name}">
            <span class="online-indicator"></span>
        </div>
        <div>
            <h2>${name}</h2>
            <p class="chat-status">Online • 12 members</p>
        </div>
    `;
}

// Toggle members sidebar
function toggleMembers() {
    const membersSidebar = document.getElementById('membersSidebar');
    membersSidebar.classList.toggle('active');
    
    if (window.innerWidth <= 768) {
        document.body.style.overflow = membersSidebar.classList.contains('active') ? 'hidden' : 'auto';
    }
}

// Filter toggle
function toggleFilter() {
    const filterBtn = document.querySelector('.filter-btn');
    filterBtn.classList.toggle('active');
    
    if (filterBtn.classList.contains('active')) {
        filterBtn.innerHTML = '<i class="fas fa-times"></i>';
        showNotification('Filters applied');
    } else {
        filterBtn.innerHTML = '<i class="fas fa-filter"></i>';
    }
}

// New message button
function newMessage() {
    showNotification('Starting new conversation...');
    
    // In a real app, this would open a modal to select recipients
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>New Message</h3>
            <input type="text" placeholder="Search contacts..." class="modal-search">
            <div class="contacts-list">
                <!-- Contacts would be populated here -->
            </div>
            <div class="modal-actions">
                <button onclick="this.closest('.modal').remove()">Cancel</button>
                <button onclick="startNewChat()">Start Chat</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Initialize chat
function initializeChat() {
    const messagesContainer = document.getElementById('messagesContainer');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Add CSS for modal
    const style = document.createElement('style');
    style.textContent = `
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
            animation: fadeIn 0.3s ease;
        }
        
        .modal-content {
            background: rgba(25, 25, 35, 0.95);
            border-radius: 20px;
            padding: 2rem;
            width: 90%;
            max-width: 500px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        
        .modal-content h3 {
            color: white;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }
        
        .modal-search {
            width: 100%;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            margin-bottom: 1.5rem;
        }
        
        .modal-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 2rem;
        }
        
        .modal-actions button {
            padding: 0.8rem 1.5rem;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .modal-actions button:first-child {
            background: rgba(255, 255, 255, 0.1);
            color: #b0b0c0;
        }
        
        .modal-actions button:last-child {
            background: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%);
            color: white;
        }
        
        .modal-actions button:hover {
            transform: translateY(-2px);
        }
    `;
    document.head.appendChild(style);
}

// Show notification
function showNotification(message) {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease, fadeOut 0.3s ease 2.7s;
        animation-fill-mode: forwards;
        max-width: 300px;
        font-weight: 500;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove notification
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Add fadeOut animation for notifications
const notificationStyle = document.createElement('style');
notificationStyle.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(notificationStyle);

// Handle window resize
window.addEventListener('resize', function() {
    const membersSidebar = document.getElementById('membersSidebar');
    if (window.innerWidth <= 768 && membersSidebar.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = 'auto';
    }
});

// Simulate online status changes
setInterval(() => {
    const indicators = document.querySelectorAll('.online-indicator');
    indicators.forEach(indicator => {
        if (Math.random() > 0.7) {
            indicator.classList.toggle('offline');
        }
    });
}, 10000);