import { useState } from 'react'

  function fmt(n) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
    if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K'
    return n?.toLocaleString() ?? '—'
  }

  export default function ProfileCard({ user, totalPosts, totalComments }) {
    const [imgError, setImgError] = useState(false)

    return (
      <div className="profile-card">
        <div className="profile-avatar-wrap">
          {user.profile_pic_url && !imgError ? (
            <img
              className="profile-avatar"
              src={user.profile_pic_url}
              alt={user.username}
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="profile-avatar-placeholder">
              {user.username?.[0]?.toUpperCase() ?? '?'}
            </div>
          )}
        </div>

        <div className="profile-info">
          <div className="profile-username">@{user.username}</div>
          {user.full_name && <div className="profile-fullname">{user.full_name}</div>}
          {user.biography && <p className="profile-bio">{user.biography}</p>}

          <div className="profile-stats">
            <div className="stat">
              <span className="stat-value">{fmt(user.follower_count)}</span>
              <span className="stat-label">Seguidores</span>
            </div>
            <div className="stat">
              <span className="stat-value">{fmt(user.following_count)}</span>
              <span className="stat-label">Siguiendo</span>
            </div>
            <div className="stat">
              <span className="stat-value">{fmt(user.post_count)}</span>
              <span className="stat-label">Posts</span>
            </div>
            <div className="stat stat-highlight">
              <span className="stat-value">{totalPosts}</span>
              <span className="stat-label">Extraídos</span>
            </div>
            <div className="stat stat-highlight">
              <span className="stat-value">{totalComments}</span>
              <span className="stat-label">Comentarios</span>
            </div>
          </div>
        </div>
      </div>
    )
  }