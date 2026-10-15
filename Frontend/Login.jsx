
import { useState } from 'react'
import { Link } from 'react-router-dom'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  function handleLogin(event) {
    event.preventDefault()

    console.log('Login form submitted:', { email })
    alert('Login authentication will be connected later.')
  }

  return (
    <section className="login-page">
      <div className="login-card">
        <Link className="login-back" to="/">
          ← Back to home
        </Link>

        <div className="login-heading">
          <div className="login-mark">⌂</div>

          <p className="eyebrow">WELCOME BACK</p>

          <h1>
            Your Dublin story
            <em> continues here.</em>
          </h1>

          <p>
            Log in to continue exploring neighbourhoods
            that feel like home.
          </p>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="login-field">
            <label htmlFor="email">Email address</label>

            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
            />
          </div>

          <div className="login-field">
            <div className="password-label">
              <label htmlFor="password">Password</label>
              <span className="login-note">Keep it private</span>
            </div>

            <div className="password-input-wrap">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
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
          </div>

          <button type="submit" className="login-submit">
            Log in <span>→</span>
          </button>
        </form>

        <div className="login-divider">
          <span>YOUR NEXT CHAPTER</span>
        </div>

        
<p className="login-bottom">
  New to Find Your Dublin?
  <br />
  <Link to="/signup">Sign up →</Link>
</p>
      </div>
    </section>
  )
}

export default Login
