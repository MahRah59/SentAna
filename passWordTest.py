

from werkzeug.security import generate_password_hash

def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            # Check if the hash is invalid
            try:
                if bcrypt.check_password_hash(user.password_hash, form.password.data):
                    # Successful login logic
                    login_user(user)
                else:
                    # Invalid password, re-hash and update in DB
                    new_password_hash = generate_password_hash(form.password.data)
                    user.password_hash = new_password_hash
                    db.session.commit()
                    flash('Password was re-hashed. Please log in again.', 'warning')
                    return redirect(url_for('login'))
            except ValueError:
                flash('Invalid password hash, please reset your password.', 'danger')
                return redirect(url_for('reset_password'))  # Redirect to reset password if necessary
        else:
            flash('Login failed. Invalid credentials.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', title='Login', form=form)
