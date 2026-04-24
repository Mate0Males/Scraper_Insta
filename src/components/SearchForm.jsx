import { useState } from 'react'

  export default function SearchForm({ onSearch, loading }) {
    const [username,  setUsername]  = useState('')
    const [postLimit, setPostLimit] = useState(10)

    function handleSubmit(e) {
      e.preventDefault()
      if (username.trim()) onSearch({ username: username.trim(), postLimit })
    }

    return (
      <form className="search-form" onSubmit={handleSubmit}>
        <input
          className="search-input"
          type="text"
          placeholder="@username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          disabled={loading}
          required
        />
        <input
          className="search-input search-input-small"
          type="number"
          min={1}
          max={20}
          value={postLimit}
          onChange={e => setPostLimit(Number(e.target.value))}
          disabled={loading}
          title="Número de posts"
        />
        <button className="search-btn" type="submit" disabled={loading || !username.trim()}>
          {loading ? 'Buscando…' : 'Buscar'}
        </button>
      </form>
    )
  }