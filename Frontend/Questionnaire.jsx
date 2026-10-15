
import { useState } from 'react'
import { Link } from 'react-router-dom'

function Questionnaire() {
  const [budget, setBudget] = useState(1000)
  const [destination, setDestination] = useState('')
  const [roomType, setRoomType] = useState('Private room')

  function handleContinue(event) {
    event.preventDefault()

    console.log({
      monthlyBudget: budget,
      commuteDestination: destination,
      accommodationType: roomType,
    })
  }

  return (
    <section className="questionnaire-page">
      <div className="questionnaire-container">
        <Link className="back-link" to="/">
          ← Back to home
        </Link>

        <p className="eyebrow">LET'S FIND YOUR PLACE</p>

        <div className="progress-info">
          <span>YOUR SITUATION</span>
          <span>STEP 1 OF 3</span>
        </div>

        <div className="progress-track">
          <div className="progress-fill" />
        </div>

        <h1>
          First, tell us a little
          <em> about your life.</em>
        </h1>

        <p className="questionnaire-description">
          We'll use your answers to find Dublin neighbourhoods
          that fit your budget and everyday routine.
        </p>

        <form onSubmit={handleContinue}>
          <div className="question-group">
            <label htmlFor="budget">
              What's your monthly accommodation budget?
            </label>

            <p className="field-hint">
              Enter the amount you can spend on rent each month.
            </p>

            <div className="budget-display">
              <span>Monthly budget</span>
              <strong>€{budget.toLocaleString('en-IE')}</strong>
            </div>

            <input
              id="budget"
              type="range"
              min="400"
              max="2500"
              step="50"
              value={budget}
              onChange={(event) =>
                setBudget(Number(event.target.value))
              }
            />

            <div className="range-labels">
              <span>€400</span>
              <span>€2,500+</span>
            </div>
          </div>

          
<div className="question-group">
  <label htmlFor="destination">
    Which university will you attend?
  </label>

  <p className="field-hint">
    Choose your university.
  </p>

  
<select
  id="destination"
  value={destination}
  onChange={(event) => setDestination(event.target.value)}
  required
>
  <option value="">Select</option>
  <option value="TU Dublin - Aungier Street">
    Technological University Dublin — Aungier Street Campus
  </option>
  <option value="TU Dublin - Bolton Street">
    Technological University Dublin — Bolton Street Campus
  </option>
  <option value="TU Dublin - Grangegorman">
    Technological University Dublin — Grangegorman Campus
  </option>
  <option value="TU Dublin - Blanchardstown">
    Technological University Dublin — Blanchardstown Campus
  </option>
  <option value="TU Dublin - Tallaght">
    Technological University Dublin — Tallaght Campus
  </option>
  <option value="University College Dublin">
    University College Dublin
  </option>
  <option value="Dublin City University">
    Dublin City University
  </option>
  <option value="Trinity College Dublin">
    Trinity College Dublin
  </option>
  <option value="Griffith College">
    Griffith College
  </option>
  <option value="National College of Ireland">
    National College of Ireland
  </option>
  <option value="Dublin Business School">
    Dublin Business School
  </option>
</select>
</div>


          <div className="question-group">
            <label>What type of accommodation do you prefer?</label>

            
<div className="room-options">
  {[
    '1 BHK apartment',
    '2 BHK apartment',
    'Private room',
    'Double sharing',
    'Student accommodation',
  ].map((type) => (
    <button
      key={type}
      type="button"
      className={
        roomType === type
          ? 'room-option selected'
          : 'room-option'
      }
      onClick={() => setRoomType(type)}
    >
      <span>
        {type === '1 BHK apartment' ? '⌂' :
         type === '2 BHK apartment' ? '⌂' :
         type === 'Private room' ? '▣' :
         type === 'Double sharing' ? '♧' :
         type === 'Student accommodation' ? '⌂' : '▢'}
      </span>
      {type}
      {roomType === type && <span>✓</span>}
    </button>
  ))}
</div>

          </div>

          <button className="questionnaire-next" type="submit">
            Continue <span>→</span>
          </button>
        </form>
      </div>
    </section>
  )
}

export default Questionnaire
