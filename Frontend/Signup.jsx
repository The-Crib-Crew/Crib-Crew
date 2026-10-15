
import { useState } from 'react'
import { Link } from 'react-router-dom'

function Signup() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState('')

  function handleSignup(event) {
    event.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Your passwords do not match. Please try again.')
      return
    }

    alert('Your sign-up form is ready! Account creation will be connected later.')
  }

  return (
    <section className="login-page">
      <div className="login-card signup-card">
        <Link className="login-back" to="/">
          ← Back to home
        </Link>

        <div className="login-heading">
          <div className="login-mark">⌂</div>

          <p className="eyebrow">FIND YOUR PLACE</p>

          <h1>
            Make Dublin
            <em> feel like home.</em>
          </h1>

          <p>
            Create your account and start discovering
            neighbourhoods that fit your life.
          </p>
        </div>

        <form onSubmit={handleSignup} className="login-form">
          <div className="login-field">
            <label htmlFor="signup-name">Full name</label>
            <input
              id="signup-name"
              type="text"
              placeholder="Enter your full name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              autoComplete="name"
              required
            />
          </div>

          <div className="login-field">
            <label htmlFor="signup-email">Email address</label>
            <input
              id="signup-email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
            />
          </div>

          <div className="login-field">
            <label htmlFor="signup-password">Password</label>
            <div className="password-input-wrap">
              <input
                id="signup-password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Create a password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="new-password"
                minLength={8}
                required
              />

              <button
                type="button"
                className="show-password"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            <p className="signup-hint">Use at least 8 characters.</p>
          </div>

          <div className="login-field">
            <label htmlFor="confirm-password">Confirm password</label>
            <div className="password-input-wrap">
              <input
                id="confirm-password"
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="Enter your password again"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                autoComplete="new-password"
                minLength={8}
                required
              />

              <button
                type="button"
                className="show-password"
                onClick={() =>
                  setShowConfirmPassword(!showConfirmPassword)
                }
              >
                {showConfirmPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          {error && (
            <p className="signup-error" role="alert">
              {error}
            </p>
          )}

          <button type="submit" className="login-submit">
            Create account <span>→</span>
          </button>
        </form>

        <div className="login-divider">
          <span>YOUR DUBLIN JOURNEY</span>
        </div>

        <p className="login-bottom">
          Already have an account?
          <br />
          <Link to="/login">Log in →</Link>
        </p>
      </div>
    </section>
  )
}

export default Signup
