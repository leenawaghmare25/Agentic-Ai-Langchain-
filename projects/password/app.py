from flask import Flask, request, jsonify, render_template
from secrets import choice
from string import ascii_letters, digits, punctuation

app = Flask(__name__)

@app.route('/generate', methods=['GET'])
def generate_password():
    length = int(request.args.get('length'))
    include_numbers = request.args.get('include_numbers') == 'true'
    include_special_characters = request.args.get('include_special_characters') == 'true'

    characters = ascii_letters
    if include_numbers:
        characters += digits
    if include_special_characters:
        characters += punctuation

    password = ''.join(choice(characters) for _ in range(length))
    return jsonify({'password': password})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)