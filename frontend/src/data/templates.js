export const courseTemplates = [
    {
        id: 1,
        title: 'Computer Science 101',
        description: 'Introduction to programming and algorithms.',
        icon: '💻',
        units: [
            {
                id: 1, title: 'Unit 1: Fundamentals',
                lectures: [
                    { id: 1, title: 'Lecture 1: Intro to CS', materials: { video: null, audio: null, pdf: null, images: [] } },
                    { id: 2, title: 'Lecture 2: Variables', materials: { video: null, audio: null, pdf: null, images: [] } }
                ]
            }
        ]
    },
    {
        id: 2,
        title: 'Advanced Mathematics',
        description: 'Calculus, Linear Algebra, and Statistics.',
        icon: '📐',
        units: [
            {
                id: 1, title: 'Unit 1: Basic Calculus', lectures: [
                    { id: 1, title: 'Lecture 1: Limits', materials: { video: null, audio: null, pdf: null, images: [] } },
                    { id: 2, title: 'Lecture 2: Derivatives', materials: { video: null, audio: null, pdf: null, images: [] } }
                ]
            }
        ]
    },
    {
        id: 3,
        title: 'World History',
        description: 'A comprehensive journey through human civilization.',
        icon: '🌍',
        units: [
            {
                id: 1, title: 'Unit 1: Ancient Civilizations', lectures: [
                    { id: 1, title: 'Lecture 1: Mesopotamia', materials: { video: null, audio: null, pdf: null, images: [] } },
                    { id: 2, title: 'Lecture 2: Ancient Egypt', materials: { video: null, audio: null, pdf: null, images: [] } }
                ]
            }
        ]
    },
    {
        id: 4,
        title: 'Physics I',
        description: 'Mechanics, Thermodynamics, and Waves.',
        icon: '⚛️',
        units: [
            {
                id: 1, title: 'Unit 1: Kinematics', lectures: [
                    { id: 1, title: 'Lecture 1: Motion in 1D', materials: { video: null, audio: null, pdf: null, images: [] } }
                ]
            }
        ]
    }
]
