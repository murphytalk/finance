"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from finance import app

@app.route('/')
@app.route('/summary')
def summary():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/stock')
def stock():
    """Renders the contact page."""
    return render_template(
        'stock.html',
        title='Stock & ETF',
        year=datetime.now().year
    )

@app.route('/fund')
def fund():
    """Renders the about page."""
    return render_template(
        'fund.html',
        title='Mutual Funds',
        year=datetime.now().year
    )
