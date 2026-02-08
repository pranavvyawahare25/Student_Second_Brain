import { useState, useEffect } from 'react'
import './LectureDetail.css'

import { uploadFile, getSummary, getResearch } from '../services/api'

function LectureDetail({ lecture, onSaveMaterials }) {
    const [pendingFiles, setPendingFiles] = useState([])
    const [isUploading, setIsUploading] = useState(false)
    const [uploadStatus, setUploadStatus] = useState('')
    const [suggestions, setSuggestions] = useState([])
    const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false)

    useEffect(() => {
        if (lecture) {
            fetchSuggestions()
        }
    }, [lecture?.id])

    const fetchSuggestions = async () => {
        if (!lecture) return
        setIsLoadingSuggestions(true)
        try {
            // We use the lecture title as the topic for suggestions
            const topic = lecture.title
            const data = await getSummary(topic)

            if (data && data.insights && data.insights.key_concepts) {
                const formattedSuggestions = data.insights.key_concepts.slice(0, 5).map((concept, index) => {
                    const icons = ['🎯', '📝', '🔗', '🧪', '📚']
                    const headers = ['Key Concept', 'Active Recall', 'Contextual Link', 'Mini Experiment', 'Extended Reading']
                    return {
                        icon: icons[index % icons.length],
                        header: concept,
                        text: data.insights.step_by_step_explanation[index] || `Explore deeper into ${concept} for a better understanding.`
                    }
                })
                setSuggestions(formattedSuggestions)
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error)
            // Fallback to empty if error
            setSuggestions([])
        } finally {
            setIsLoadingSuggestions(false)
        }
    }

    if (!lecture) {
        return (
            <div className="lecture-detail">
                <div className="empty-state">
                    <span className="empty-icon">📂</span>
                    <p>Select a lecture to view and upload materials</p>
                </div>
            </div>
        )
    }

    const handleFileChange = (e) => {
        const files = Array.from(e.target.files)
        setPendingFiles(prev => [...prev, ...files])
        setUploadStatus('')
    }

    const removePendingFile = (index) => {
        setPendingFiles(prev => prev.filter((_, i) => i !== index))
    }

    const handleSave = async (e) => {
        if (e) e.preventDefault()

        setIsUploading(true)
        setUploadStatus('Uploading materials to AI backend...')

        const categorized = {
            video: lecture.materials.video,
            audio: lecture.materials.audio,
            pdf: lecture.materials.pdf,
            images: [...(lecture.materials.images || [])]
        }

        try {
            for (const file of pendingFiles) {
                let type = ''
                if (file.type.startsWith('video/')) type = 'video'
                else if (file.type.startsWith('audio/')) type = 'audio'
                else if (file.type === 'application/pdf') type = 'pdf'
                else if (file.type.startsWith('image/')) type = 'image'

                if (type) {
                    await uploadFile(file, type)

                    // Update local state based on type
                    if (type === 'video') categorized.video = file
                    else if (type === 'audio') categorized.audio = file
                    else if (type === 'pdf') categorized.pdf = file
                    else if (type === 'image') categorized.images.push(file)
                }
            }

            onSaveMaterials(categorized)
            setPendingFiles([])
            setUploadStatus('Upload complete! ✨ AI processing started.')
            setTimeout(() => setUploadStatus(''), 3000)

            // Re-fetch suggestions after upload
            fetchSuggestions()
        } catch (error) {
            console.error('Upload failed:', error)
            setUploadStatus('❌ Upload failed. Please try again.')
        } finally {
            setIsUploading(false)
        }
    }

    const getFileIcon = (type) => {
        if (type.startsWith('video/')) return '📹'
        if (type.startsWith('audio/')) return '🎵'
        if (type === 'application/pdf') return '📄'
        if (type.startsWith('image/')) return '🖼️'
        return '📁'
    }

    const mat = lecture.materials

    return (
        <div className="lecture-detail">
            <h4>{lecture.title}</h4>

            <div className="detail-body">
                <div className="detail-left">
                    <div className="materials-section">
                        <h5>📁 Current Materials</h5>
                        <div className="materials-grid">
                            <div className="material-card">
                                <span className="mat-icon">📹</span>
                                <span className="mat-label">Video</span>
                                <span className="mat-value">{mat.video ? mat.video.name : 'None'}</span>
                            </div>
                            <div className="material-card">
                                <span className="mat-icon">🎵</span>
                                <span className="mat-label">Audio</span>
                                <span className="mat-value">{mat.audio ? mat.audio.name : 'None'}</span>
                            </div>
                            <div className="material-card">
                                <span className="mat-icon">📄</span>
                                <span className="mat-label">PDF</span>
                                <span className="mat-value">{mat.pdf ? mat.pdf.name : 'None'}</span>
                            </div>
                            <div className="material-card">
                                <span className="mat-icon">🖼️</span>
                                <span className="mat-label">Images</span>
                                <span className="mat-value">{mat.images?.length > 0 ? `${mat.images.length} files` : 'None'}</span>
                            </div>
                        </div>
                    </div>

                    <div className="upload-section">
                        <h5>⬆️ Upload New Materials</h5>
                        <div className="unified-dropzone">
                            <input
                                type="file"
                                id="file-upload"
                                multiple
                                onChange={handleFileChange}
                                accept="video/*,audio/*,application/pdf,image/*"
                            />
                            <label htmlFor="file-upload">
                                <span className="dropzone-icon">☁️</span>
                                <strong>Click to upload</strong> or drag and drop
                                <span className="supported-formats">Audio, Video, PDF, Images</span>
                            </label>
                        </div>

                        {pendingFiles.length > 0 && (
                            <div className="pending-files">
                                <h6>Pending Uploads ({pendingFiles.length})</h6>
                                <div className="pending-list">
                                    {pendingFiles.map((file, idx) => (
                                        <div key={idx} className="pending-file-item">
                                            <span>{getFileIcon(file.type)}</span>
                                            <span className="file-name">{file.name}</span>
                                            <button className="remove-file" onClick={() => removePendingFile(idx)}>×</button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {uploadStatus && <div className="upload-status-msg">{uploadStatus}</div>}

                        <button
                            type="button"
                            className="save-btn"
                            onClick={handleSave}
                            disabled={pendingFiles.length === 0 || isUploading}
                        >
                            {isUploading ? '⏳ Uploading...' : '💾 Save & Process'}
                        </button>
                    </div>
                </div>

                <div className="detail-right">
                    <div className="suggestions-section">
                        <div className="suggestions-header">
                            <h5>💡 AI Suggestions</h5>
                            <button
                                className={`refresh-sugg-btn ${isLoadingSuggestions ? 'loading' : ''}`}
                                title="Refresh Suggestions"
                                onClick={fetchSuggestions}
                                disabled={isLoadingSuggestions}
                            >
                                🔄
                            </button>
                        </div>
                        <div className="suggestions-container">
                            {isLoadingSuggestions ? (
                                <div className="suggestions-loading">
                                    <div className="skeleton-loader"></div>
                                    <div className="skeleton-loader"></div>
                                    <div className="skeleton-loader"></div>
                                </div>
                            ) : suggestions.length > 0 ? (
                                suggestions.map((sugg, idx) => (
                                    <div key={idx} className="suggestion-card animate-in" style={{ animationDelay: `${idx * 0.1}s` }}>
                                        <div className="sugg-icon-wrapper">
                                            <span className="sugg-icon">{sugg.icon}</span>
                                        </div>
                                        <div className="sugg-content">
                                            <h6>{sugg.header}</h6>
                                            <p>{sugg.text}</p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="no-suggestions">
                                    <p>Upload materials to get AI-powered study suggestions.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}


export default LectureDetail
