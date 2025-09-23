// Unified Devices Page JavaScript - Combining audit.html and devices.html functionality
class UnifiedDeviceManager {
    constructor() {
        this.devices = [];
        this.selectedDevices = new Set();
        this.isWiping = false;
        this.wipeProgress = {};
        this.completedDevices = new Set();
        this.currentStep = 1;

        this.initializeEventListeners();
        this.loadDevices();
        this.initializeCharts();
    }

    initializeEventListeners() {
        // Checkbox for understanding the risks
        document.getElementById('understand-checkbox')?.addEventListener('change', (e) => {
            const confirmBtn = document.getElementById('confirm-wipe-btn');
            if (confirmBtn) {
                confirmBtn.disabled = !e.target.checked;
            }
        });
    }

    async loadDevices() {
        try {
            const response = await fetch('/api/drives');
            const data = await response.json();

            this.devices = data;
            this.renderDevices();
            this.updateStatistics();

        } catch (error) {
            console.error('Error loading devices:', error);
            this.showError('Failed to load devices. Please refresh the page.');
        }
    }

    renderDevices() {
        const tbody = document.getElementById('drivesTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        this.devices.forEach(device => {
            const row = this.createDeviceRow(device);
            tbody.appendChild(row);
        });
    }

    createDeviceRow(device) {
        const row = document.createElement('tr');
        const isWipeable = device.is_wipeable && device.status === 'Ready';
        const isSelected = this.selectedDevices.has(device.id);

        row.innerHTML = `
            <td>
                ${isWipeable ? `
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="device-${device.id}"
                               ${isSelected ? 'checked' : ''}
                               onchange="deviceManager.toggleDeviceSelection('${device.id}')">
                    </div>
                ` : '<span class="text-muted">-</span>'}
            </td>
            <td>${device.id}</td>
            <td>
                <span class="badge bg-secondary">${device.type}</span>
            </td>
            <td>${device.model}</td>
            <td>${device.capacity}</td>
            <td>
                <span class="drive-status ${this.getStatusClass(device.status)}">
                    ${this.getStatusText(device.status)}
                </span>
            </td>
            <td>
                ${isWipeable ? `
                    <button class="btn btn-primary btn-sm" onclick="deviceManager.wipeSingleDevice('${device.id}')">
                        <i class="fas fa-eraser"></i> Wipe
                    </button>
                ` : device.status === 'Wiped' ? `
                    <button class="btn btn-success btn-sm" onclick="deviceManager.downloadCertificate('${device.id}')">
                        <i class="fas fa-certificate"></i> Certificate
                    </button>
                ` : '<button class="btn btn-secondary btn-sm" disabled>Not Available</button>'}
            </td>
        `;

        return row;
    }

    getStatusClass(status) {
        switch (status) {
            case 'Ready': return 'status-available';
            case 'Wiping in progress': return 'status-selected';
            case 'Wiped': return 'status-erased';
            case 'Error': return 'status-erased';
            default: return 'status-available';
        }
    }

    getStatusText(status) {
        switch (status) {
            case 'Ready': return 'Available';
            case 'Wiping in progress': return 'Wiping';
            case 'Wiped': return 'Erased';
            case 'Error': return 'Error';
            default: return status;
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

    selectAllDevices() {
        this.devices.forEach(device => {
            if (device.is_wipeable && device.status === 'Ready') {
                this.selectedDevices.add(device.id);
                const checkbox = document.getElementById(`device-${device.id}`);
                if (checkbox) checkbox.checked = true;
            }
        });
        this.updateBulkActions();
    }

    clearSelection() {
        this.selectedDevices.clear();
        document.querySelectorAll('.form-check-input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateBulkActions();
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
        this.nextStep(3);
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
        this.updateOverallProgress();
    }

    updateOverallProgress() {
        const total = this.selectedDevices.size;
        const completed = Array.from(this.selectedDevices).filter(id => this.wipeProgress[id]?.progress === 100).length;
        const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

        const overallProgress = document.getElementById('overall-progress');
        const overallProgressFill = document.getElementById('overall-progress-fill');

        if (overallProgress) overallProgress.textContent = `${percentage}%`;
        if (overallProgressFill) overallProgressFill.style.width = `${percentage}%`;
    }

    showProgressModal() {
        this.updateProgressModal();
    }

    updateProgressModal() {
        const deviceProgressContainer = document.getElementById('device-progress-container');
        if (!deviceProgressContainer) return;

        deviceProgressContainer.innerHTML = '';

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

            deviceProgressContainer.appendChild(progressItem);
        });
    }

    showCompletionScreen() {
        const completionButtons = document.getElementById('completion-buttons');
        if (completionButtons) {
            completionButtons.style.display = 'block';
        }

        // Update charts
        this.updateCharts();

        // Show success message
        this.showSuccess('All devices have been successfully wiped!');
    }

    wipeSingleDevice(deviceId) {
        this.selectedDevices.clear();
        this.selectedDevices.add(deviceId);
        this.showWipeConfirmation();
    }

    downloadCertificate(deviceId) {
        window.location.href = `/download_certificate/${deviceId}`;
    }

    downloadCertificates() {
        this.selectedDevices.forEach(deviceId => {
            this.downloadCertificate(deviceId);
        });
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

    getDeviceIcon(type) {
        switch (type.toLowerCase()) {
            case 'hdd': return 'fa-hdd';
            case 'ssd': return 'fa-solid fa-memory';
            case 'nvme': return 'fa-server';
            default: return 'fa-hdd';
        }
    }

    initializeCharts() {
        // Initialize charts when step 3 is reached
        this.progressChart = null;
        this.statisticsChart = null;
    }

    updateCharts() {
        // Progress Chart
        const progressCtx = document.getElementById('progressChart');
        if (progressCtx && !this.progressChart) {
            this.progressChart = new Chart(progressCtx, {
                type: 'pie',
                data: {
                    labels: ['Completed', 'In Progress', 'Failed'],
                    datasets: [{
                        data: [this.completedDevices.size, this.selectedDevices.size - this.completedDevices.size, 0],
                        backgroundColor: ['#16a34a', '#3b82f6', '#ef4444']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    }
                }
            });
        }

        // Statistics Chart
        const statisticsCtx = document.getElementById('statisticsChart');
        if (statisticsCtx && !this.statisticsChart) {
            this.statisticsChart = new Chart(statisticsCtx, {
                type: 'bar',
                data: {
                    labels: ['Total', 'Ready', 'Wiping', 'Completed'],
                    datasets: [{
                        data: [this.devices.length, this.devices.filter(d => d.status === 'Ready').length,
                               this.devices.filter(d => d.status === 'Wiping in progress').length,
                               this.devices.filter(d => d.status === 'Wiped').length],
                        backgroundColor: ['#16a34a', '#3b82f6', '#f59e0b', '#ef4444']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        }
                    }
                }
            });
        }
    }

    nextStep(step) {
        this.currentStep = step;
        this.updateStepNavigation();
        this.showStepContent(step);
    }

    previousStep(step) {
        this.currentStep = step;
        this.updateStepNavigation();
        this.showStepContent(step);
    }

    updateStepNavigation() {
        // Update step indicators
        document.querySelectorAll('.step').forEach((stepEl, index) => {
            const stepNumber = index + 1;
            stepEl.classList.remove('active', 'completed');

            if (stepNumber < this.currentStep) {
                stepEl.classList.add('completed');
            } else if (stepNumber === this.currentStep) {
                stepEl.classList.add('active');
            }
        });
    }

    showStepContent(step) {
        // Hide all content
        document.querySelectorAll('.step-content').forEach(content => {
            content.classList.remove('active');
        });

        // Show current step content
        const currentContent = document.getElementById(`content${step}`);
        if (currentContent) {
            currentContent.classList.add('active');
        }
    }

    showSuccess(message) {
        Swal.fire({
            title: 'Success!',
            text: message,
            icon: 'success',
            confirmButtonText: 'Continue',
            customClass: {
                popup: 'bg-slate-900 border border-cyan-400/30',
                title: 'text-cyan-400',
                confirmButton: 'bg-cyan-500 hover:bg-cyan-600 text-slate-900'
            }
        });
    }

    showError(message) {
        Swal.fire({
            title: 'Error!',
            text: message,
            icon: 'error',
            confirmButtonText: 'OK',
            customClass: {
                popup: 'bg-slate-900 border border-red-400/30',
                title: 'text-red-400',
                confirmButton: 'bg-red-500 hover:bg-red-600 text-slate-900'
            }
        });
    }

    restartProcess() {
        this.selectedDevices.clear();
        this.wipeProgress = {};
        this.completedDevices.clear();
        this.currentStep = 1;
        this.updateStepNavigation();
        this.showStepContent(1);
        this.loadDevices();

        const completionButtons = document.getElementById('completion-buttons');
        if (completionButtons) {
            completionButtons.style.display = 'none';
        }
    }
}

// Initialize the device manager when the page loads
let deviceManager;
document.addEventListener('DOMContentLoaded', function() {
    deviceManager = new UnifiedDeviceManager();

    // Make deviceManager globally available for onclick handlers
    window.deviceManager = deviceManager;
});

// Global functions for onclick handlers
function scanDrives() {
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

function startWipeProcess() {
    deviceManager.startWipeProcess();
}
