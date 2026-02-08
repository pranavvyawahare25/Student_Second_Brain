import React from 'react'
import { courseTemplates } from '../data/templates'
import './CourseCatalog.css'

function CourseCatalog({ onEnroll }) {
    return (
        <div className="course-catalog">
            <div className="catalog-header">
                <h1>📚 Course Catalog</h1>
                <p>Select a course to add to your personal workspace.</p>
            </div>

            <div className="catalog-grid">
                {courseTemplates.map(template => (
                    <div key={template.id} className="catalog-card">
                        <div className="catalog-icon">{template.icon}</div>
                        <h3>{template.title}</h3>
                        <p>{template.description}</p>
                        <button
                            className="enroll-btn"
                            onClick={() => onEnroll(template)}
                        >
                            Enroll Now
                        </button>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default CourseCatalog
