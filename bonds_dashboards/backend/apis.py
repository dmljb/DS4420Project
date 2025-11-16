from flask import Flask, jsonify
from flask_cors import CORS
from bonds import Bonds, bond_issuing_date, interest_rate, b1, b2
from portfolio import Portfolio, p1

app = Flask(__name__)
CORS(app)


@app.route('/api/bond')
def get_bond_data():
    b1 = Bonds(bond_issuing_date, 1000, 0.04, 10)
    
    return jsonify({
        'present_value': b1.present_value(interest_rate),
        'dv01': b1.dv01(interest_rate),
        'face_value': b1.face_value,
        'coupon_rate': b1.bond_interest
    })

@app.route('/api/portfolio')
def get_portfolio_data():
    try:
        # Get complete portfolio summary
        portfolio_summary = p1.get_portfolio_summary(interest_rate)
        
        return jsonify(portfolio_summary)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # choose a free port, e.g., 5050
    app.run(host="127.0.0.1", port=5050, debug=True)