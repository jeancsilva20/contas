
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

// Função para salvar aba ativa no localStorage
function salvarAbaAtiva(tipo) {
    localStorage.setItem('dadosAbaAtiva', tipo);
}

// Função para recuperar aba ativa do localStorage
function recuperarAbaAtiva() {
    return localStorage.getItem('dadosAbaAtiva') || 'upload';
}

// Função para ativar uma aba específica
function ativarAba(tipo) {
    // Desativar todas as abas
    document.querySelectorAll('#dadosTabs .nav-link').forEach(tab => {
        tab.classList.remove('active');
        tab.setAttribute('aria-selected', 'false');
    });
    
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('show', 'active');
    });
    
    // Ativar a aba específica
    const tabButton = document.getElementById(`${tipo}-tab`);
    const tabPane = document.getElementById(`${tipo}-pane`);
    
    if (tabButton && tabPane) {
        tabButton.classList.add('active');
        tabButton.setAttribute('aria-selected', 'true');
        
        tabPane.classList.add('show', 'active');
        
        // Salvar no localStorage
        salvarAbaAtiva(tipo);
    }
}

// Função para carregar conteúdo via AJAX
function carregarConteudo(tipo) {
    const urls = {
        'fontes': '/fontes_content',
        'pessoas': '/pessoas_content',
        'limpar_base': '/limpar_base_content',
        'upload': '/upload_content'
    };
    
    const url = urls[tipo];
    if (!url) {
        console.error('Tipo de conteúdo não encontrado:', tipo);
        return;
    }
    
    // Salvar aba ativa
    salvarAbaAtiva(tipo);
    
    showLoading('Atualizando dados...');
    
    const contentDiv = `#${tipo}-content`;
    
    // Limpa o cache de carregamento para forçar recarregamento
    $(contentDiv).removeData('loaded');
    
    // Carrega conteúdo via AJAX
    $.get(url)
        .done(function(data) {
            $(contentDiv).html(data);
            $(contentDiv).data('loaded', true);
            hideLoading();
            
            // Ativa a aba correta se não estiver ativa
            if (!$(`#${tipo}-tab`).hasClass('active')) {
                ativarAba(tipo);
            }
            
            Notiflix.Notify.success('Dados atualizados com sucesso!');
        })
        .fail(function() {
            hideLoading();
            $(contentDiv).html(`
                <div class="alert alert-danger" role="alert">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Erro ao carregar conteúdo. Tente novamente.
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="carregarConteudo('${tipo}')">
                        <i class="bi bi-arrow-clockwise me-1"></i>Tentar Novamente
                    </button>
                </div>
            `);
            Notiflix.Notify.failure('Erro ao atualizar dados');
        });
}

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

// Disponibilizar carregarConteudo globalmente
window.carregarConteudo = carregarConteudo;
