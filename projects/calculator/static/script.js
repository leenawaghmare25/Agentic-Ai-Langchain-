document.addEventListener('DOMContentLoaded', () => {
    const expressionDisplay = document.getElementById('expression');
    const resultDisplay = document.getElementById('result');
    const buttons = document.querySelectorAll('.btn');
    
    let currentExpression = '';
    let justCalculated = false;

    // Helper to update the displays
    function updateDisplay() {
        let visualExpression = currentExpression
            .replace(/\*/g, ' × ')
            .replace(/\//g, ' ÷ ')
            .replace(/\+/g, ' + ')
            .replace(/-/g, ' − ');
            
        expressionDisplay.textContent = visualExpression;
        resultDisplay.classList.remove('text-error');
        
        if (resultDisplay.textContent.length > 10) {
            resultDisplay.style.fontSize = '24px';
        } else {
            resultDisplay.style.fontSize = '38px';
        }
    }

    // Append value
    function appendValue(value) {
        if (justCalculated) {
            if (['+', '-', '*', '/'].includes(value)) {
                currentExpression = resultDisplay.textContent;
            } else {
                currentExpression = '';
            }
            justCalculated = false;
        }
        
        const lastChar = currentExpression.slice(-1);
        if (['+', '-', '*', '/'].includes(lastChar) && ['+', '-', '*', '/'].includes(value)) {
            currentExpression = currentExpression.slice(0, -1) + value;
        } else {
            currentExpression += value;
        }
        updateDisplay();
    }

    // Clear display
    function clearAll() {
        currentExpression = '';
        resultDisplay.textContent = '0';
        updateDisplay();
    }

    // Delete last character
    function deleteLast() {
        if (justCalculated) {
            clearAll();
            return;
        }
        currentExpression = currentExpression.slice(0, -1);
        updateDisplay();
    }

    // Call Flask Backend to perform calculation
    async function calculateExpression() {
        if (!currentExpression) return;
        
        resultDisplay.textContent = '...';
        
        try {
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ expression: currentExpression })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                resultDisplay.textContent = data.result;
                justCalculated = true;
            } else {
                resultDisplay.textContent = data.message || 'Error';
                resultDisplay.classList.add('text-error');
                justCalculated = true;
            }
        } catch (error) {
            resultDisplay.textContent = 'Connection Error';
            resultDisplay.classList.add('text-error');
            justCalculated = true;
        }
    }

    // Click handler for grid buttons
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const val = button.getAttribute('data-val');
            const action = button.getAttribute('data-action');
            
            button.style.transform = 'scale(0.92)';
            setTimeout(() => {
                button.style.transform = '';
            }, 100);

            if (val) {
                appendValue(val);
            } else if (action === 'clear') {
                clearAll();
            } else if (action === 'backspace') {
                deleteLast();
            } else if (action === 'calculate') {
                calculateExpression();
            }
        });
    });

    // Keyboard support
    document.addEventListener('keydown', (event) => {
        const key = event.key;
        
        if (/[0-9]/.test(key)) {
            appendValue(key);
        } else if (['+', '-', '*', '/'].includes(key)) {
            appendValue(key);
        } else if (key === '.' || key === '(' || key === ')') {
            appendValue(key);
        } else if (key === 'Enter' || key === '=') {
            event.preventDefault();
            calculateExpression();
        } else if (key === 'Backspace') {
            deleteLast();
        } else if (key === 'Escape') {
            clearAll();
        }
    });
});
