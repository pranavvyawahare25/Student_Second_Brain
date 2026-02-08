import { useState, useEffect } from 'react'
import { useUser } from '@clerk/clerk-react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import MainContent from './components/MainContent'
import CourseCatalog from './components/CourseCatalog'
import ThemeToggle from './components/ThemeToggle'
import './App.css'

function App() {
    const { user, isSignedIn } = useUser()
    const [courses, setCourses] = useState([])
    const [selectedCourseId, setSelectedCourseId] = useState(null)
    const [selectedUnitId, setSelectedUnitId] = useState(null)
    const [selectedLectureId, setSelectedLectureId] = useState(null)
    const [chatHistory, setChatHistory] = useState([])
    const [showProfile, setShowProfile] = useState(false)
    const [showCatalog, setShowCatalog] = useState(false)
    const [isSidebarOpen, setIsSidebarOpen] = useState(false)

    // Load courses from local storage when user changes
    useEffect(() => {
        if (isSignedIn && user) {
            const savedCourses = localStorage.getItem(`user_courses_${user.id}`)
            if (savedCourses) {
                setCourses(JSON.parse(savedCourses))
            } else {
                setCourses([]) // New user starts with empty list
            }
        } else {
            setCourses([])
        }
    }, [isSignedIn, user])

    // Save courses to local storage whenever they change
    useEffect(() => {
        if (isSignedIn && user && courses.length > 0) {
            localStorage.setItem(`user_courses_${user.id}`, JSON.stringify(courses))
        }
    }, [courses, isSignedIn, user])

    const selectedCourse = courses.find(c => c.id === selectedCourseId)
    const selectedUnit = selectedCourse?.units?.find(u => u.id === selectedUnitId)
    const selectedLecture = selectedUnit?.lectures?.find(l => l.id === selectedLectureId)

    const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen)

    const handleShowCatalog = () => {
        setShowCatalog(true)
        setSelectedCourseId(null)
        setSelectedUnitId(null)
        setSelectedLectureId(null)
        setShowProfile(false)
        setIsSidebarOpen(false)
    }

    const handleSelectCourse = (courseId) => {
        setSelectedCourseId(courseId)
        setSelectedUnitId(null)
        setSelectedLectureId(null)
        setShowProfile(false)
        setShowCatalog(false) // Hide catalog when a course is selected
        setIsSidebarOpen(false)
    }

    const handleEnrollCourse = (template) => {
        const newCourse = { ...template, id: Date.now() } // Ensure unique ID
        const updatedCourses = [...courses, newCourse]
        setCourses(updatedCourses)
        // Save immediately to ensure persistence
        if (user) {
            localStorage.setItem(`user_courses_${user.id}`, JSON.stringify(updatedCourses))
        }
        setSelectedCourseId(newCourse.id)
        setShowCatalog(false)
    }

    const handleToggleProfile = () => {
        setShowProfile(!showProfile)
        if (!showProfile) {
            setSelectedCourseId(null)
            setSelectedUnitId(null)
            setSelectedLectureId(null)
            setShowCatalog(false)
        }
        setIsSidebarOpen(false)
    }

    const handleSelectLecture = (unitId, lectureId) => {
        setSelectedUnitId(unitId)
        setSelectedLectureId(lectureId)
        setIsSidebarOpen(false)
    }

    const handleAddCourse = (title, description) => {
        const newId = Date.now()
        setCourses([...courses, { id: newId, title, description, units: [] }])
        setSelectedCourseId(newId)
        setShowProfile(false)
        setShowCatalog(false)
    }

    const handleAddUnit = () => {
        if (!selectedCourse) return
        const newId = selectedCourse.units.length > 0
            ? Math.max(...selectedCourse.units.map(u => u.id)) + 1
            : 1
        const updatedCourses = courses.map(c => {
            if (c.id === selectedCourseId) {
                return {
                    ...c,
                    units: [...c.units, {
                        id: newId,
                        title: `Unit ${newId}: New Unit`,
                        lectures: []
                    }]
                }
            }
            return c
        })
        setCourses(updatedCourses)
    }

    const handleDeleteUnit = (unitId) => {
        if (!selectedCourse) return
        const updatedCourses = courses.map(c => {
            if (c.id === selectedCourseId) {
                return {
                    ...c,
                    units: c.units.filter(u => u.id !== unitId)
                }
            }
            return c
        })
        setCourses(updatedCourses)
        if (selectedUnitId === unitId) {
            setSelectedUnitId(null)
            setSelectedLectureId(null)
        }
    }

    const handleAddLecture = (unitId) => {
        if (!selectedCourse) return
        const unit = selectedCourse.units.find(u => u.id === unitId)
        if (!unit) return
        const newId = unit.lectures.length > 0
            ? Math.max(...unit.lectures.map(l => l.id)) + 1
            : 1
        const updatedCourses = courses.map(c => {
            if (c.id === selectedCourseId) {
                return {
                    ...c,
                    units: c.units.map(u => {
                        if (u.id === unitId) {
                            return {
                                ...u,
                                lectures: [...u.lectures, {
                                    id: newId,
                                    title: `Lecture ${newId}: New Lecture`,
                                    materials: { video: null, audio: null, pdf: null, images: [] }
                                }]
                            }
                        }
                        return u
                    })
                }
            }
            return c
        })
        setCourses(updatedCourses)
    }

    const handleDeleteLecture = (unitId, lectureId) => {
        if (!selectedCourse) return
        const updatedCourses = courses.map(c => {
            if (c.id === selectedCourseId) {
                return {
                    ...c,
                    units: c.units.map(u => {
                        if (u.id === unitId) {
                            return {
                                ...u,
                                lectures: u.lectures.filter(l => l.id !== lectureId)
                            }
                        }
                        return u
                    })
                }
            }
            return c
        })
        setCourses(updatedCourses)
        if (selectedLectureId === lectureId && selectedUnitId === unitId) {
            setSelectedLectureId(null)
        }
    }

    const handleSaveMaterials = (materials) => {
        if (!selectedCourse || !selectedLecture) return
        const updatedCourses = courses.map(c => {
            if (c.id === selectedCourseId) {
                return {
                    ...c,
                    units: c.units.map(u => {
                        if (u.id === selectedUnitId) {
                            return {
                                ...u,
                                lectures: u.lectures.map(l => {
                                    if (l.id === selectedLectureId) {
                                        return { ...l, materials: { ...l.materials, ...materials } }
                                    }
                                    return l
                                })
                            }
                        }
                        return u
                    })
                }
            }
            return c
        })
        setCourses(updatedCourses)
    }

    const handleSendQuery = async (msg) => {
        setChatHistory(prev => [...prev, { type: 'user', text: msg }])
        setChatHistory(prev => [...prev, { type: 'ai', text: 'Analyzing topic and gathering insights... 🤖' }])

        try {
            // Check if it's a research topic request
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/summarize?topic=${encodeURIComponent(msg)}`)

            if (!response.ok) {
                throw new Error('Research failed')
            }

            const data = await response.json()

            // Remove loading message and add result
            setChatHistory(prev => {
                const newHistory = [...prev]
                newHistory.pop() // Remove loading msg
                return [...newHistory, {
                    type: 'research',
                    data: data
                }]
            })

        } catch (error) {
            console.error('Query failed:', error)
            setChatHistory(prev => {
                const newHistory = [...prev]
                newHistory.pop()
                return [...newHistory, {
                    type: 'ai',
                    text: 'Sorry, I encountered an error while researching that topic. Please try again.'
                }]
            })
        }
    }

    return (
        <div className="app-container">
            <Header onToggleSidebar={toggleSidebar} />
            <div className={`main-layout ${!isSignedIn ? 'full-width' : ''}`}>
                {isSignedIn && (
                    <Sidebar
                        isOpen={isSidebarOpen}
                        onClose={() => setIsSidebarOpen(false)}
                        courses={courses}
                        selectedCourseId={selectedCourseId}
                        selectedUnitId={selectedUnitId}
                        selectedLectureId={selectedLectureId}
                        onSelectCourse={handleSelectCourse}
                        onAddCourse={handleAddCourse}
                        onAddUnit={handleAddUnit}
                        onDeleteUnit={handleDeleteUnit}
                        onAddLecture={handleAddLecture}
                        onDeleteLecture={handleDeleteLecture}
                        onSelectLecture={handleSelectLecture}
                        showProfile={showProfile}
                        onToggleProfile={handleToggleProfile}
                        onShowCatalog={handleShowCatalog}
                    />
                )}

                {isSignedIn && (courses.length === 0 || showCatalog) ? (
                    <main className="main-content">
                        <CourseCatalog onEnroll={handleEnrollCourse} />
                    </main>
                ) : (
                    <MainContent
                        selectedCourse={selectedCourse}
                        selectedUnit={selectedUnit}
                        selectedLecture={selectedLecture}
                        selectedLectureId={selectedLectureId}
                        onSaveMaterials={handleSaveMaterials}
                        chatHistory={chatHistory}
                        onSendQuery={handleSendQuery}
                        showProfile={showProfile}
                    />
                )}
            </div>
            <ThemeToggle />
        </div>
    )
}

export default App
