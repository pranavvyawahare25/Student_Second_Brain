import { useState, useEffect } from 'react'
import './ThemeToggle.css'

function ThemeToggle() {
    const [isDark, setIsDark] = useState(true)

    useEffect(() => {
        document.body.setAttribute('data-theme', isDark ? 'dark' : 'light')
    }, [isDark])

    return (
        <button
            className="theme-toggle"
            onClick={() => setIsDark(!isDark)}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
            <span className="theme-icon">{isDark ? '☀️' : '🌙'}</span>
            <span className="theme-label">{isDark ? 'Light' : 'Dark'}</span>
        </button>
    )
}

export default ThemeToggle
