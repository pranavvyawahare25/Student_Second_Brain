import { useState } from 'react'
import './LecturePanel.css'

function LecturePanel({
    units,
    selectedLectureId,
    onSelectLecture,
    onAddUnit,
    onDeleteUnit,
    onAddLecture,
    onDeleteLecture
}) {
    const [expandedUnits, setExpandedUnits] = useState({})
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(null) // { type: 'unit'|'lecture', unitId, lectureId }

    const toggleUnit = (unitId) => {
        setExpandedUnits(prev => ({
            ...prev,
            [unitId]: !prev[unitId]
        }))
    }

    const handleDeleteClick = (e, type, unitId, lectureId = null) => {
        e.stopPropagation()
        setShowDeleteConfirm({ type, unitId, lectureId })
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
        <div className="lecture-panel">
            <div className="panel-header">
                <h4>📂 Course Content</h4>
                <button className="add-unit-btn" onClick={onAddUnit} title="Add New Unit">
                    + Unit
                </button>
            </div>
            <div className="unit-list">
                {units.map(unit => (
                    <div key={unit.id} className={`unit-item ${expandedUnits[unit.id] ? 'expanded' : ''}`}>
                        <div className="unit-header" onClick={() => toggleUnit(unit.id)}>
                            <span className="unit-caret">{expandedUnits[unit.id] ? '▼' : '▶'}</span>
                            <span className="unit-title">{unit.title}</span>
                            <div className="unit-actions">
                                <button
                                    className="add-lec-inline-btn"
                                    onClick={(e) => { e.stopPropagation(); onAddLecture(unit.id); }}
                                    title="Add Lecture to this Unit"
                                >
                                    +
                                </button>
                                <button
                                    className="delete-unit-btn"
                                    onClick={(e) => handleDeleteClick(e, 'unit', unit.id)}
                                    title="Delete Unit"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>

                        {expandedUnits[unit.id] && (
                            <ul className="lecture-list nested">
                                {unit.lectures.map(lecture => (
                                    <li key={lecture.id}>
                                        <button
                                            className={`lecture-item ${selectedLectureId === lecture.id ? 'active' : ''}`}
                                            onClick={() => onSelectLecture(unit.id, lecture.id)}
                                        >
                                            <span className="lecture-num">{lecture.id}</span>
                                            <span className="lecture-title">{lecture.title}</span>
                                            <button
                                                className="delete-lecture-btn"
                                                onClick={(e) => handleDeleteClick(e, 'lecture', unit.id, lecture.id)}
                                                title="Delete lecture"
                                            >
                                                🗑️
                                            </button>
                                        </button>
                                    </li>
                                ))}
                                {unit.lectures.length === 0 && (
                                    <li className="empty-msg">No lectures in this unit.</li>
                                )}
                            </ul>
                        )}
                    </div>
                ))}
                {units.length === 0 && (
                    <div className="empty-msg">No units yet. Click "+ Unit" to start.</div>
                )}
            </div>

            {/* Delete Confirmation Modal */}
            {showDeleteConfirm && (
                <div className="delete-modal-overlay" onClick={cancelDelete}>
                    <div className="delete-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-icon">⚠️</div>
                        <h3>Delete {showDeleteConfirm.type === 'unit' ? 'Unit' : 'Lecture'}?</h3>
                        <p>Are you sure you want to delete this {showDeleteConfirm.type}? This action cannot be undone.</p>
                        <div className="modal-actions">
                            <button className="cancel-btn" onClick={cancelDelete}>Cancel</button>
                            <button className="confirm-delete-btn" onClick={confirmDelete}>Delete</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default LecturePanel
