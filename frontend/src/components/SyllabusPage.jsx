import { useState } from 'react'
import './SyllabusPage.css'

function SyllabusPage() {
    const [syllabusText, setSyllabusText] = useState('')
    const [courseName, setCourseName] = useState('')
    const [parsedSyllabus, setParsedSyllabus] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')

    const handleTextSubmit = async () => {
        if (!syllabusText.trim()) {
            setError('Please enter your syllabus')
            return
        }

        setIsLoading(true)
        setError('')

        try {
            const formData = new FormData()
            formData.append('text', syllabusText)
            formData.append('course_name', courseName || 'My Course')

            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/syllabus/upload`, {
                method: 'POST',
                body: formData
            })

            if (!response.ok) {
                const errData = await response.json()
                throw new Error(errData.detail || 'Upload failed')
            }

            const data = await response.json()
            setParsedSyllabus(data.syllabus)
        } catch (err) {
            setError(err.message)
        } finally {
            setIsLoading(false)
        }
    }

    const handleFileUpload = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        setIsLoading(true)
        setError('')

        try {
            const formData = new FormData()
            formData.append('file', file)
            formData.append('course_name', courseName || file.name.replace(/\.[^/.]+$/, ''))

            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/syllabus/upload`, {
                method: 'POST',
                body: formData
            })

            if (!response.ok) {
                const errData = await response.json()
                throw new Error(errData.detail || 'Upload failed')
            }

            const data = await response.json()
            setParsedSyllabus(data.syllabus)
        } catch (err) {
            setError(err.message)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="syllabus-page">
            <div className="syllabus-header">
                <h2>📚 Add Your Syllabus</h2>
                <p>Upload your course syllabus to track your study progress</p>
            </div>

            <div className="syllabus-input-section">
                <div className="course-name-input">
                    <label>Course Name</label>
                    <input
                        type="text"
                        placeholder="e.g., Computer Science 101"
                        value={courseName}
                        onChange={(e) => setCourseName(e.target.value)}
                    />
                </div>

                <div className="input-methods">
                    <div className="text-input-card">
                        <h4>📝 Paste Syllabus Text</h4>
                        <textarea
                            placeholder={`Unit 1: Introduction
- Topic 1
- Topic 2

Unit 2: Advanced Concepts
- Topic 3
- Topic 4`}
                            value={syllabusText}
                            onChange={(e) => setSyllabusText(e.target.value)}
                        />
                        <button
                            className="submit-btn"
                            onClick={handleTextSubmit}
                            disabled={isLoading}
                        >
                            {isLoading ? '⏳ Processing...' : '🚀 Parse Syllabus'}
                        </button>
                    </div>

                    <div className="divider">
                        <span>OR</span>
                    </div>

                    <div className="file-input-card">
                        <h4>📄 Upload PDF/Text File</h4>
                        <div className="file-dropzone">
                            <input
                                type="file"
                                accept=".pdf,.txt"
                                onChange={handleFileUpload}
                                id="syllabus-file"
                            />
                            <label htmlFor="syllabus-file">
                                <span className="upload-icon">☁️</span>
                                <strong>Click to upload</strong>
                                <span className="file-types">PDF or TXT files</span>
                            </label>
                        </div>
                    </div>
                </div>

                {error && <div className="error-message">❌ {error}</div>}
            </div>

            {parsedSyllabus && (
                <div className="parsed-preview">
                    <h3>✅ Syllabus Parsed Successfully!</h3>
                    <div className="units-grid">
                        {parsedSyllabus.units.map((unit, idx) => (
                            <div key={idx} className="unit-card">
                                <div className="unit-header">
                                    <span className="unit-number">Unit {unit.number}</span>
                                    <h4>{unit.title}</h4>
                                </div>
                                <ul className="topics-list">
                                    {unit.topics.map((topic, tIdx) => (
                                        <li key={tIdx}>{topic.name}</li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                    <div className="syllabus-stats">
                        <span>📊 {parsedSyllabus.units.length} Units</span>
                        <span>📝 {parsedSyllabus.units.reduce((acc, u) => acc + u.topics.length, 0)} Topics</span>
                    </div>
                </div>
            )}
        </div>
    )
}

export default SyllabusPage
