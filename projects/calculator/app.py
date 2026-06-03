import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

SAFE_PATTERN = re.compile(r'^[0-9+\-*/\s().]+$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        if not data or 'expression' not in data:
            return jsonify({'status': 'error', 'message': 'No expression provided'}), 400
            
        expression = str(data['expression']).strip()
        
        if not expression:
            return jsonify({'status': 'error', 'message': 'Empty expression'}), 400
            
        if not SAFE_PATTERN.match(expression):
            return jsonify({'status': 'error', 'message': 'Invalid characters in expression'}), 400
            
        try:
            result = eval(expression, {"__builtins__": None}, {})
            if isinstance(result, float):
                result = round(result, 10)
                if result.is_integer():
                    result = int(result)
            return jsonify({
                'status': 'success',
                'result': str(result)
            })
        except ZeroDivisionError:
            return jsonify({'status': 'error', 'message': 'Cannot divide by zero'})
        except (SyntaxError, NameError, TypeError, ValueError):
            return jsonify({'status': 'error', 'message': 'Malformed expression'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
