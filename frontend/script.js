document.addEventListener('DOMContentLoaded', () => {
    // --- Data Model with Lectures ---
    let courses = [
        {
            id: 1, title: 'Computer Science 101', description: 'Introduction to programming.',
            lectures: [
                { id: 1, title: 'Lecture 1: Intro to CS', materials: { video: null, audio: null, pdf: null, images: [] } },
                { id: 2, title: 'Lecture 2: Variables', materials: { video: null, audio: null, pdf: null, images: [] } }
            ]
        },
        {
            id: 2, title: 'Advanced Mathematics', description: 'Calculus and Linear Algebra.',
            lectures: [
                { id: 1, title: 'Lecture 1: Limits', materials: { video: null, audio: null, pdf: null, images: [] } },
                { id: 2, title: 'Lecture 2: Derivatives', materials: { video: null, audio: null, pdf: null, images: [] } }
            ]
        },
        {
            id: 3, title: 'Physics & Mechanics', description: 'Laws of motion and energy.',
            lectures: [
                { id: 1, title: 'Lecture 1: Newton\'s Laws', materials: { video: null, audio: null, pdf: null, images: [] } }
            ]
        },
        {
            id: 4, title: 'English Literature', description: 'Classic and modern works.',
            lectures: [
                { id: 1, title: 'Lecture 1: Shakespeare', materials: { video: null, audio: null, pdf: null, images: [] } }
            ]
        },
        {
            id: 5, title: 'World History', description: 'Human civilization journey.',
            lectures: [
                { id: 1, title: 'Lecture 1: Ancient Egypt', materials: { video: null, audio: null, pdf: null, images: [] } }
            ]
        }
    ];

    let chatHistory = [];
    let selectedCourseId = null;
    let selectedLectureId = null;

    const courseListEl = document.getElementById('course-list');
    const mainContentEl = document.getElementById('main-dynamic-content');
    const addCourseBtn = document.getElementById('add-course-btn');

    // --- Render Sidebar ---
    function renderSidebar() {
        courseListEl.innerHTML = '';
        courses.forEach(course => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#';
            a.textContent = course.title;
            a.dataset.id = course.id;
            a.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.submenu a').forEach(link => link.classList.remove('active'));
                a.classList.add('active');
                selectedCourseId = course.id;
                selectedLectureId = null;
                renderCourseLectures(course.id);
            });
            li.appendChild(a);
            courseListEl.appendChild(li);
        });
    }

    // --- Render Course with Lecture List ---
    function renderCourseLectures(courseId) {
        const course = courses.find(c => c.id === courseId);
        if (!course) return;

        mainContentEl.innerHTML = `
            <div class="course-view-container">
                <div class="lecture-panel">
                    <h3>${course.title}</h3>
                    <p class="course-desc">${course.description}</p>
                    <div class="lecture-list-header">
                        <strong>Lectures</strong>
                        <button class="btn-small btn-success" id="add-lecture-btn">+ Add Lecture</button>
                    </div>
                    <ul class="lecture-list" id="lecture-list">
                        ${course.lectures.map(lec => `
                            <li>
                                <a href="#" class="lecture-link" data-course-id="${courseId}" data-lecture-id="${lec.id}">${lec.title}</a>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div class="lecture-detail-panel" id="lecture-detail-panel">
                    <p class="placeholder-text">Select a lecture to view materials.</p>
                </div>
            </div>
            <div class="query-section" id="query-section">
                <h4>Query / Chat</h4>
                <div class="chat-messages" id="chat-messages">
                    ${chatHistory.map(m => `<div class="chat-msg ${m.type}">${m.text}</div>`).join('')}
                </div>
                <div class="chat-input-area">
                    <input type="text" id="chat-input" class="form-control" placeholder="Ask about uploaded materials...">
                    <button class="btn btn-primary" id="send-query-btn">Send</button>
                </div>
            </div>
        `;

        // Attach lecture click events
        document.querySelectorAll('.lecture-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.lecture-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                const cId = parseInt(link.dataset.courseId);
                const lId = parseInt(link.dataset.lectureId);
                selectedLectureId = lId;
                renderLectureDetails(cId, lId);
            });
        });

        // Add Lecture button
        document.getElementById('add-lecture-btn').addEventListener('click', () => handleAddLecture(courseId));

        // Chat send button
        document.getElementById('send-query-btn').addEventListener('click', handleSendQuery);
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSendQuery();
        });
    }

    // --- Render Lecture Details (Materials) ---
    function renderLectureDetails(courseId, lectureId) {
        const course = courses.find(c => c.id === courseId);
        if (!course) return;
        const lecture = course.lectures.find(l => l.id === lectureId);
        if (!lecture) return;

        const panel = document.getElementById('lecture-detail-panel');
        const mat = lecture.materials;

        panel.innerHTML = `
            <h4>${lecture.title}</h4>
            <div class="materials-display">
                <div class="material-item">
                    <strong>Video:</strong> ${mat.video ? `<span class="file-name">${mat.video.name}</span>` : '<em>None</em>'}
                </div>
                <div class="material-item">
                    <strong>Audio:</strong> ${mat.audio ? `<span class="file-name">${mat.audio.name}</span>` : '<em>None</em>'}
                </div>
                <div class="material-item">
                    <strong>PDF:</strong> ${mat.pdf ? `<span class="file-name">${mat.pdf.name}</span>` : '<em>None</em>'}
                </div>
                <div class="material-item">
                    <strong>Images:</strong> ${mat.images.length > 0 ? mat.images.map(i => `<span class="file-name">${i.name}</span>`).join(', ') : '<em>None</em>'}
                </div>
            </div>
            <hr>
            <h5>Upload New Materials</h5>
            <div class="upload-container">
                <div class="upload-item">
                    <label>Video</label>
                    <input type="file" id="upload-video" accept="video/*">
                </div>
                <div class="upload-item">
                    <label>Audio</label>
                    <input type="file" id="upload-audio" accept="audio/*">
                </div>
                <div class="upload-item">
                    <label>PDF</label>
                    <input type="file" id="upload-pdf" accept=".pdf">
                </div>
                <div class="upload-item">
                    <label>Images</label>
                    <input type="file" id="upload-images" accept="image/*" multiple>
                </div>
            </div>
            <button class="btn btn-primary" id="save-materials-btn" style="margin-top:1rem;">Save Materials</button>
        `;

        document.getElementById('save-materials-btn').addEventListener('click', () => {
            const videoFile = document.getElementById('upload-video').files[0];
            const audioFile = document.getElementById('upload-audio').files[0];
            const pdfFile = document.getElementById('upload-pdf').files[0];
            const imageFiles = Array.from(document.getElementById('upload-images').files);

            if (videoFile) lecture.materials.video = videoFile;
            if (audioFile) lecture.materials.audio = audioFile;
            if (pdfFile) lecture.materials.pdf = pdfFile;
            if (imageFiles.length > 0) lecture.materials.images.push(...imageFiles);

            alert('Materials saved!');
            renderLectureDetails(courseId, lectureId);
        });
    }

    // --- Add Lecture ---
    function handleAddLecture(courseId) {
        const course = courses.find(c => c.id === courseId);
        if (!course) return;
        const newId = course.lectures.length > 0 ? Math.max(...course.lectures.map(l => l.id)) + 1 : 1;
        course.lectures.push({
            id: newId,
            title: `Lecture ${newId}: New Lecture`,
            materials: { video: null, audio: null, pdf: null, images: [] }
        });
        renderCourseLectures(courseId);
    }

    // --- Query/Chat Handler ---
    function handleSendQuery() {
        const input = document.getElementById('chat-input');
        const msg = input.value.trim();
        if (!msg) return;

        chatHistory.push({ type: 'user', text: msg });

        // Simulated AI response
        setTimeout(() => {
            chatHistory.push({ type: 'ai', text: `You asked: "${msg}". (This is a simulated response. Connect to an AI backend for real answers.)` });
            updateChatUI();
        }, 500);

        input.value = '';
        updateChatUI();
    }

    function updateChatUI() {
        const chatEl = document.getElementById('chat-messages');
        if (chatEl) {
            chatEl.innerHTML = chatHistory.map(m => `<div class="chat-msg ${m.type}">${m.text}</div>`).join('');
            chatEl.scrollTop = chatEl.scrollHeight;
        }
    }

    // --- Add Course (existing) ---
    function renderAddCourseForm() {
        document.querySelectorAll('.submenu a').forEach(link => link.classList.remove('active'));
        mainContentEl.innerHTML = `
            <div class="course-form-container">
                <h2>Add New Course</h2>
                <form id="add-course-form">
                    <div class="form-group">
                        <label>Course Title</label>
                        <input type="text" id="new-course-title" class="form-control" placeholder="Enter title" required>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea id="new-course-desc" class="form-control" rows="3" placeholder="Enter description" required></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-success">Create Course</button>
                        <button type="button" class="btn" id="cancel-btn" style="background:#ccc;">Cancel</button>
                    </div>
                </form>
            </div>
        `;
        document.getElementById('add-course-form').addEventListener('submit', handleAddCourse);
        document.getElementById('cancel-btn').addEventListener('click', () => {
            mainContentEl.innerHTML = `<section class="welcome-section"><h2>Welcome</h2><p>Select a course.</p></section>`;
        });
    }

    function handleAddCourse(e) {
        e.preventDefault();
        const title = document.getElementById('new-course-title').value;
        const desc = document.getElementById('new-course-desc').value;
        const newId = courses.length > 0 ? Math.max(...courses.map(c => c.id)) + 1 : 1;
        courses.push({ id: newId, title, description: desc, lectures: [] });
        renderSidebar();
        selectedCourseId = newId;
        renderCourseLectures(newId);
        setTimeout(() => {
            const link = document.querySelector(`.submenu a[data-id="${newId}"]`);
            if (link) link.classList.add('active');
        }, 0);
    }

    // --- Init ---
    if (addCourseBtn) addCourseBtn.addEventListener('click', renderAddCourseForm);
    renderSidebar();
});
