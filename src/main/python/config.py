"""
Application configurations
"""

"""
Brokers used in this deployment, a list of BrokerName
where BrokerName must be the class name of one of the Broker child classes defined in scraper.py
"""
BROKERS = (
    'UFJ',
#    'Nomura',
    'Suruga',
    'Nomura401K',
    'Saison',
    'Fidelity'
)

REPORT_EMAIL_ADDRESS = 'murphytalk+invest@gmail.com'
MAIL_FROM = "MyInvestMan <murphytalk@gmail.com>"
