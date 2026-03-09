const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const runBtn = document.getElementById('runBtn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const resultsBody = document.getElementById('resultsBody');
const runControls = document.getElementById('runControls');
const fileInfo = document.getElementById('fileInfo');
const totalCountEl = document.getElementById('totalCount');
const successCountEl = document.getElementById('successCount');
const failCountEl = document.getElementById('failCount');

let uploadedFilename = '';
let currentResults = null;

// --- Event Listeners ---

// Drag & Drop
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
});

dropZone.addEventListener('drop', handleDrop, false);
fileInput.addEventListener('change', handleFiles, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles({ target: { files: files } });
}

async function handleFiles(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.har')) {
        alert('Please upload a valid .har file.');
        return;
    }

    uploadFile(file);
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    loading.classList.remove('hidden');
    fileInfo.innerText = '';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        uploadedFilename = data.filename;
        fileInfo.innerHTML = `<span style="color: #73c990;"><i class="fas fa-check-circle"></i> ${file.name}</span>`;
        runControls.classList.remove('hidden');
    } catch (err) {
        fileInfo.innerHTML = `<span style="color: #f93e3e;">Error: ${err.message}</span>`;
    } finally {
        loading.classList.add('hidden');
    }
}

runBtn.addEventListener('click', async () => {
    if (!uploadedFilename) return;

    loading.classList.remove('hidden');
    runBtn.disabled = true;
    resultsSection.classList.add('hidden');

    try {
        const response = await fetch(`/run-check/${uploadedFilename}`, { method: 'POST' });
        const results = await response.json();
        renderResults(results);
    } catch (err) {
        alert("Failed to run health check: " + err);
    } finally {
        loading.classList.add('hidden');
        runBtn.disabled = false;
    }
});


function renderResults(results) {
    currentResults = results;
    resultsBody.innerHTML = '';

    // Enable Download Button
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.disabled = false;
    }

    if (!Array.isArray(results)) {
        console.error("Results is not an array:", results);
        alert("Received invalid data format from server.");
        return;
    }

    let successCount = 0;

    results.forEach((res, index) => {
        if (res.success) successCount++;

        const rowId = `row-${index}`;
        const tr = document.createElement('tr');
        tr.className = 'api-row';
        tr.onclick = () => toggleDetails(index);

        const statusClass = res.success ? 'status-2xx' : 'status-4xx'; // Simplified check

        tr.innerHTML = `
            <td><span class="method-badge ${res.method}">${res.method}</span></td>
            <td><div class="url-cell" title="${res.url}">${res.url}</div></td>
            <td class="status-cell ${statusClass}">${res.status_code || 'ERR'} <span style="font-size:0.7em; font-weight:normal;">${res.success ? 'OK' : 'FAIL'}</span></td>
            <td class="time-cell">${res.response_time ? res.response_time + 's' : '-'}</td>
        `;

        const detailsTr = document.createElement('tr');
        detailsTr.className = 'details-row';
        detailsTr.id = `detail-${index}`;

        const reqStr = res.request_body ? formatJSON(res.request_body) : '(No Body)';
        const resStr = res.response_body ? formatJSON(res.response_body) : '(No Response Body)';

        let errorHtml = '';
        if (!res.success) {
            // Fallback if short_error is missing
            const errorTitle = res.short_error || "Check Failed";
            const errorDetail = res.error || "Unknown Error";
            errorHtml = `
                 <div class="error-container">
                     <div class="error-header">
                        <i class="fas fa-exclamation-triangle"></i> ${errorTitle}
                     </div>
                     <pre class="error-detail">${formatJSON(errorDetail)}</pre>
                 </div>
             `;
        }

        const assertResult = res.result || '(No Assertion Info)';
        const resultClass = res.success ? 'text-success' : 'text-danger';

        detailsTr.innerHTML = `
            <td colspan="4" style="padding: 0;">
                <div class="details-wrapper">
                    ${errorHtml}
                    
                    <div style="margin-bottom: 1rem; padding: 0.5rem; background: #252526; border: 1px solid #3e3e42; border-radius: 4px;">
                        <strong>Assertion Result:</strong> <span class="${resultClass}" style="font-weight:bold;">${assertResult}</span>
                    </div>

                    <div style="display: flex; gap: 1rem;">
                        <div style="flex: 1;">
                            <div class="tabs">
                                <div class="tab active">Request Body</div>
                            </div>
                            <div class="code-container">
                                <button class="copy-btn" onclick="copyText('${index}-req')">Copy</button>
                                <pre id="${index}-req">${reqStr}</pre>
                            </div>
                        </div>
                        <div style="flex: 1;">
                            <div class="tabs">
                                <div class="tab active">Response Body</div>
                            </div>
                            <div class="code-container">
                                <button class="copy-btn" onclick="copyText('${index}-res')">Copy</button>
                                <pre id="${index}-res">${resStr}</pre>
                            </div>
                        </div>
                    </div>
                </div>
            </td>
        `;

        resultsBody.appendChild(tr);
        resultsBody.appendChild(detailsTr);
    });

    // Update Stats
    totalCountEl.innerText = results.length;
    successCountEl.innerText = successCount;
    failCountEl.innerText = results.length - successCount;

    resultsSection.classList.remove('hidden');
}

function toggleDetails(index) {
    const detailRow = document.getElementById(`detail-${index}`);
    if (detailRow.style.display === 'table-row') {
        detailRow.style.display = 'none';
        // Remove active class from parent row manually if needed
    } else {
        detailRow.style.display = 'table-row';
    }
}

function formatJSON(data) {
    // 1. If object, convert to string
    if (typeof data !== 'string') {
        data = JSON.stringify(data, null, 2);
    } else {
        // 2. Try to parse string as JSON to beautify it
        try {
            data = JSON.stringify(JSON.parse(data), null, 2);
        } catch (e) {
            // It's a plain string (HTML, text, etc.)
        }
    }

    // 3. Escape HTML characters to prevent rendering
    return data
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


window.copyText = (id) => {
    const text = document.getElementById(id).innerText;
    navigator.clipboard.writeText(text);
    // Optional: Show toast
};

function generateHTMLReport(results) {
    const date = new Date().toLocaleString();
    const successCount = results.filter(r => r.success).length;
    const failCount = results.length - successCount;

    let rows = '';
    results.forEach(res => {
        const statusClass = res.success ? 'pass' : 'fail';
        const resultText = res.success ? 'PASS' : 'FAIL';
        const reqBody = res.request_body ? formatJSON(res.request_body).replace(/</g, "&lt;") : '(No Body)';
        const resBody = res.response_body ? formatJSON(res.response_body).replace(/</g, "&lt;") : '(No Body)';

        rows += `
            <tr class="summary-row" onclick="this.nextElementSibling.classList.toggle('hidden')">
                <td><span class="badge ${res.method}">${res.method}</span></td>
                <td class="url-cell">${res.url}</td>
                <td class="status-cell ${statusClass}">${res.status_code || 'ERR'}</td>
                <td class="result-cell ${statusClass}">${resultText}</td>
            </tr>
            <tr class="detail-row hidden">
                <td colspan="4">
                    <div class="detail-content">
                        <div class="detail-section">
                            <strong>Assertion Result:</strong>
                            <span class="${statusClass}">${res.result || '-'}</span>
                        </div>
                        ${res.short_error ? `
                        <div class="detail-section">
                            <strong>Error:</strong>
                            <span class="fail">${res.short_error}</span>
                        </div>
                        ` : ''}
                        <div class="detail-grid">
                            <div>
                                <strong>Request Body:</strong>
                                <pre>${reqBody}</pre>
                            </div>
                            <div>
                                <strong>Response Body:</strong>
                                <pre>${resBody}</pre>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    });

    return `
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Test Report</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            background-color: #1e1e1e; 
            color: #d4d4d4; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            padding: 20px; 
            margin: 0;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: #61afef;
            margin-bottom: 10px;
        }
        .summary {
            background: #252526;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .summary-item {
            flex: 1;
            min-width: 150px;
        }
        .table-container {
            overflow-x: auto;
            background: #252526;
            border-radius: 8px;
            padding: 10px;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            min-width: 600px;
        }
        th, td { 
            padding: 12px 8px; 
            text-align: left; 
            border-bottom: 1px solid #333; 
            vertical-align: top;
        }
        th { 
            background-color: #2d2d30; 
            color: #fff; 
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        .badge { 
            padding: 4px 8px; 
            border-radius: 4px; 
            color: #fff; 
            font-size: 0.75em; 
            font-weight: bold;
            display: inline-block;
            min-width: 50px;
            text-align: center;
        }
        .GET { background-color: #61afef; }
        .POST { background-color: #e5c07b; color: #000; }
        .PUT { background-color: #98c379; color: #000; }
        .DELETE { background-color: #e06c75; }
        .PATCH { background-color: #c678dd; }
        .OPTIONS { background-color: #56b6c2; }
        
        .url-cell {
            max-width: 500px;
            word-break: break-all;
            overflow-wrap: break-word;
            font-size: 0.9em;
        }
        .status-cell {
            font-weight: bold;
            white-space: nowrap;
        }
        .result-cell {
            font-weight: bold;
            white-space: nowrap;
        }
        .hidden { display: none; }
        .summary-row { 
            cursor: pointer; 
            transition: background-color 0.2s;
        }
        .summary-row:hover { 
            background-color: #2c2c2d; 
        }
        .detail-row td {
            padding: 0 !important;
        }
        .detail-content {
            padding: 15px;
            background: #1e1e1e;
            border-left: 3px solid #61afef;
            margin: 5px 0;
        }
        .detail-section {
            margin-bottom: 15px;
        }
        .detail-section strong {
            color: #61afef;
            display: block;
            margin-bottom: 5px;
        }
        .detail-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 10px;
        }
        @media (max-width: 768px) {
            .detail-grid {
                grid-template-columns: 1fr;
            }
            .summary {
                flex-direction: column;
            }
        }
        pre {
            background: #0d1117;
            padding: 10px;
            border-radius: 4px;
            overflow: auto;
            max-height: 300px;
            font-size: 0.85em;
            margin: 0;
            border: 1px solid #30363d;
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
        }
        .pass { color: #73c990; }
        .fail { color: #fca0a0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 API Health Check Report</h1>
        <div class="summary">
            <div class="summary-item">
                <strong>Generated:</strong><br>${date}
            </div>
            <div class="summary-item">
                <strong>Total Requests:</strong><br>${results.length}
            </div>
            <div class="summary-item">
                <strong class="pass">Passed:</strong><br>${successCount}
            </div>
            <div class="summary-item">
                <strong class="fail">Failed:</strong><br>${failCount}
            </div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 80px;">Method</th>
                        <th>URL</th>
                        <th style="width: 100px;">Status</th>
                        <th style="width: 80px;">Result</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>`;
}

function downloadReport() {
    if (!currentResults) {
        alert("No results to download.");
        return;
    }

    // Generate HTML content
    const htmlContent = generateHTMLReport(currentResults);
    const blob = new Blob([htmlContent], { type: "text/html" });
    const url = URL.createObjectURL(blob);

    // Create link
    const a = document.createElement('a');
    a.href = url;
    a.download = `health_check_report_${new Date().toISOString().slice(0, 10)}.html`;
    document.body.appendChild(a);
    a.click();

    // Cleanup
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

document.getElementById('downloadBtn').addEventListener('click', downloadReport);
