// App principal
class ViajeApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupServiceWorker();
        this.setupEventListeners();
        this.setupOfflineSupport();
    }

    // Service Worker para PWA
    async setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/static/sw.js');
                console.log('Service Worker registrado exitosamente');
            } catch (error) {
                console.log('Error al registrar Service Worker:', error);
            }
        }
    }

    // Event listeners globales
    setupEventListeners() {
        // Prevenir zoom en inputs en iOS
        document.addEventListener('touchstart', function(e) {
            if (e.touches.length > 1) {
                e.preventDefault();
            }
        });

        // Manejar install prompt de PWA
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        // Manejar cuando la app se instala
        window.addEventListener('appinstalled', () => {
            console.log('PWA instalada exitosamente');
            this.hideInstallButton();
        });

        // Manejar conexión online/offline
        window.addEventListener('online', () => {
            this.hideOfflineMessage();
            this.syncOfflineData();
        });

        window.addEventListener('offline', () => {
            this.showOfflineMessage();
        });
    }

    // Soporte offline
    setupOfflineSupport() {
        // Verificar estado inicial de conexión
        if (!navigator.onLine) {
            this.showOfflineMessage();
        }
    }

    // Mostrar botón de instalación
    showInstallButton() {
        const installBtn = document.createElement('button');
        installBtn.className = 'install-btn';
        installBtn.innerHTML = '<span class="material-icons">get_app</span> Instalar App';
        installBtn.onclick = () => this.installApp();
        
        // Agregar al header si existe
        const headerActions = document.querySelector('.header-actions');
        if (headerActions) {
            headerActions.appendChild(installBtn);
        }
    }

    hideInstallButton() {
        const installBtn = document.querySelector('.install-btn');
        if (installBtn) {
            installBtn.remove();
        }
    }

    // Instalar PWA
    async installApp() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            const result = await this.deferredPrompt.userChoice;
            
            if (result.outcome === 'accepted') {
                console.log('Usuario aceptó instalar la PWA');
            } else {
                console.log('Usuario rechazó instalar la PWA');
            }
            
            this.deferredPrompt = null;
            this.hideInstallButton();
        }
    }

    // Mensaje offline
    showOfflineMessage() {
        let offlineMsg = document.querySelector('.offline-message');
        if (!offlineMsg) {
            offlineMsg = document.createElement('div');
            offlineMsg.className = 'offline-message';
            offlineMsg.innerHTML = `
                <span class="material-icons">wifi_off</span>
                Modo offline - Los cambios se sincronizarán cuando tengas conexión
            `;
            document.body.appendChild(offlineMsg);
        }
        offlineMsg.classList.add('show');
    }

    hideOfflineMessage() {
        const offlineMsg = document.querySelector('.offline-message');
        if (offlineMsg) {
            offlineMsg.classList.remove('show');
        }
    }

    // Sincronizar datos offline
    syncOfflineData() {
        const offlineData = localStorage.getItem('offlineData');
        if (offlineData) {
            const data = JSON.parse(offlineData);
            // Aquí implementarías la lógica de sincronización
            console.log('Sincronizando datos offline:', data);
            localStorage.removeItem('offlineData');
        }
    }
}

// Funciones utilitarias globales
function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.remove('hidden');
    }
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.add('hidden');
    }
}

function showToast(message, type = 'info') {
    // Remover toast existente si hay uno
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Mostrar toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Ocultar toast después de 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// Función para manejar errores de red
async function handleApiCall(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error en API call:', error);
        
        // Si estamos offline, guardar para sincronizar después
        if (!navigator.onLine) {
            const offlineData = JSON.parse(localStorage.getItem('offlineData') || '[]');
            offlineData.push({
                url,
                options,
                timestamp: new Date().toISOString()
            });
            localStorage.setItem('offlineData', JSON.stringify(offlineData));
            showToast('Guardado offline. Se sincronizará cuando tengas conexión.', 'info');
        } else {
            showToast('Error de conexión. Por favor intenta de nuevo.', 'error');
        }
        
        throw error;
    }
}

// Función para formatear fechas
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Función para formatear moneda
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2
    }).format(amount);
}

// Función para calcular días entre fechas
function calculateDaysBetween(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

// Función para validar formularios
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        const errorElement = input.parentNode.querySelector('.error-message');
        
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('error');
            
            if (!errorElement) {
                const error = document.createElement('div');
                error.className = 'error-message';
                error.textContent = 'Este campo es requerido';
                input.parentNode.appendChild(error);
            }
        } else {
            input.classList.remove('error');
            if (errorElement) {
                errorElement.remove();
            }
        }
    });
    
    return isValid;
}

// Función para limpiar formularios
function clearForm(formId) {
    const form = document.getElementById(formId);
    form.reset();
    
    // Remover clases de error
    form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
    form.querySelectorAll('.error-message').forEach(el => el.remove());
}

// Función para generar color basado en categoría
function getCategoryColor(category) {
    const colors = {
        'transporte': '#2196F3',
        'hospedaje': '#4CAF50',
        'comida': '#FF9800',
        'entretenimiento': '#9C27B0',
        'compras': '#F44336',
        'otros': '#607D8B'
    };
    return colors[category] || colors['otros'];
}

// Función para generar gráfico simple de gastos por categoría
function createExpenseChart(gastos, containerId) {
    const container = document.getElementById(containerId);
    if (!container || !gastos.length) return;
    
    // Agrupar gastos por categoría
    const categorias = {};
    gastos.forEach(gasto => {
        if (!categorias[gasto.categoria]) {
            categorias[gasto.categoria] = 0;
        }
        categorias[gasto.categoria] += gasto.monto;
    });
    
    // Crear barras
    const total = Object.values(categorias).reduce((a, b) => a + b, 0);
    
    container.innerHTML = '';
    Object.entries(categorias).forEach(([categoria, monto]) => {
        const percentage = (monto / total) * 100;
        const bar = document.createElement('div');
        bar.className = 'chart-bar';
        bar.innerHTML = `
            <div class="chart-label">${categoria.charAt(0).toUpperCase() + categoria.slice(1)}</div>
            <div class="chart-bar-fill" style="width: ${percentage}%; background-color: ${getCategoryColor(categoria)}"></div>
            <div class="chart-value">${formatCurrency(monto)}</div>
        `;
        container.appendChild(bar);
    });
}

// Función para detectar si es dispositivo móvil
function isMobile() {
    return window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Función para vibración háptica en móviles
function hapticFeedback(type = 'light') {
    if ('vibrate' in navigator) {
        switch (type) {
            case 'light':
                navigator.vibrate(10);
                break;
            case 'medium':
                navigator.vibrate(50);
                break;
            case 'heavy':
                navigator.vibrate(100);
                break;
        }
    }
}

// Función para compartir nativo
async function shareContent(title, text, url) {
    if (navigator.share) {
        try {
            await navigator.share({
                title,
                text,
                url
            });
        } catch (error) {
            console.log('Error al compartir:', error);
            // Fallback: copiar al portapapeles
            await navigator.clipboard.writeText(url);
            showToast('Enlace copiado al portapapeles', 'success');
        }
    } else {
        // Fallback: copiar al portapapeles
        await navigator.clipboard.writeText(url);
        showToast('Enlace copiado al portapapeles', 'success');
    }
}

// Debounce para optimizar búsquedas
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Inicializar app cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    new ViajeApp();
    
    // Inicializar sistema de tabs si estamos en la página de viaje
    if (document.querySelector('.tabs')) {
        setTimeout(() => {
            initializeTabs();
        }, 100);
    }
    
    // Configurar fecha de hoy para inputs de fecha
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.value && input.id.includes('fecha')) {
            input.value = today;
        }
    });
    
    // Autocompletar ubicaciones si la API de geolocalización está disponible
    if ('geolocation' in navigator) {
        const locationInputs = document.querySelectorAll('input[name="ubicacion"]');
        locationInputs.forEach(input => {
            input.addEventListener('focus', () => {
                if (!input.value) {
                    // Aquí podrías integrar con una API de lugares como Google Places
                    console.log('Solicitar ubicación actual');
                }
            });
        });
    }
});

// Funciones para persistencia de tabs
function saveActiveTab(tabId) {
    localStorage.setItem('activeTab', tabId);
}

function getActiveTab() {
    return localStorage.getItem('activeTab') || 'gastos';
}

function reloadWithActiveTab() {
    window.location.reload();
}

// Funciones para manejo de tabs
function switchToTab(tabName) {
    // Remover active de todos los tabs y contenidos
    document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    // Agregar active al tab y contenido seleccionado
    const tabButton = document.querySelector(`[data-tab="${tabName}"]`);
    const tabContent = document.getElementById(tabName);
    
    if (tabButton && tabContent) {
        tabButton.classList.add('active');
        tabContent.classList.add('active');
        saveActiveTab(tabName);
    }
}

function initializeTabs() {
    // Configurar event listeners para tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchToTab(tabName);
        });
    });

    // Restaurar tab activo al cargar la página
    const activeTab = getActiveTab();
    
    if (activeTab && document.getElementById(activeTab)) {
        switchToTab(activeTab);
    } else {
        switchToTab('gastos');
    }
}
