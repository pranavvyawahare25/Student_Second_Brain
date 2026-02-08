import './CourseOverview.css'

function CourseOverview({ course }) {
    // Calculate stats
    const totalUnits = course.units?.length || 0
    const totalLectures = course.units?.reduce((acc, unit) => acc + (unit.lectures?.length || 0), 0) || 0

    // Simulated progress
    const progress = 35 // Mock value

    return (
        <div className="course-overview">
            <div className="overview-header">
                <div className="header-info">
                    <h1>{course.title}</h1>
                    <p>{course.description}</p>
                </div>
                <div className="progress-card">
                    <div className="progress-ring">
                        <svg viewBox="0 0 36 36" className="circular-chart">
                            <path className="circle-bg"
                                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            />
                            <path className="circle"
                                strokeDasharray={`${progress}, 100`}
                                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            />
                        </svg>
                        <span className="progress-text">{progress}%</span>
                    </div>
                    <div className="progress-info">
                        <strong>Course Progress</strong>
                        <span>Keep it up! 🚀</span>
                    </div>
                </div>
            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <span className="stat-icon">📚</span>
                    <div className="stat-content">
                        <h3>{totalUnits}</h3>
                        <p>Total Units</p>
                    </div>
                </div>
                <div className="stat-card">
                    <span className="stat-icon">📹</span>
                    <div className="stat-content">
                        <h3>{totalLectures}</h3>
                        <p>Lectures</p>
                    </div>
                </div>
                <div className="stat-card">
                    <span className="stat-icon">📄</span>
                    <div className="stat-content">
                        <h3>AI Ready</h3>
                        <p>Assistant Enabled</p>
                    </div>
                </div>
            </div>

            <div className="getting-started">
                <h3>Getting Started</h3>
                <p>Welcome to <strong>{course.title}</strong>! To begin your learning journey, select a unit and lecture from the sidebar on the left.</p>
                <div className="highlight-box">
                    <span className="lightbulb">💡</span>
                    <p>Tip: You can use the AI assistant at the bottom to ask questions about the course content anytime.</p>
                </div>
            </div>
        </div>
    )
}

export default CourseOverview
