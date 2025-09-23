// Devices Page JavaScript
class DeviceManager {
    constructor() {
        this.devices = [];
        this.selectedDevices = new Set();
        this.isWiping = false;
        this.wipeProgress = {};
        this.completedDevices = new Set();

        this.initializeEventListeners();
        this.loadDevices();
    }

    initializeEventListeners() {
        // Checkbox for understanding the risks
        document.getElementById('understand-checkbox')?.addEventListener('change', (e) => {
            const confirmBtn = document.getElementById('confirm-wipe-btn');
            if (confirmBtn) {
                confirmBtn.disabled = !e.target.checked;
            }
        });

        // Confirm wipe button
        document.getElementById('confirm-wipe-btn')?.addEventListener('click', () => {
            this.startWipeProcess();
        });
    }

    async loadDevices() {
        const loadingIndicator = document.getElementById('loading-indicator');
        const devicesContainer = document.getElementById('devices-container');
        const noDevices = document.getElementById('no-devices');

        try {
            if (loadingIndicator) loadingIndicator.style.display = 'block';
            if (devicesContainer) devicesContainer.innerHTML = '';

            const response = await fetch('/api/drives');
            const data = await response.json();

            this.devices = data;
            this.renderDevices();
            this.updateStatistics();

            if (loadingIndicator) loadingIndicator.style.display = 'none';

            if (this.devices.length === 0) {
                if (noDevices) noDevices.style.display = 'block';
            } else {
                if (noDevices) noDevices.style.display = 'none';
            }

        } catch (error) {
            console.error('Error loading devices:', error);
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            if (noDevices) noDevices.style.display = 'block';
        }
    }

    renderDevices() {
        const container = document.getElementById('devices-container');
        if (!container) return;

        container.innerHTML = '';

        this.devices.forEach(device => {
            const deviceCard = this.createDeviceCard(device);
            container.appendChild(deviceCard);
        });
    }

    createDeviceCard(device) {
        const cardDiv = document.createElement('div');
        cardDiv.className = `col-lg-6 col-xl-4 device-card ${this.getDeviceStatusClass(device)}`;
        if (this.selectedDevices.has(device.id)) {
            cardDiv.classList.add('selected');
        }

        const isWipeable = device.is_wipeable && device.status === 'Ready';

        cardDiv.innerHTML = `
            <div class="position-relative">
                ${isWipeable ? `
                    <div class="form-check device-checkbox">
                        <input class="form-check-input" type="checkbox" id="device-${device.id}"
                               ${this.selectedDevices.has(device.id) ? 'checked' : ''}
                               onchange="deviceManager.toggleDeviceSelection('${device.id}')">
                    </div>
                ` : ''}

                <div class="d-flex align-items-center">
                    <div class="device-icon ${device.type.toLowerCase()}">
                        <i class="fas ${this.getDeviceIcon(device.type)}"></i>
                    </div>
                    <div class="device-info flex-grow-1">
                        <h5>${device.model}</h5>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="badge bg-secondary">${device.type}</span>
                            <span class="device-serial">${device.serial_number}</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="device-status status-${device.status.toLowerCase().replace(' ', '-')}">
                                ${device.status}
                            </span>
                            <small class="text-muted">${device.capacity}</small>
                        </div>

                        ${device.status === 'Wiping in progress' && device.progress_percentage !== undefined ? `
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" style="width: ${device.progress_percentage}%">
                                    ${device.progress_percentage}%
                                </div>
                            </div>
                        ` : ''}

                        ${device.error_message ? `
                            <div class="alert alert-danger mt-2 py-2">
                                <small><i class="fas fa-exclamation-triangle"></i> ${device.error_message}</small>
                            </div>
                        ` : ''}

                        <div class="device-actions">
                            ${isWipeable ? `
                                <button class="btn btn-device btn-wipe btn-sm" onclick="deviceManager.wipeSingleDevice('${device.id}')">
                                    <i class="fas fa-eraser"></i> Wipe
                                </button>
                            ` : ''}
                            ${device.status === 'Wiped' ? `
                                <button class="btn btn-device btn-certificate btn-sm" onclick="deviceManager.downloadCertificate('${device.id}')">
                                    <i class="fas fa-certificate"></i> Certificate
                                </button>
                            ` : ''}
                            <button class="btn btn-device btn-info btn-sm" onclick="deviceManager.showDeviceInfo('${device.id}')">
                                <i class="fas fa-info-circle"></i> Info
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        return cardDiv;
    }

    getDeviceStatusClass(device) {
        const status = device.status.toLowerCase();
        if (status.includes('wiping')) return 'wiping';
        if (status === 'wiped') return 'completed';
        if (status === 'error') return 'error';
        return 'ready';
    }

    getDeviceIcon(type) {
        switch (type.toLowerCase()) {
            case 'hdd': return 'fa-hdd';
            case 'ssd': return 'fa-solid fa-memory';
            case 'nvme': return 'fa-server';
            default: return 'fa-hdd';
        }
    }

    toggleDeviceSelection(deviceId) {
        const checkbox = document.getElementById(`device-${deviceId}`);
        if (!checkbox) return;

        if (checkbox.checked) {
            this.selectedDevices.add(deviceId);
        } else {
            this.selectedDevices.delete(deviceId);
        }

        this.updateBulkActions();
        this.updateDeviceCards();
    }

    updateBulkActions() {
        const bulkActions = document.getElementById('bulk-actions');
        const selectedCount = document.getElementById('selected-count');
        const bulkWipeBtn = document.getElementById('bulk-wipe-btn');

        if (this.selectedDevices.size > 0) {
            if (bulkActions) bulkActions.style.display = 'block';
            if (selectedCount) {
                selectedCount.textContent = `${this.selectedDevices.size} device${this.selectedDevices.size > 1 ? 's' : ''} selected`;
            }
            if (bulkWipeBtn) bulkWipeBtn.disabled = false;
        } else {
            if (bulkActions) bulkActions.style.display = 'none';
            if (bulkWipeBtn) bulkWipeBtn.disabled = true;
        }
    }

    updateDeviceCards() {
        this.devices.forEach(device => {
            const card = document.querySelector(`#device-${device.id}`)?.closest('.device-card');
            if (card) {
                if (this.selectedDevices.has(device.id)) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
            }
        });
    }

    selectAllDevices() {
        this.devices.forEach(device => {
            if (device.is_wipeable && device.status === 'Ready') {
                this.selectedDevices.add(device.id);
                const checkbox = document.getElementById(`device-${device.id}`);
                if (checkbox) checkbox.checked = true;
            }
        });
        this.updateBulkActions();
        this.updateDeviceCards();
    }

    clearSelection() {
        this.selectedDevices.clear();
        document.querySelectorAll('.device-checkbox input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateBulkActions();
        this.updateDeviceCards();
    }

    showWipeConfirmation() {
        const modal = new bootstrap.Modal(document.getElementById('wipeConfirmationModal'));
        const selectedDevicesList = document.getElementById('selected-devices-list');

        if (!selectedDevicesList) return;

        selectedDevicesList.innerHTML = '';

        this.selectedDevices.forEach(deviceId => {
            const device = this.devices.find(d => d.id === deviceId);
            if (device) {
                const deviceItem = document.createElement('div');
                deviceItem.className = 'd-flex align-items-center mb-2';
                deviceItem.innerHTML = `
                    <div class="device-icon ${device.type.toLowerCase()} me-3" style="width: 30px; height: 30px; font-size: 14px;">
                        <i class="fas ${this.getDeviceIcon(device.type)}"></i>
                    </div>
                    <div>
                        <strong>${device.model}</strong><br>
                        <small class="text-muted">${device.capacity} • ${device.serial_number}</small>
                    </div>
                `;
                selectedDevicesList.appendChild(deviceItem);
            }
        });

        modal.show();
    }

    async startWipeProcess() {
        if (this.selectedDevices.size === 0) return;

        const modal = bootstrap.Modal.getInstance(document.getElementById('wipeConfirmationModal'));
        if (modal) modal.hide();

        this.isWiping = true;
        this.showProgressModal();

        // Start wiping each selected device
        const wipePromises = Array.from(this.selectedDevices).map(deviceId =>
            this.wipeDevice(deviceId)
        );

        await Promise.all(wipePromises);

        this.isWiping = false;
        this.showCompletionScreen();
    }

    async wipeDevice(deviceId) {
        try {
            this.updateDeviceProgress(deviceId, 'Starting...', 0);

            const response = await fetch(`/api/wipe/${deviceId}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('Wipe request failed');
            }

            // Simulate progress updates
            await this.simulateWipeProgress(deviceId);

            this.updateDeviceProgress(deviceId, 'Completed', 100);
            this.completedDevices.add(deviceId);

        } catch (error) {
            console.error(`Error wiping device ${deviceId}:`, error);
            this.updateDeviceProgress(deviceId, 'Error', -1);
        }
    }

    async simulateWipeProgress(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        const duration = device.type === 'HDD' ? 10000 : 3000; // HDD takes longer
        const steps = device.type === 'HDD' ? 20 : 10;
        const interval = duration / steps;

        for (let i = 1; i <= steps; i++) {
            if (!this.isWiping) break;

            const progress = Math.round((i / steps) * 100);
            this.updateDeviceProgress(deviceId, 'Wiping...', progress);

            await new Promise(resolve => setTimeout(resolve, interval));
        }
    }

    updateDeviceProgress(deviceId, status, progress) {
        this.wipeProgress[deviceId] = { status, progress };
        this.updateProgressModal();
    }

    showProgressModal() {
        const progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
        progressModal.show();
        this.updateProgressModal();
    }

    updateProgressModal() {
        const progressContent = document.getElementById('progress-content');
        if (!progressContent) return;

        let completed = 0;
        let total = this.selectedDevices.size;

        progressContent.innerHTML = '';

        this.selectedDevices.forEach(deviceId => {
            const device = this.devices.find(d => d.id === deviceId);
            const progress = this.wipeProgress[deviceId] || { status: 'Waiting...', progress: 0 };

            const progressItem = document.createElement('div');
            progressItem.className = 'progress-device';

            progressItem.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="progress-device-icon ${device.type.toLowerCase()}">
                        <i class="fas ${this.getDeviceIcon(device.type)}"></i>
                    </div>
                    <div class="progress-device-info flex-grow-1">
                        <h6>${device.model}</h6>
                        <div class="progress-device-status">${progress.status}</div>
                        ${progress.progress >= 0 ? `
                            <div class="progress mt-2">
                                <div class="progress-bar" role="progressbar" style="width: ${progress.progress}%">
                                    ${progress.progress}%
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;

            progressContent.appendChild(progressItem);

            if (progress.progress === 100) {
                completed++;
            }
        });

        // Update modal title
        const modalTitle = document.querySelector('#progressModal .modal-title');
        if (modalTitle) {
            const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
            modalTitle.innerHTML = `<i class="fas fa-cog fa-spin"></i> Wiping Devices... (${completed}/${total} completed)`;
        }

        // Show completion screen when all devices are done
        if (completed === total && total > 0) {
            setTimeout(() => {
                this.showCompletionScreen();
            }, 1000);
        }
    }

    showCompletionScreen() {
        const progressContent = document.getElementById('progress-content');
        const progressFooter = document.getElementById('progress-footer');
        const modalTitle = document.querySelector('#progressModal .modal-title');

        if (progressContent) {
            progressContent.innerHTML = `
                <div class="text-center">
                    <div class="mb-4">
                        <i class="fas fa-check-circle text-success" style="font-size: 4rem;"></i>
                    </div>
                    <h4 class="text-success">Wipe Operation Completed!</h4>
                    <p class="text-muted">
                        All selected devices have been securely wiped.
                        Certificates have been generated for compliance verification.
                    </p>
                </div>
            `;
        }

        if (modalTitle) {
            modalTitle.innerHTML = `<i class="fas fa-check-circle text-success"></i> Wipe Completed Successfully!`;
        }

        if (progressFooter) {
            progressFooter.style.display = 'block';
        }
    }

    wipeSingleDevice(deviceId) {
        this.selectedDevices.clear();
        this.selectedDevices.add(deviceId);
        this.showWipeConfirmation();
    }

    downloadCertificate(deviceId) {
        window.location.href = `/download_certificate/${deviceId}`;
    }

    showDeviceInfo(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        let info = `Device Information:\n\n`;
        info += `Model: ${device.model}\n`;
        info += `Type: ${device.type}\n`;
        info += `Capacity: ${device.capacity}\n`;
        info += `Serial Number: ${device.serial_number}\n`;
        info += `Status: ${device.status}\n`;

        if (device.supported_methods && device.supported_methods.length > 0) {
            info += `Supported Methods: ${device.supported_methods.join(', ')}\n`;
        }

        if (device.error_message) {
            info += `Error: ${device.error_message}\n`;
        }

        alert(info);
    }

    updateStatistics() {
        const totalDevices = this.devices.length;
        const readyDevices = this.devices.filter(d => d.is_wipeable && d.status === 'Ready').length;
        const wipingDevices = this.devices.filter(d => d.status === 'Wiping in progress').length;
        const completedDevices = this.devices.filter(d => d.status === 'Wiped').length;

        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        };

        updateElement('total-devices', totalDevices);
        updateElement('ready-devices', readyDevices);
        updateElement('wiping-devices', wipingDevices);
        updateElement('completed-devices', completedDevices);
    }
}

// Initialize the device manager when the page loads
let deviceManager;
document.addEventListener('DOMContentLoaded', function() {
    deviceManager = new DeviceManager();

    // Make deviceManager globally available for onclick handlers
    window.deviceManager = deviceManager;
});

// Global functions for onclick handlers
function refreshDevices() {
    deviceManager.loadDevices();
}

function selectAllDevices() {
    deviceManager.selectAllDevices();
}

function clearSelection() {
    deviceManager.clearSelection();
}

function showWipeConfirmation() {
    deviceManager.showWipeConfirmation();
}
