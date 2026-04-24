export default function PostCard({ post, index }) {
    return (
      <div className="post-card">
        <div className="post-header">
          <span className="post-number">Post #{index}</span>
          <a
            className="post-link"
            href={post.url}
            target="_blank"
            rel="noopener noreferrer"
          >
            Ver en Instagram ↗
          </a>
        </div>

        <div className="post-meta">
          {post.total_comments} comentario{post.total_comments !== 1 ? 's' : ''} en total
          {post.has_more_comments && ' · hay más'}
        </div>

        {post.error ? (
          <p className="post-error">⚠ {post.error}</p>
        ) : post.comments.length === 0 ? (
          <p className="post-error">Sin comentarios disponibles</p>
        ) : (
          <ul className="comments-list">
            {post.comments.map(c => (
              <li key={c.id} className="comment">
                <span className="comment-author">@{c.username}</span>
                <span className="comment-text">{c.text}</span>
                {c.likes > 0 && (
                  <div className="comment-footer">
                    <span className="comment-likes">♥ {c.likes}</span>
                    {c.reply_count > 0 && (
                      <span className="comment-likes">↩ {c.reply_count} respuestas</span>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    )
  }