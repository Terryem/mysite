from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import os

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'default_fallback_key')

# Database configuration
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='fortune2'
    )
    return conn

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            full_name = request.form['full_name']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            country = request.form['country']
            ref_by = request.form.get('ref_by', None)  # Optional field

            print(f"Received data: username={username}, full_name={full_name}, email={email}, phone={phone}, password={password}, country={country}, ref_by={ref_by}")

            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if the email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Email already registered!', 'danger')
                return redirect(url_for('register'))

            # Insert the new user into the database
            cursor.execute("""
                           INSERT INTO users (username, full_name, email, phone, password, country, ref_by)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           """, (username, full_name, email, phone, password, country, ref_by))
            conn.commit()  # Save the changes
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except KeyError as e:
            flash(f'Missing form field: {e}', 'danger')
        except Exception as e:
            flash('There was an issue with your registration. Please try again later.', 'danger')
            print(f"An error occurred: {e}")
            conn.rollback()  # Rollback in case of error
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            # Set session variables
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['full_name'] = user[2]
            session['email'] = user[3]
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:
            flash('Invalid email or password!', 'danger')

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch the user's data from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT u.username, u.full_name, 
           COALESCE(t.total_profit, 0) AS total_profit, 
           COALESCE(t.total_bonus, 0) AS total_bonus, 
           COALESCE(t.referral_bonus, 0) AS referral_bonus, 
           COALESCE(t.total_deposit, 0) AS total_deposit, 
           COALESCE(t.total_withdrawal, 0) AS total_withdrawal,
           COALESCE(t.total_investments, 0) AS total_investments,
           COALESCE(t.active_investments, 0) AS active_investments
    FROM users u
    LEFT JOIN transactions t ON u.id = t.user_id
    WHERE u.id = %s
    """
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        username = user_data['username']
        full_name = user_data['full_name']
        total_profit = user_data['total_profit']
        total_bonus = user_data['total_bonus']
        referral_bonus = user_data['referral_bonus']
        total_deposit = user_data['total_deposit']
        total_withdrawal = user_data['total_withdrawal']
        total_investments = user_data['total_investments']
        active_investments = user_data['active_investments']
        account_balance = total_deposit - total_withdrawal  # Assuming account balance is calculated this way
    else:
        username = 'Unknown User'
        full_name = 'No Name Available'
        total_profit = 0.00
        total_bonus = 0.00
        referral_bonus = 0.00
        total_deposit = 0.00
        total_withdrawal = 0.00
        total_investments = 0
        active_investments = 0
        account_balance = 0.00

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html',
        username=username,
        full_name=full_name,
        total_profit=total_profit,
        total_bonus=total_bonus,
        referral_bonus=referral_bonus,
        total_deposit=total_deposit,
        total_withdrawal=total_withdrawal,
        total_investments=total_investments,
        active_investments=active_investments,
        account_balance=account_balance
    )



@app.route('/about')
def about():
    username = session.get('email')  

    full_name = session.get('full_name') 
    return render_template('about.html', username=username, full_name=full_name)

@app.route('/terms')
def terms():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('terms.html', username=username, full_name=full_name)

@app.route('/trading_strategies')
def trading_strategies():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('trading_strategies.html', username=username, full_name=full_name)

@app.route('/risk_disclosure')
def risk_disclosure():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('risk_disclosure.html', username=username, full_name=full_name)

@app.route('/privacy_policy')
def privacy_policy():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('privacy_policy.html', username=username, full_name=full_name)

@app.route('/customer_agreement')
def customer_agreement():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('customer_agreement.html', username=username, full_name=full_name)

@app.route('/aml_policy')
def aml_policy():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('aml_policy.html', username=username, full_name=full_name)

@app.route('/google_login')
def google_login():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('google_login.html', username=username, full_name=full_name)

@app.route('/forgot_password')
def forgot_password():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('forgot_password.html', username=username, full_name=full_name)

@app.route('/auth_google_redirect')
def auth_google_redirect():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('auth_google_redirect.html', username=username, full_name=full_name)

@app.route('/markets')
def markets():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('markets.html', username=username, full_name=full_name)

@app.route('/contact')
def contact():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('contact.html', username=username, full_name=full_name)

@app.route('/education')
def education():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('education.html', username=username, full_name=full_name)

@app.route('/deposits')
def deposits():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('deposits.html', username=username, full_name=full_name)

@app.route('/support')
def support():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('support.html', username=username, full_name=full_name)

@app.route('/withdrawals')
def withdrawals():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('withdrawals.html', username=username, full_name=full_name)

@app.route('/trading_history')
def trading_history():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('trading_history.html', username=username, full_name=full_name)

@app.route('/account_settings')
def account_settings():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('account_settings.html', username=username, full_name=full_name)

@app.route('/buy-plan')
def buy_plan():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('buy-plan.html', username=username, full_name=full_name)

@app.route('/asset-balance')
def asset_balance():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('asset-balance.html', username=username, full_name=full_name)

@app.route('/manage-account-security')
def manage_account_security():
    username = session.get('email')  
    full_name = session.get('full_name') 
    return render_template('manage-account-security.html', username=username, full_name=full_name)

@app.route('/referuser')
def refer_user():
    username = session.get('email')  
    full_name = session.get('full_name')  
    url = 'solanafortune.net/ref'
    return render_template('referuser.html', url=url, username=username, full_name=full_name)

@app.route('/account_history')
def account_history():
    username = session.get('email')  
    full_name = session.get('full_name')  
    return render_template('account_history.html', username=username, full_name=full_name)

@app.route('/my_investment')
def my_investment():
    username = session.get('email')  
    full_name = session.get('full_name')  
    return render_template('my_investment.html', username=username, full_name=full_name)

if __name__ == '__main__':
    app.run(debug=True)