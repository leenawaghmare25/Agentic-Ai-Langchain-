const lengthSlider = document.getElementById('length-slider');const lengthDisplay = document.getElementById('length-display');const includeNumbersCheckbox = document.getElementById('include-numbers');const includeSpecialCharactersCheckbox = document.getElementById('include-special-characters');const generatePasswordButton = document.getElementById('generate-password-button');const passwordText = document.getElementById('password-text');const copyToClipboardButton = document.getElementById('copy-to-clipboard-button');

lengthSlider.addEventListener('input', () => {
    lengthDisplay.textContent = lengthSlider.value;
});

generatePasswordButton.addEventListener('click', async () => {
    const length = parseInt(lengthSlider.value);
    const includeNumbers = includeNumbersCheckbox.checked;
    const includeSpecialCharacters = includeSpecialCharactersCheckbox.checked;

    const response = await fetch(`/generate?length=${length}&include_numbers=${includeNumbers}&include_special_characters=${includeSpecialCharacters}`);

    const data = await response.json();
    passwordText.textContent = data.password;

    copyToClipboardButton.disabled = false;
});

copyToClipboardButton.addEventListener('click', () => {
    navigator.clipboard.writeText(passwordText.textContent);
    alert('Password copied to clipboard!');
});

copyToClipboardButton.disabled = true;