/**
 * Enhanced Table Component with Advanced Features
 * Supports: Virtual scrolling, search, sorting, filtering, pagination
 */

class EnhancedTable {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.data = [];
        this.filteredData = [];
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.searchTerm = '';
        this.currentPage = 1;
        this.itemsPerPage = options.itemsPerPage || 50;
        this.virtualScrolling = options.virtualScrolling || false;
        this.columns = options.columns || [];
        this.title = options.title || '';
        this.color = options.color || '#2196f3';
        
        this.init();
    }
    
    init() {
        this.createTableStructure();
        this.attachEventListeners();
    }
    
    createTableStructure() {
        this.container.innerHTML = `
            <div class="enhanced-table-container">
                <div class="enhanced-table-header">
                    <div class="enhanced-table-title-row">
                        <h3 style="margin: 0; color: ${this.color};">${this.title}</h3>
                        <div class="enhanced-table-actions">
                            <button class="enhanced-table-btn" onclick="this.exportData()">📊 Export</button>
                            <button class="enhanced-table-btn" onclick="this.toggleColumns()">⚙️ Columns</button>
                        </div>
                    </div>
                    <div class="enhanced-table-controls">
                        <input type="text" id="tableSearch" placeholder="Search..." 
                               style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
                        <select id="tablePageSize" style="padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-left: 10px;">
                            <option value="25">25 per page</option>
                            <option value="50" selected>50 per page</option>
                            <option value="100">100 per page</option>
                            <option value="all">Show all</option>
                        </select>
                        <span id="tableStats" style="margin-left: 10px; font-size: 12px; color: #666;"></span>
                    </div>
                </div>
                
                <div class="enhanced-table-body" style="flex: 1; overflow: hidden;">
                    <table id="enhancedTable" style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <thead id="tableHead" style="background: #f8f9fa; position: sticky; top: 0; z-index: 10;">
                            <!-- Headers will be populated here -->
                        </thead>
                        <tbody id="tableBody">
                            <!-- Data will be populated here -->
                        </tbody>
                    </table>
                </div>
                
                <div class="enhanced-table-footer">
                    <div class="enhanced-table-pagination">
                        <button id="prevPage" class="enhanced-table-btn">← Previous</button>
                        <span id="pageInfo" style="margin: 0 15px; font-size: 12px;"></span>
                        <button id="nextPage" class="enhanced-table-btn">Next →</button>
                    </div>
                </div>
            </div>
        `;
        
        this.addTableStyles();
    }
    
    addTableStyles() {
        if (document.getElementById('enhancedTableStyles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'enhancedTableStyles';
        styles.textContent = `
            .enhanced-table-container {
                height: 100%;
                display: flex;
                flex-direction: column;
                border: 1px solid #ddd;
                border-radius: 8px;
                overflow: hidden;
            }
            
            .enhanced-table-header {
                background: #f8f9fa;
                border-bottom: 1px solid #ddd;
                padding: 15px;
            }
            
            .enhanced-table-title-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .enhanced-table-controls {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .enhanced-table-actions {
                display: flex;
                gap: 8px;
            }
            
            .enhanced-table-btn {
                background: ${this.color};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 11px;
                transition: background 0.2s;
            }
            
            .enhanced-table-btn:hover {
                opacity: 0.9;
            }
            
            .enhanced-table-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .enhanced-table-body {
                overflow-y: auto;
                max-height: 500px;
            }
            
            .enhanced-table-footer {
                background: #f8f9fa;
                border-top: 1px solid #ddd;
                padding: 10px 15px;
            }
            
            .enhanced-table-pagination {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .sortable-header {
                cursor: pointer;
                user-select: none;
                position: relative;
                padding-right: 20px !important;
            }
            
            .sortable-header:hover {
                background: #e9ecef;
            }
            
            .sort-indicator {
                position: absolute;
                right: 5px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 10px;
                color: #666;
            }
            
            .enhanced-table-body tr:hover {
                background: #f8f9fa;
            }
            
            .highlighted-row {
                background: #fff3cd !important;
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    attachEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('tableSearch');
        searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.filterAndSort();
            this.render();
        });
        
        // Page size change
        const pageSizeSelect = document.getElementById('tablePageSize');
        pageSizeSelect.addEventListener('change', (e) => {
            this.itemsPerPage = e.target.value === 'all' ? this.filteredData.length : parseInt(e.target.value);
            this.currentPage = 1;
            this.render();
        });
        
        // Pagination
        document.getElementById('prevPage').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.render();
            }
        });
        
        document.getElementById('nextPage').addEventListener('click', () => {
            const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.render();
            }
        });
    }
    
    setData(data) {
        this.data = data;
        this.filteredData = [...data];
        this.filterAndSort();
        this.render();
    }
    
    setColumns(columns) {
        this.columns = columns;
        this.renderHeaders();
    }
    
    renderHeaders() {
        const tableHead = document.getElementById('tableHead');
        const headerRow = document.createElement('tr');
        
        this.columns.forEach(column => {
            const th = document.createElement('th');
            th.style.cssText = 'padding: 8px; text-align: left; border-bottom: 1px solid #ddd; font-weight: 600;';
            th.className = 'sortable-header';
            th.innerHTML = `
                ${column.title}
                <span class="sort-indicator" id="sort-${column.key}"></span>
            `;
            
            th.addEventListener('click', () => {
                this.sortBy(column.key);
            });
            
            headerRow.appendChild(th);
        });
        
        tableHead.innerHTML = '';
        tableHead.appendChild(headerRow);
    }
    
    sortBy(columnKey) {
        if (this.sortColumn === columnKey) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = columnKey;
            this.sortDirection = 'asc';
        }
        
        this.filterAndSort();
        this.render();
        this.updateSortIndicators();
    }
    
    updateSortIndicators() {
        // Clear all indicators
        document.querySelectorAll('.sort-indicator').forEach(indicator => {
            indicator.textContent = '';
        });
        
        // Set current sort indicator
        if (this.sortColumn) {
            const indicator = document.getElementById(`sort-${this.sortColumn}`);
            if (indicator) {
                indicator.textContent = this.sortDirection === 'asc' ? '▲' : '▼';
            }
        }
    }
    
    filterAndSort() {
        // Filter data
        this.filteredData = this.data.filter(row => {
            if (!this.searchTerm) return true;
            
            return this.columns.some(column => {
                const value = this.getNestedValue(row, column.key);
                return value && value.toString().toLowerCase().includes(this.searchTerm);
            });
        });
        
        // Sort data
        if (this.sortColumn) {
            this.filteredData.sort((a, b) => {
                const aVal = this.getNestedValue(a, this.sortColumn);
                const bVal = this.getNestedValue(b, this.sortColumn);
                
                if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
                return 0;
            });
        }
        
        this.currentPage = 1; // Reset to first page after filtering
    }
    
    getNestedValue(obj, key) {
        return key.split('.').reduce((o, k) => o && o[k], obj);
    }
    
    render() {
        this.renderHeaders();
        this.renderBody();
        this.renderPagination();
        this.renderStats();
    }
    
    renderBody() {
        const tableBody = document.getElementById('tableBody');
        
        // Calculate pagination
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.filteredData.slice(startIndex, endIndex);
        
        // Clear existing rows
        tableBody.innerHTML = '';
        
        if (pageData.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `
                <td colspan="${this.columns.length}" style="text-align: center; padding: 20px; color: #666;">
                    ${this.searchTerm ? 'No results found for your search.' : 'No data available.'}
                </td>
            `;
            tableBody.appendChild(emptyRow);
            return;
        }
        
        pageData.forEach(row => {
            const tr = document.createElement('tr');
            tr.style.cssText = 'border-bottom: 1px solid #eee;';
            
            this.columns.forEach(column => {
                const td = document.createElement('td');
                td.style.cssText = 'padding: 8px; vertical-align: top;';
                
                const value = this.getNestedValue(row, column.key);
                
                if (column.render) {
                    td.innerHTML = column.render(value, row);
                } else {
                    td.textContent = value || '';
                }
                
                tr.appendChild(td);
            });
            
            tableBody.appendChild(tr);
        });
    }
    
    renderPagination() {
        const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);
        const pageInfo = document.getElementById('pageInfo');
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        
        pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        
        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage >= totalPages;
    }
    
    renderStats() {
        const stats = document.getElementById('tableStats');
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = Math.min(startIndex + this.itemsPerPage, this.filteredData.length);
        
        stats.textContent = `Showing ${startIndex + 1}-${endIndex} of ${this.filteredData.length} entries`;
        
        if (this.filteredData.length !== this.data.length) {
            stats.textContent += ` (filtered from ${this.data.length} total)`;
        }
    }
    
    exportData() {
        const dataToExport = this.filteredData.length > 0 ? this.filteredData : this.data;
        const csvContent = this.convertToCSV(dataToExport);
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `${this.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    convertToCSV(data) {
        if (!data.length) return '';
        
        const headers = this.columns.map(col => col.title).join(',');
        const rows = data.map(row => 
            this.columns.map(col => {
                const value = this.getNestedValue(row, col.key);
                return `"${(value || '').toString().replace(/"/g, '""')}"`;
            }).join(',')
        );
        
        return [headers, ...rows].join('\n');
    }
    
    highlightRow(index) {
        const rows = document.querySelectorAll('#tableBody tr');
        rows.forEach(row => row.classList.remove('highlighted-row'));
        
        if (rows[index]) {
            rows[index].classList.add('highlighted-row');
            rows[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    refresh() {
        this.render();
    }
}

// Export for global use
window.EnhancedTable = EnhancedTable;