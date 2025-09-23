/**
 * WebSocket Client for Reboot-Reclaim Application
 * Handles real-time communication with the server
 */

class RebootReclaimWebSocket {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.eventListeners = {};
    }

    /**
     * Connect to the WebSocket server
     */
    connect() {
        try {
            // Use Socket.IO client
            this.socket = io('http://localhost:5000', {
                transports: ['websocket', 'polling']
            });

            this.socket.on('connect', () => {
                console.log('Connected to Reboot-Reclaim server');
                this.connected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;

                this.emit('connected');
                this.showNotification('Connected to server', 'success');
            });

            this.socket.on('disconnect', (reason) => {
                console.log('Disconnected from server:', reason);
                this.connected = false;
                this.emit('disconnected', { reason });
                this.showNotification('Disconnected from server', 'warning');

                if (reason === 'io server disconnect') {
                    // Server disconnected us, try to reconnect
                    this.reconnect();
                }
            });

            this.socket.on('connect_error', (error) => {
                console.error('Connection error:', error);
                this.emit('connection_error', { error });
                this.showNotification('Connection error occurred', 'error');
            });

            // Handle system status updates
            this.socket.on('status', (data) => {
                console.log('Status update:', data);
                this.emit('status', data);
            });

            // Handle blockchain status updates
            this.socket.on('blockchain_status', (data) => {
                console.log('Blockchain status:', data);
                this.emit('blockchain_status', data);
                this.updateBlockchainDisplay(data);
            });

            // Handle certificate verification results
            this.socket.on('verification_result', (data) => {
                console.log('Verification result:', data);
                this.emit('verification_result', data);
                this.showVerificationResult(data);
            });

            // Handle device status updates
            this.socket.on('device_status', (data) => {
                console.log('Device status:', data);
                this.emit('device_status', data);
                this.updateDeviceDisplay(data);
            });

            // Handle wipe progress updates
            this.socket.on('wipe_progress', (data) => {
                console.log('Wipe progress:', data);
                this.emit('wipe_progress', data);
                this.updateProgressDisplay(data);
            });

            // Handle wipe completion
            this.socket.on('wipe_complete', (data) => {
                console.log('Wipe complete:', data);
                this.emit('wipe_complete', data);
                this.showNotification('Device wipe completed successfully!', 'success');
            });

            // Handle errors
            this.socket.on('error', (data) => {
                console.error('Socket error:', data);
                this.emit('error', data);
                this.showNotification(data.message || 'An error occurred', 'error');
            });

            // Handle pong responses
            this.socket.on('pong', (data) => {
                console.log('Pong received:', data);
                this.emit('pong', data);
            });

        } catch (error) {
            console.error('Failed to connect:', error);
            this.showNotification('Failed to connect to server', 'error');
        }
    }

    /**
     * Disconnect from the WebSocket server
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.connected = false;
        }
    }

    /**
     * Attempt to reconnect to the server
     */
    reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.showNotification('Max reconnection attempts reached', 'error');
            return;
        }

        this.reconnectAttempts++;
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        setTimeout(() => {
            this.connect();
        }, this.reconnectDelay);

        // Exponential backoff
        this.reconnectDelay *= 2;
    }

    /**
     * Request blockchain status
     */
    requestBlockchainStatus() {
        if (this.socket && this.connected) {
            this.socket.emit('request_blockchain_status');
        } else {
            console.warn('Not connected to server');
            this.showNotification('Not connected to server', 'warning');
        }
    }

    /**
     * Request certificate verification
     */
    verifyCertificate(certificateId) {
        if (this.socket && this.connected) {
            this.socket.emit('request_certificate_verification', {
                certificate_id: certificateId
            });
        } else {
            console.warn('Not connected to server');
            this.showNotification('Not connected to server', 'warning');
        }
    }

    /**
     * Request device status
     */
    requestDeviceStatus() {
        if (this.socket && this.connected) {
            this.socket.emit('request_device_status');
        } else {
            console.warn('Not connected to server');
            this.showNotification('Not connected to server', 'warning');
        }
    }

    /**
     * Start wipe process
     */
    startWipeProcess(deviceId, wipeMethod = 'Standard Wipe') {
        if (this.socket && this.connected) {
            this.socket.emit('start_wipe_process', {
                device_id: deviceId,
                wipe_method: wipeMethod
            });
        } else {
            console.warn('Not connected to server');
            this.showNotification('Not connected to server', 'warning');
        }
    }

    /**
     * Send ping to server
     */
    ping() {
        if (this.socket && this.connected) {
            this.socket.emit('ping');
        }
    }

    /**
     * Add event listener
     */
    on(event, callback) {
        if (!this.eventListeners[event]) {
            this.eventListeners[event] = [];
        }
        this.eventListeners[event].push(callback);
    }

    /**
     * Remove event listener
     */
    off(event, callback) {
        if (this.eventListeners[event]) {
            const index = this.eventListeners[event].indexOf(callback);
            if (index > -1) {
                this.eventListeners[event].splice(index, 1);
            }
        }
    }

    /**
     * Emit event to listeners
     */
    emit(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in event listener:', error);
                }
            });
        }
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;

        // Add styles if not already added
        if (!document.getElementById('websocket-notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'websocket-notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 20px;
                    border-radius: 5px;
                    color: white;
                    font-weight: bold;
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    animation: slideIn 0.3s ease-out;
                }
                .notification-success { background-color: #28a745; }
                .notification-error { background-color: #dc3545; }
                .notification-warning { background-color: #ffc107; color: black; }
                .notification-info { background-color: #007bff; }
                .notification button {
                    background: none;
                    border: none;
                    color: inherit;
                    cursor: pointer;
                    font-size: 20px;
                    line-height: 1;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideIn 0.3s ease-out reverse';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    /**
     * Update blockchain display
     */
    updateBlockchainDisplay(data) {
        const blockchainContainer = document.getElementById('blockchain-status');
        if (blockchainContainer) {
            blockchainContainer.innerHTML = `
                <div class="blockchain-info">
                    <h3>Blockchain Status</h3>
                    <p>Total Certificates: ${data.total_certificates}</p>
                    <p>Chain Valid: ${data.chain_valid ? '✅' : '❌'}</p>
                    <p>Last Updated: ${new Date(data.timestamp).toLocaleTimeString()}</p>
                </div>
            `;
        }
    }

    /**
     * Show verification result
     */
    showVerificationResult(data) {
        const resultContainer = document.getElementById('verification-result');
        if (resultContainer) {
            const status = data.verified ? 'success' : 'error';
            const message = data.message || (data.verified ? 'Certificate verified successfully' : 'Verification failed');

            resultContainer.innerHTML = `
                <div class="verification-result ${status}">
                    <h3>Verification Result</h3>
                    <p><strong>Certificate ID:</strong> ${data.certificate_id}</p>
                    <p><strong>Status:</strong> ${data.verified ? '✅ Verified' : '❌ Not Verified'}</p>
                    <p><strong>Chain Valid:</strong> ${data.chain_valid ? '✅' : '❌'}</p>
                    <p><strong>Message:</strong> ${message}</p>
                    <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                </div>
            `;
        }
    }

    /**
     * Update device display
     */
    updateDeviceDisplay(data) {
        const deviceContainer = document.getElementById('device-status');
        if (deviceContainer) {
            const devicesHtml = data.devices.map(device => `
                <div class="device-item">
                    <h4>${device.model}</h4>
                    <p><strong>ID:</strong> ${device.id}</p>
                    <p><strong>Capacity:</strong> ${device.capacity}</p>
                    <p><strong>Status:</strong> ${device.status}</p>
                </div>
            `).join('');

            deviceContainer.innerHTML = `
                <div class="devices-info">
                    <h3>Device Status</h3>
                    ${devicesHtml}
                    <p>Last Updated: ${new Date(data.timestamp).toLocaleTimeString()}</p>
                </div>
            `;
        }
    }

    /**
     * Update progress display
     */
    updateProgressDisplay(data) {
        const progressContainer = document.getElementById('wipe-progress');
        if (progressContainer) {
            progressContainer.innerHTML = `
                <div class="progress-info">
                    <h3>Wipe Progress</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${data.progress}%"></div>
                    </div>
                    <p>${data.progress}% - ${data.message}</p>
                    <p>Device: ${data.device_id}</p>
                </div>
            `;
        }
    }
}

// Create global instance
const rebootReclaimWS = new RebootReclaimWebSocket();

// Export for use in other modules
window.RebootReclaimWebSocket = RebootReclaimWebSocket;
window.rebootReclaimWS = rebootReclaimWS;
