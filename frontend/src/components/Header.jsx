import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton } from '@clerk/clerk-react'
import './Header.css'

function Header({ onToggleSidebar }) {
    return (
        <header className="header">
            <div className="header-content">
                <div className="header-left">
                    <button className="menu-toggle" onClick={onToggleSidebar} aria-label="Toggle Menu">
                        ☰
                    </button>
                    <h1 className="logo">
                        <span className="logo-icon">🎓</span>
                        <span className="logo-text">Intelligent Academic Knowledge</span>
                    </h1>
                </div>
                <div className="auth-section">
                    <SignedOut>
                        <SignInButton mode="modal">
                            <button className="sign-in-btn">
                                <span>Sign in</span>
                            </button>
                        </SignInButton>
                        <SignUpButton mode="modal">
                            <button className="sign-up-btn">
                                <span className="btn-icon">👤+</span>
                                <span>Sign up</span>
                            </button>
                        </SignUpButton>
                    </SignedOut>
                    <SignedIn>
                        <UserButton
                            appearance={{
                                elements: {
                                    avatarBox: {
                                        width: 40,
                                        height: 40
                                    }
                                }
                            }}
                            afterSignOutUrl="/"
                        />
                    </SignedIn>
                </div>
            </div>
        </header>
    )
}

export default Header
