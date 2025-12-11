
# main.py
from flask import Flask, render_template, request, session, redirect, url_for, flash
from itertools import product
from collections import Counter
import os  # <-- add this

app = Flask(__name__)

# Read SECRET_KEY from environment, fall back to a dev-only default if missing
app.secret_key = os.environ.get("SECRET_KEY", "dev-fallback-change-me")

def find_best_combination(rates, total_rate, min_units):
    max_multipliers = [int(total_rate // rate) for rate in rates]
    best_combo = None
    for multipliers in product(*(range(1, m + 1) for m in max_multipliers)):
        total_units = sum(multipliers)
        if total_units < min_units:
            continue
        total = sum(rate * count for rate, count in zip(rates, multipliers))
        if round(total, 2) == round(total_rate, 2):
            detailed_combo = []
            for rate, count in zip(rates, multipliers):
                detailed_combo.extend([rate] * count)
            best_combo = detailed_combo
            break
    return best_combo

@app.before_request
def track_visits():
    if 'visitor_count' not in session:
        session['visitor_count'] = 0
    if 'click_count' not in session:
        session['click_count'] = 0
    session['visitor_count'] += 1

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            session['click_count'] += 1
            total_rate = float(request.form['total_rate'])
            min_units = int(request.form['min_units'])
            rates_input = request.form['rates']

            if not rates_input.strip():
                flash('Rates input cannot be empty.', 'error')
                return redirect(url_for('index'))

            user_rates = [float(rate.strip()) for rate in rates_input.split(',') if rate.strip()]
            if not user_rates:
                flash('Please provide valid numeric rates.', 'error')
                return redirect(url_for('index'))

            best_match = find_best_combination(user_rates, total_rate, min_units)

            if best_match:
                rate_counts = Counter(best_match)
                return render_template(
                    'result.html',
                    rate_counts=rate_counts,
                    total_units=len(best_match),
                    total_rate=sum(best_match),
                    visitor_count=session['visitor_count'],
                    click_count=session['click_count']
                )
            else:
                flash('No valid combination found.', 'info')
                return render_template(
                    'result.html',
                    rate_counts=None,
                    visitor_count=session['visitor_count'],
                    click_count=session['click_count']
                )
        except ValueError:
            flash('Invalid input. Please enter numeric values only.', 'error')
            return redirect(url_for('index'))

    return render_template(
        'index.html',
        visitor_count=session.get('visitor_count', 0),
        click_count=session.get('click_count', 0)
    )

if __name__ == '__main__':
    app.run(debug=True)
