/**
 * Script principal para o Sistema de Controle de Pendências
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Exibir alertas com efeito fade
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        alert.classList.add('fade-in');
        
        // Auto-fechar alertas de sucesso após 5 segundos
        if (alert.classList.contains('alert-success')) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });

    // Confirmação para ações importantes
    const confirmActions = document.querySelectorAll('[data-confirm]');
    confirmActions.forEach(function(element) {
        element.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Tem certeza que deseja realizar esta ação?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Formatação de campos de telefone
    const telefoneInputs = document.querySelectorAll('.telefone-mask');
    telefoneInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            let formatted = '';
            
            if (value.length <= 2) {
                formatted = value;
            } else if (value.length <= 6) {
                formatted = `(${value.substring(0, 2)}) ${value.substring(2)}`;
            } else if (value.length <= 10) {
                formatted = `(${value.substring(0, 2)}) ${value.substring(2, 6)}-${value.substring(6)}`;
            } else {
                formatted = `(${value.substring(0, 2)}) ${value.substring(2, 7)}-${value.substring(7, 11)}`;
            }
            
            this.value = formatted;
        });
    });

    // Animação para mensagens e notificações
    const messageItems = document.querySelectorAll('.list-group-item');
    messageItems.forEach(function(item, index) {
        item.style.animationDelay = (index * 0.1) + 's';
        item.classList.add('fade-in');
    });
});

// Função para inicializar dataTables
function initDataTable(tableId) {
    const table = document.getElementById(tableId);
    if (table) {
        $(table).DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json'
            },
            responsive: true,
            pageLength: 10,
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]]
        });
    }
}