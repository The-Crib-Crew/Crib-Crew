import { Link } from 'react-router-dom'

function HowItWorks() {
  return (
    <section className="how-page">
      <div className="how-intro">
        <p className="eyebrow">YOUR NEXT CHAPTER STARTS HERE</p>

        <h1>
          Finding your place in Dublin,
          <em> made simpler.</em>
        </h1>

        <p>
          Every neighbourhood has something different to offer.
          We'll help you find the one that fits your life, needs
          and budget.
        </p>
      </div>

      <div className="steps-grid">
        <article className="step-card">
          <span className="step-number">01</span>
          <div className="step-icon">⌂</div>
          <h2>Tell us about you</h2>
          <p>
            Share your budget, where you need to travel
            and the type of place you're looking for.
          </p>
        </article>

        <article className="step-card">
          <span className="step-number">02</span>
          <div className="step-icon">✳</div>
          <h2>Set your priorities</h2>
          <p>
            Choose what matters most to you, from affordable
            rent and transport to green spaces and local amenities.
          </p>
        </article>

        <article className="step-card">
          <span className="step-number">03</span>
          <div className="step-icon">⌖</div>
          <h2>Discover your match</h2>
          <p>
            Explore recommended Dublin districts and understand
            why each one could suit your lifestyle.
          </p>
        </article>
      </div>

      <div className="how-cta">
        <h2>Your Dublin story starts with a few questions.</h2>
        <Link className="button button-primary" to="/questionnaire">
          Find my match <span>→</span>
        </Link>
      </div>
    </section>
  )
}

export default HowItWorks
