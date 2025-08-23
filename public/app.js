// PDF417 Driver's License Generator App
document.addEventListener('DOMContentLoaded', function() {
    console.log('PDF417 App initialized');
    
    // Get DOM elements
    const form = document.getElementById('dlForm');
    const generateBtn = document.getElementById('generateBtn');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const barcodeImg = document.getElementById('barcodeImage');
    const downloadLink = document.getElementById('downloadLink');
    const copyBtn = document.getElementById('copyBtn');
    const ansiOutput = document.getElementById('ansiOutput');
    const heightInches = document.getElementById('height_inches');
    const heightCm = document.getElementById('height_cm');

    // Height conversion helper
    function updateHeightCm() {
        const inches = parseFloat(heightInches.value);
        if (inches && inches > 0) {
            const cm = Math.round(inches * 2.54);
            heightCm.textContent = `${cm} cm`;
        } else {
            heightCm.textContent = '175 cm';
        }
    }

    // Add event listener for height conversion
    heightInches.addEventListener('input', updateHeightCm);

    // Form validation helpers
    function validateDateFormat(dateStr) {
        // Check if it's exactly 8 digits in MMDDYYYY format
        const dateRegex = /^\d{8}$/;
        if (!dateRegex.test(dateStr)) return false;
        
        const month = parseInt(dateStr.substring(0, 2));
        const day = parseInt(dateStr.substring(2, 4));
        const year = parseInt(dateStr.substring(4, 8));
        
        // Basic validation
        return month >= 1 && month <= 12 && 
               day >= 1 && day <= 31 && 
               year >= 1900 && year <= 2100;
    }

    function validateForm(formData) {
        const errors = [];
        
        // Required fields
        const requiredFields = [
            'dl_number', 'first_name', 'last_name', 'address', 
            'city', 'zip_code', 'sex', 'height_inches', 
            'birth_date', 'issue_date', 'expiry_date'
        ];
        
        requiredFields.forEach(field => {
            if (!formData[field] || formData[field].trim() === '') {
                errors.push(`${field.replace('_', ' ')} is required`);
            }
        });

        // Date format validation
        ['birth_date', 'issue_date', 'expiry_date'].forEach(dateField => {
            if (formData[dateField] && !validateDateFormat(formData[dateField])) {
                errors.push(`${dateField.replace('_', ' ')} must be in MMDDYYYY format`);
            }
        });

        // Zip code validation
        if (formData.zip_code && !/^\d{5}$/.test(formData.zip_code)) {
            errors.push('Zip code must be exactly 5 digits');
        }

        // Height validation
        const height = parseInt(formData.height_inches);
        if (height && (height < 36 || height > 96)) {
            errors.push('Height must be between 36 and 96 inches');
        }

        return errors;
    }

    function showErrors(errors) {
        // Create or update error display
        let errorDiv = document.querySelector('.error-messages');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-messages';
            errorDiv.style.cssText = `
                background: #fed7d7;
                border: 2px solid #e53e3e;
                color: #742a2a;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-size: 0.9rem;
            `;
            form.insertBefore(errorDiv, form.firstChild);
        }
        
        errorDiv.innerHTML = `
            <strong>Please fix the following errors:</strong>
            <ul style="margin: 8px 0 0 20px;">
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        `;
        
        // Scroll to top of form
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Remove error messages after 8 seconds
        setTimeout(() => {
            if (errorDiv) errorDiv.remove();
        }, 8000);
    }

    function removeErrors() {
        const errorDiv = document.querySelector('.error-messages');
        if (errorDiv) errorDiv.remove();
    }

    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Remove any existing errors
        removeErrors();
        
        // Get form data
        const formData = new FormData(form);
        const data = {};
        
        // Convert FormData to regular object
        for (let [key, value] of formData.entries()) {
            data[key] = value.toString().trim();
        }
        
        console.log('Form data:', data);
        
        // Validate form
        const errors = validateForm(data);
        if (errors.length > 0) {
            showErrors(errors);
            return;
        }
        
        // Show loading state
        generateBtn.disabled = true;
        generateBtn.innerHTML = '⏳ Generating...';
        loadingDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        
        try {
            // Make API request
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('API Response:', result);
            
            if (result.success && result.barcode) {
                // Display barcode
                barcodeImg.src = result.barcode;
                downloadLink.href = result.barcode;
                ansiOutput.textContent = result.ansi_data || 'ANSI data not available';
                
                // Show results
                loadingDiv.style.display = 'none';
                resultsDiv.style.display = 'block';
                
                // Scroll to results
                resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                // Success message
                showSuccessMessage('PDF417 barcode generated successfully!');
                
            } else {
                throw new Error('Invalid response from server');
            }
            
        } catch (error) {
            console.error('Error generating barcode:', error);
            
            // Hide loading
            loadingDiv.style.display = 'none';
            
            // Show error
            showErrors([`Error generating PDF417 barcode: ${error.message}`]);
        } finally {
            // Reset button
            generateBtn.disabled = false;
            generateBtn.innerHTML = '🔄 Generate PDF417 Barcode';
        }
    });

    function showSuccessMessage(message) {
        // Create success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.style.cssText = `
            background: #c6f6d5;
            border: 2px solid #38a169;
            color: #22543d;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            text-align: center;
        `;
        successDiv.textContent = message;
        
        // Insert at top of results
        resultsDiv.insertBefore(successDiv, resultsDiv.firstChild);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (successDiv) successDiv.remove();
        }, 5000);
    }

    // Copy to clipboard functionality
    copyBtn.addEventListener('click', async function() {
        try {
            if (barcodeImg.src) {
                // Convert base64 image to blob
                const response = await fetch(barcodeImg.src);
                const blob = await response.blob();
                
                // Copy to clipboard using the new Clipboard API
                if (navigator.clipboard && navigator.clipboard.write) {
                    await navigator.clipboard.write([
                        new ClipboardItem({
                            'image/png': blob
                        })
                    ]);
                    
                    // Show success feedback
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = '✅ Copied!';
                    copyBtn.style.background = '#c6f6d5';
                    copyBtn.style.color = '#22543d';
                    
                    setTimeout(() => {
                        copyBtn.textContent = originalText;
                        copyBtn.style.background = '';
                        copyBtn.style.color = '';
                    }, 2000);
                } else {
                    throw new Error('Clipboard API not supported');
                }
            }
        } catch (error) {
            console.error('Error copying to clipboard:', error);
            
            // Fallback - show a message to manually save
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '❌ Use Download Instead';
            copyBtn.style.background = '#fed7d7';
            copyBtn.style.color = '#742a2a';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '';
                copyBtn.style.color = '';
            }, 3000);
        }
    });

    // Auto-fill with demo data for testing
    function fillDemoData() {
        const demoData = {
            dl_number: '091076664',
            first_name: 'STANLEY',
            last_name: 'Crooms',
            middle_name: 'David',
            address: '2110 Old Maple Ln',
            city: 'Durham',
            zip_code: '37745',
            sex: 'M',
            height_inches: '69',
            birth_date: '04151988',
            issue_date: '07282025',
            expiry_date: '07282033'
        };
        
        Object.entries(demoData).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) element.value = value;
        });
        
        updateHeightCm();
    }

    // Add demo data button for development/testing
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        const demoBtn = document.createElement('button');
        demoBtn.type = 'button';
        demoBtn.className = 'btn-secondary';
        demoBtn.textContent = '🧪 Fill Demo Data';
        demoBtn.onclick = fillDemoData;
        
        const actions = document.querySelector('.form-actions');
        actions.appendChild(demoBtn);
    }

    // Initialize
    updateHeightCm();
    console.log('PDF417 Generator ready!');
});
