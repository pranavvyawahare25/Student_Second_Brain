import { useUser } from '@clerk/clerk-react'
import './UserProfile.css'

function UserProfile() {
    const { isLoaded, isSignedIn, user } = useUser()

    if (!isLoaded) {
        return (
            <div className="profile-loading">
                <div className="spinner"></div>
                <p>Loading profile...</p>
            </div>
        )
    }

    if (!isSignedIn) {
        return (
            <div className="profile-not-signed-in">
                <span className="profile-icon">🔐</span>
                <h3>Not Signed In</h3>
                <p>Sign in to access your profile and personalized learning experience.</p>
            </div>
        )
    }

    return (
        <div className="user-profile">
            <div className="profile-header">
                <img
                    src={user.imageUrl}
                    alt={user.fullName || 'User'}
                    className="profile-avatar"
                />
                <div className="profile-info">
                    <h3>{user.fullName || 'Student'}</h3>
                    <p className="profile-email">{user.primaryEmailAddress?.emailAddress}</p>
                    <span className="profile-badge">🎓 Active Learner</span>
                </div>
            </div>

            <div className="profile-stats">
                <div className="stat-card">
                    <span className="stat-value">5</span>
                    <span className="stat-label">Enrolled Courses</span>
                </div>
                <div className="stat-card">
                    <span className="stat-value">12</span>
                    <span className="stat-label">Lectures Completed</span>
                </div>
                <div className="stat-card">
                    <span className="stat-value">3</span>
                    <span className="stat-label">Certificates</span>
                </div>
            </div>

            <div className="profile-details">
                <h4>Account Details</h4>
                <div className="detail-row">
                    <span className="detail-label">Username</span>
                    <span className="detail-value">{user.username || 'Not set'}</span>
                </div>
                <div className="detail-row">
                    <span className="detail-label">Member Since</span>
                    <span className="detail-value">
                        {new Date(user.createdAt).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                        })}
                    </span>
                </div>
                <div className="detail-row">
                    <span className="detail-label">User ID</span>
                    <span className="detail-value user-id">{user.id.slice(0, 12)}...</span>
                </div>
            </div>
        </div>
    )
}

export default UserProfile
