
import { Link } from 'react-router-dom'

function Home() {
  return (
    <section className="hero" id="home">
      <div className="hero-content">
        <p className="eyebrow">
          A GUIDE TO FINDING YOUR PLACE IN DUBLIN
        </p>

        <h1>
          Find the Dublin neighbourhood{' '}
          <em>that feels like you.</em>
        </h1>

        <p className="hero-description">
          Moving to Dublin or looking for a new place to live?
          Discover neighbourhoods that fit your budget,
          daily journey and lifestyle.
        </p>

        <div className="hero-actions">
          <Link
            className="button button-primary"
            to="/questionnaire"
          >
            Find my match <span>→</span>
          </Link>

          <Link
            className="button button-secondary"
            to="/districts"
          >
            Explore districts <span>↗</span>
          </Link>
        </div>

        <div className="hero-note">
          <span className="note-icon">✳</span>
          <span>Less guesswork. More feeling at home.</span>
        </div>
      </div>

      <div className="hero-photo">
        
<img
  src="https://d2d5nznhz6f08p.cloudfront.net/blogs/best-areas-to-buy-a-house-in-dublin-for-buyers-and-property-investors-1773585123.webp"
  alt="Dublin residential neighbourhood"
 />


        <div className="photo-label">
          <span className="photo-dot" />
          <span>
            <strong>Your next chapter</strong>
            <small>Dublin, Ireland</small>
          </span>
        </div>

        <div className="floating-card">
          <span className="floating-icon">⌖</span>
          <span>
            <strong>Your life, your priorities</strong>
            <small>Find areas that fit you</small>
          </span>
        </div>
      </div>
    </section>
  )
}

export default Home

