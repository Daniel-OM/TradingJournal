

// Format currency values
function formatCurrency (value, min_decimals = 1, max_decimals = 2, notation = null) {
    // Use notation = 'compact' for financial amounts
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: min_decimals,
        maximumFractionDigits: max_decimals,
        notation: notation
    }).format(value);
}

// Format percentage values
function formatPercentage (value, min_decimals = 1, max_decimals = 2) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: min_decimals,
        maximumFractionDigits: max_decimals
    }).format(value / 100);
}

// Format compact values
function formatFinancial (value, min_decimals = 1, max_decimals = 2, notation = null) {
    // Use notation = 'compact' for financial amounts
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: min_decimals,
        maximumFractionDigits: max_decimals,
        notation: notation
    }).format(value);
}

function formatNumber (n, mode = null, min_decimals = 1, max_decimals = 2, notation = null) {
    // Use notation = 'compact' for financial amounts
    if (mode === 'currency') {
        return formatCurrency(n, min_decimals, max_decimals, notation);
    } else if (mode === 'percentage') {
        return formatPercentage(n, min_decimals, max_decimals);
    } else if (mode == 'financial') {
        return formatFinancial(n, min_decimals, max_decimals, notation);
    } else {
        return n.toFixed(max_decimals);
    }
}

function zeroPad (num, length) {
    length = length || 2; // defaults to 2 if no parameter is passed
    return (new Array(length).join('0')+num.toString()).slice(length*-1);
};


function formatDate (dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}