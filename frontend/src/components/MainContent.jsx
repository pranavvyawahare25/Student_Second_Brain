import { useUser, SignUpButton } from '@clerk/clerk-react'
import LectureDetail from './LectureDetail'
import CourseOverview from './CourseOverview'
import ChatSection from './ChatSection'
import UserProfile from './UserProfile'
import './MainContent.css'

function MainContent({
    selectedCourse,
    selectedUnit,
    selectedLecture,
    selectedLectureId,
    onSaveMaterials,
    chatHistory,
    onSendQuery,
    showProfile
}) {
    const { isSignedIn } = useUser()

    // Show user profile
    if (showProfile) {
        return (
            <main className="main-content">
                <div className="content-header">
                    <h2>👤 My Profile</h2>
                    <p>Manage your account and view learning progress</p>
                </div>
                <UserProfile />
            </main>
        )
    }

    // Welcome screen/Landing Page for Guest Users
    if (!isSignedIn) {
        return (
            <main className="main-content landing-page">
                <section className="hero-section">
                    <div className="hero-content">
                        <span className="hero-tag">✨ AI-Powered Academic System</span>
                        <h1>Unlock Your Full Potential with Intelligent Learning</h1>
                        <p>Streamline your study flow with our advanced knowledge management platform. Organize materials, chat with your documents, and master complex subjects faster than ever.</p>
                        <SignUpButton mode="modal">
                            <button className="cta-btn primary">Get Started Now — It's Free</button>
                        </SignUpButton>
                    </div>
                </section>

                <section className="features-grid">
                    <div className="landing-feature-card">
                        <div className="feature-icon">🤖</div>
                        <h3>AI Research Assistant</h3>
                        <p>Get instant answers from your lecture notes and PDFs using our RAG-powered chatbot.</p>
                    </div>
                    <div className="landing-feature-card">
                        <div className="feature-icon">📂</div>
                        <h3>Smart Organization</h3>
                        <p>Automatically categorize video, audio, and documents into neat course units and lectures.</p>
                    </div>
                    <div className="landing-feature-card">
                        <div className="feature-icon">📊</div>
                        <h3>Progress Analytics</h3>
                        <p>Track your learning journey with interactive dashboards and personalized insights.</p>
                    </div>
                </section>

                <div className="landing-footer">
                    <p>© 2026 Intelligent Academic Knowledge. All rights reserved.</p>
                </div>
            </main>
        )
    }

    // Welcome screen when signed in but no course selected
    if (!selectedCourse) {
        return (
            <main className="main-content">
                <div className="welcome-card">
                    <div className="welcome-icon">🚀</div>
                    <h2>Welcome Back to Your Portal</h2>
                    <p>Select a course from the sidebar to continue your AI-powered learning journey.</p>
                    <div className="feature-badges">
                        <span className="badge">📹 Video Lectures</span>
                        <span className="badge">📄 PDF Notes</span>
                        <span className="badge">🤖 AI Assistant</span>
                    </div>
                </div>
            </main>
        )
    }

    // Course view for Logged-In Users
    return (
        <main className="main-content">
            <div className="content-detail">
                {selectedLecture ? (
                    <>
                        <div className="content-header">
                            <h2>{selectedCourse.title}</h2>
                            <p>{selectedCourse.description}</p>
                        </div>
                        <LectureDetail
                            lecture={selectedLecture}
                            onSaveMaterials={onSaveMaterials}
                        />
                    </>
                ) : (
                    <CourseOverview course={selectedCourse} />
                )}
            </div>

            <ChatSection
                chatHistory={chatHistory}
                onSendQuery={onSendQuery}
            />
        </main>
    )
}

export default MainContent
