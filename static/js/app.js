
// Funções JavaScript comuns para o projeto

// Configurações globais do DataTables
const dataTablesConfig = {
    responsive: true,
    language: {
        url: 'https://cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json'
    },
    pageLength: 25,
    lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],
    dom: 'Bfrtip',
    buttons: ['copy', 'csv', 'excel', 'pdf', 'print']
};

// Função para inicializar DataTable com configurações padrão
function initDataTable(selector, customConfig = {}) {
    const config = { ...dataTablesConfig, ...customConfig };
    return $(selector).DataTable(config);
}

// Função para formatar valores monetários
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Função para validar formulários
function validateForm(formSelector) {
    const form = document.querySelector(formSelector);
    if (!form) return false;
    
    return form.checkValidity();
}

// Função para mostrar loading
function showLoading(message = 'Carregando...') {
    Notiflix.Loading.circle(message);
}

// Função para esconder loading
function hideLoading() {
    Notiflix.Loading.remove();
}

// Função para fazer requisições AJAX com tratamento de erro
async function makeRequest(url, options = {}) {
    try {
        showLoading();
        
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        const config = { ...defaultOptions, ...options };
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        hideLoading();
        return data;
        
    } catch (error) {
        hideLoading();
        console.error('Erro na requisição:', error);
        Notiflix.Notify.failure(`Erro: ${error.message}`);
        throw error;
    }
}

// Função para confirmar ações
function confirmAction(title, message, onConfirm, onCancel = null) {
    Notiflix.Confirm.show(
        title,
        message,
        'Sim',
        'Cancelar',
        onConfirm,
        onCancel
    );
}

// Função para calcular percentuais
function calculatePercentages(inputs) {
    let total = 0;
    const values = {};
    
    inputs.forEach(input => {
        const value = parseFloat(input.value) || 0;
        values[input.id] = value;
        total += value;
    });
    
    return { total, values };
}

// Função para validar percentuais (devem somar 100%)
function validatePercentages(inputs, tolerance = 0.01) {
    const { total } = calculatePercentages(inputs);
    return Math.abs(total - 100) <= tolerance;
}

// Função para atualizar indicador de percentual
function updatePercentageIndicator(inputs, indicatorSelector) {
    const { total } = calculatePercentages(inputs);
    const indicator = document.querySelector(indicatorSelector);
    
    if (!indicator) return;
    
    indicator.textContent = `Total: ${total.toFixed(1)}%`;
    
    if (Math.abs(total - 100) <= 0.01) {
        indicator.className = 'percentage-total percentage-valid';
    } else {
        indicator.className = 'percentage-total percentage-invalid';
    }
}

// Função para resetar formulário
function resetForm(formSelector) {
    const form = document.querySelector(formSelector);
    if (form) {
        form.reset();
        
        // Remove classes de validação do Bootstrap
        form.classList.remove('was-validated');
        
        // Remove mensagens de erro personalizadas
        form.querySelectorAll('.invalid-feedback').forEach(el => {
            el.textContent = '';
        });
        
        form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
    }
}

// Função para tratar upload de arquivos
function handleFileUpload(inputSelector, labelSelector, callback) {
    const input = document.querySelector(inputSelector);
    const label = document.querySelector(labelSelector);
    
    if (!input || !label) return;
    
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (file) {
            label.textContent = `Arquivo selecionado: ${file.name}`;
            label.classList.add('file-selected');
            
            if (callback && typeof callback === 'function') {
                callback(file);
            }
        } else {
            label.textContent = 'Clique aqui ou arraste um arquivo CSV para fazer upload';
            label.classList.remove('file-selected');
        }
    });
}

// Função para configurar drag and drop
function setupDragAndDrop(containerSelector, inputSelector) {
    const container = document.querySelector(containerSelector);
    const input = document.querySelector(inputSelector);
    
    if (!container || !input) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        container.addEventListener(eventName, () => {
            container.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, () => {
            container.classList.remove('dragover');
        }, false);
    });
    
    container.addEventListener('drop', function(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            input.files = files;
            input.dispatchEvent(new Event('change'));
        }
    }, false);
}

// Função para exportar dados como CSV
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Função auxiliar para converter dados para CSV
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvHeaders = headers.join(',');
    
    const csvRows = data.map(row => {
        return headers.map(header => {
            const value = row[header];
            return typeof value === 'string' ? `"${value}"` : value;
        }).join(',');
    });
    
    return [csvHeaders, ...csvRows].join('\n');
}

// Função para debounce (evitar múltiplas chamadas)
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

// Inicialização quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Configurações globais do Notiflix
    Notiflix.Notify.init({
        width: '350px',
        position: 'right-top',
        distance: '20px',
        opacity: 1,
        borderRadius: '8px',
        rtl: false,
        timeout: 5000,
        messageMaxLength: 110,
        backOverlay: false,
        backOverlayColor: 'rgba(0,0,0,0.5)',
        plainText: true,
        showOnlyTheLastOne: false,
        clickToClose: false,
        pauseOnHover: true,
        ID: 'NotiflixNotify',
        className: 'notiflix-notify',
        zindex: 4001,
        fontFamily: 'Quicksand',
        fontSize: '13px',
        cssAnimation: true,
        cssAnimationDuration: 400,
        cssAnimationStyle: 'fade',
        closeButton: false,
        useGoogleFont: false,
        fontFamilyFallback: 'Verdana'
    });
    
    // Configuração global do Notiflix Loading
    Notiflix.Loading.init({
        className: 'notiflix-loading',
        zindex: 4000,
        backgroundColor: 'rgba(0,0,0,0.8)',
        rtl: false,
        fontFamily: 'Quicksand',
        cssAnimation: true,
        cssAnimationDuration: 400,
        clickToClose: false,
        customSvgUrl: null,
        customSvgCode: null,
        svgSize: '80px',
        svgColor: '#32c682',
        messageID: 'NotiflixLoadingMessage',
        messageFontSize: '15px',
        messageMaxLength: 34,
        messageColor: '#dcdcdc'
    });
});

// Exportar funções para uso global
window.AppUtils = {
    initDataTable,
    formatCurrency,
    validateForm,
    showLoading,
    hideLoading,
    makeRequest,
    confirmAction,
    calculatePercentages,
    validatePercentages,
    updatePercentageIndicator,
    resetForm,
    handleFileUpload,
    setupDragAndDrop,
    exportToCSV,
    debounce
};
