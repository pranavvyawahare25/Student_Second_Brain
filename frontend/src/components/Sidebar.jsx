import { useState } from 'react'
import { useUser } from '@clerk/clerk-react'
import './Sidebar.css'

function Sidebar({
    isOpen,
    onClose,
    courses,
    selectedCourseId,
    selectedUnitId,
    selectedLectureId,
    onSelectCourse,
    onAddCourse,
    onAddUnit,
    onDeleteUnit,
    onAddLecture,
    onDeleteLecture,
    onSelectLecture,
    showProfile,
    onToggleProfile,
    onShowCatalog
}) {
    const { isSignedIn, user } = useUser()
    const [showAddCourseForm, setShowAddCourseForm] = useState(false)
    const [newCourseTitle, setNewCourseTitle] = useState('')
    const [newCourseDesc, setNewCourseDesc] = useState('')
    const [expandedCourses, setExpandedCourses] = useState({})
    const [expandedUnits, setExpandedUnits] = useState({})
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(null) // { type: 'unit'|'lecture', unitId, lectureId, courseId }

    const toggleCourse = (courseId) => {
        setExpandedCourses(prev => ({
            ...prev,
            [courseId]: !prev[courseId]
        }))
        onSelectCourse(courseId)
    }

    const toggleUnit = (e, unitId) => {
        e.stopPropagation()
        setExpandedUnits(prev => ({
            ...prev,
            [unitId]: !prev[unitId]
        }))
    }

    const handleAddCourseSubmit = (e) => {
        e.preventDefault()
        if (newCourseTitle.trim()) {
            onAddCourse(newCourseTitle, newCourseDesc)
            setNewCourseTitle('')
            setNewCourseDesc('')
            setShowAddCourseForm(false)
        }
    }

    const handleDeleteClick = (e, type, courseId, unitId, lectureId = null) => {
        e.stopPropagation()
        setShowDeleteConfirm({ type, courseId, unitId, lectureId })
    }

    const confirmDelete = () => {
        if (!showDeleteConfirm) return
        if (showDeleteConfirm.type === 'unit') {
            onDeleteUnit(showDeleteConfirm.unitId)
        } else {
            onDeleteLecture(showDeleteConfirm.unitId, showDeleteConfirm.lectureId)
        }
        setShowDeleteConfirm(null)
    }

    const cancelDelete = () => {
        setShowDeleteConfirm(null)
    }

    return (
        <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
            <button className="mobile-close" onClick={onClose} aria-label="Close Menu">×</button>
            {isSignedIn && (
                <button
                    className={`profile-btn ${showProfile ? 'active' : ''}`}
                    onClick={onToggleProfile}
                >
                    <img src={user.imageUrl} alt="" className="mini-avatar" />
                    <span>My Profile</span>
                </button>
            )}

            {isSignedIn ? (
                <>
                    <div className="sidebar-header">
                        <h3 onClick={onShowCatalog} style={{ cursor: 'pointer' }} title="Click to view all courses">
                            📚 Courses
                        </h3>
                        <button className="add-btn" onClick={() => setShowAddCourseForm(!showAddCourseForm)}>
                            {showAddCourseForm ? '×' : '+'}
                        </button>
                    </div>

                    {showAddCourseForm && (
                        <form className="add-course-form" onSubmit={handleAddCourseSubmit}>
                            <input
                                type="text"
                                placeholder="Course title"
                                value={newCourseTitle}
                                onChange={(e) => setNewCourseTitle(e.target.value)}
                                required
                            />
                            <input
                                type="text"
                                placeholder="Description"
                                value={newCourseDesc}
                                onChange={(e) => setNewCourseDesc(e.target.value)}
                            />
                            <button type="submit" className="create-btn">Create</button>
                        </form>
                    )}

                    <ul className="course-list">
                        {courses.map(course => (
                            <li key={course.id} className={`course-container ${selectedCourseId === course.id ? 'active' : ''}`}>
                                <div
                                    className={`course-item-header ${selectedCourseId === course.id && !showProfile ? 'selected' : ''}`}
                                    onClick={() => toggleCourse(course.id)}
                                >
                                    <span className="course-icon">📖</span>
                                    <span className="course-title">{course.title}</span>
                                    <span className="expand-indicator">{expandedCourses[course.id] ? '▼' : '▶'}</span>
                                </div>

                                {expandedCourses[course.id] && (
                                    <div className="course-nested-content">
                                        <div className="unit-section-header">
                                            <span>Units</span>
                                            <button
                                                className="add-inline-btn"
                                                onClick={(e) => { e.stopPropagation(); onAddUnit(); }}
                                                title="Add Unit"
                                            >
                                                +
                                            </button>
                                        </div>
                                        <div className="unit-list-sidebar">
                                            {(course.units || []).map(unit => (
                                                <div key={unit.id} className="unit-container">
                                                    <div
                                                        className={`unit-item-header ${selectedUnitId === unit.id ? 'active' : ''}`}
                                                        onClick={(e) => toggleUnit(e, unit.id)}
                                                    >
                                                        <span className="unit-caret">{expandedUnits[unit.id] ? '▼' : '▶'}</span>
                                                        <span className="unit-title-sidebar">{unit.title}</span>
                                                        <div className="unit-actions-sidebar">
                                                            <button
                                                                className="add-lec-inline-btn"
                                                                onClick={(e) => { e.stopPropagation(); onAddLecture(unit.id); }}
                                                                title="Add Lecture"
                                                            >
                                                                +
                                                            </button>
                                                            <button
                                                                className="delete-small-btn"
                                                                onClick={(e) => handleDeleteClick(e, 'unit', course.id, unit.id)}
                                                                title="Delete Unit"
                                                            >
                                                                🗑️
                                                            </button>
                                                        </div>
                                                    </div>

                                                    {expandedUnits[unit.id] && (
                                                        <ul className="lecture-list-sidebar">
                                                            {unit.lectures.map(lecture => (
                                                                <li
                                                                    key={lecture.id}
                                                                    className={`lecture-item-sidebar ${selectedLectureId === lecture.id ? 'active' : ''}`}
                                                                    onClick={() => onSelectLecture(unit.id, lecture.id)}
                                                                >
                                                                    <span className="lec-dot">•</span>
                                                                    <span className="lecture-title-sidebar">{lecture.title}</span>
                                                                    <button
                                                                        className="delete-lec-small-btn"
                                                                        onClick={(e) => handleDeleteClick(e, 'lecture', course.id, unit.id, lecture.id)}
                                                                        title="Delete Lecture"
                                                                    >
                                                                        ×
                                                                    </button>
                                                                </li>
                                                            ))}
                                                            {unit.lectures.length === 0 && (
                                                                <li className="empty-sidebar-msg">No lectures</li>
                                                            )}
                                                        </ul>
                                                    )}
                                                </div>
                                            ))}
                                            {(course.units || []).length === 0 && (
                                                <div className="empty-sidebar-msg">No units yet</div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                </>
            ) : (
                <div className="sidebar-guest-msg">
                    <span className="guest-icon">🔒</span>
                    <p>Please sign in to access your courses and learning materials.</p>
                </div>
            )}

            {/* Delete Confirmation Modal (Sidebar Specific) */}
            {showDeleteConfirm && (
                <div className="delete-modal-overlay" onClick={cancelDelete}>
                    <div className="delete-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-icon">⚠️</div>
                        <h3>Delete {showDeleteConfirm.type}?</h3>
                        <p>Are you sure you want to delete this {showDeleteConfirm.type}?</p>
                        <div className="modal-actions">
                            <button className="cancel-btn" onClick={cancelDelete}>Cancel</button>
                            <button className="confirm-delete-btn" onClick={confirmDelete}>Delete</button>
                        </div>
                    </div>
                </div>
            )}
        </aside>
    )
}

export default Sidebar
