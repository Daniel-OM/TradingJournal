

function formatNumber(num) {
    if (num >= 1e12) {
        return `${(num / 1e12).toFixed(2)}T`;
    } else if (num >= 1e9) {
        return `${(num / 1e9).toFixed(2)}B`;
    } else if (num >= 1e6) {
        return `${(num / 1e6).toFixed(2)}M`;
    } else if (num >= 1e3) {
        return `${(num / 1e3).toFixed(2)}K`;
    }
    return num.toLocaleString();
}

function zeroPad (num, length) {
    length = length || 2; // defaults to 2 if no parameter is passed
    return (new Array(length).join('0')+num.toString()).slice(length*-1);
};