import { useState } from 'react'
  import SearchForm from './components/SearchForm'
  import ProfileCard from './components/ProfileCard'
  import PostCard from './components/PostCard'

  export default function App() {
    const [loading, setLoading] = useState(false)
    const [error, setError]   = useState(null)
    const [data, setData]     = useState(null)

    async function handleSearch({ username, postLimit }) {
      setLoading(true)
      setError(null)
      setData(null)
      try {
        const res  = await fetch(`/api/scrape?username=${username}&posts=${postLimit}`)
        const json = await res.json()
        if (!res.ok) {
          setError(json.error || 'Error desconocido')
        } else {
          setData(json)
        }
      } catch {
        setError('No se pudo conectar con el servidor. ¿Está corriendo api.py?')
      } finally {
        setLoading(false)
      }
    }

    return (
      <div className="app">
        <header className="app-header">
          <h1 className="app-title">Instagram Scraper</h1>
          <p className="app-subtitle">Extrae perfil, posts y comentarios</p>
          <SearchForm onSearch={handleSearch} loading={loading} />
        </header>

        <main className="app-main">
          {loading && (
            <div className="loading">
              <div className="spinner" />
              <p>Obteniendo datos, esto puede tardar unos segundos…</p>
            </div>
          )}

          {error && !loading && (
            <div className="error-box">❌ {error}</div>
          )}

          {data && !loading && (
            <>
              <ProfileCard
                user={data.user_info}
                totalPosts={data.total_posts_found}
                totalComments={data.total_comments_collected}
              />
              <section className="posts-section">
                <h2 className="section-title">
                  Posts <span className="count-badge">{data.posts.length}</span>
                </h2>
                <div className="posts-list">
                  {data.posts.map((post, i) => (
                    <PostCard key={post.code} post={post} index={i + 1} />
                  ))}
                </div>
              </section>
            </>
          )}
        </main>
      </div>
    )
  }