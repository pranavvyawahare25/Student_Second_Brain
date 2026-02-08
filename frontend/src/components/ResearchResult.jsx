import React from 'react'
import './ResearchResult.css'

function ResearchResult({ data }) {
    if (!data || !data.insights) return null
    const { insights } = data

    return (
        <div className="research-result">
            <div className="research-summary">
                <h4>✨ Summary</h4>
                <p>{insights.summary}</p>
            </div>

            <div className="research-grid">
                <div className="research-card">
                    <h5>📚 Key Concepts</h5>
                    <ul>
                        {insights.key_concepts?.map((c, i) => <li key={i}>{c}</li>)}
                    </ul>
                </div>

                <div className="research-card">
                    <h5>🗺️ Learning Roadmap</h5>
                    <ol>
                        {insights.learning_roadmap?.map((step, i) => <li key={i}>{step}</li>)}
                    </ol>
                </div>

                <div className="research-card">
                    <h5>✅ Practical To-Dos</h5>
                    <ul>
                        {insights.practical_todos?.map((todo, i) => <li key={i}>{todo}</li>)}
                    </ul>
                </div>

                <div className="research-card">
                    <h5>⚠️ Common Mistakes</h5>
                    <ul>
                        {insights.common_mistakes?.map((m, i) => <li key={i}>{m}</li>)}
                    </ul>
                </div>
            </div>

            {insights.step_by_step_explanation && insights.step_by_step_explanation.length > 0 && (
                <div className="research-steps">
                    <h5>👣 Step-by-Step Guide</h5>
                    <div className="steps-container">
                        {insights.step_by_step_explanation.map((step, i) => (
                            <div key={i} className="step-item">
                                <span className="step-number">{i + 1}</span>
                                <p>{step}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {insights.further_resources && insights.further_resources.length > 0 && (
                <div className="research-resources">
                    <h5>🔗 Further Resources</h5>
                    <div className="resources-list">
                        {insights.further_resources.map((res, i) => (
                            <a
                                key={i}
                                href={res.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`resource-link ${res.type}`}
                            >
                                <span className="resource-icon">
                                    {res.type === 'video' ? '📺' :
                                        res.type === 'tutorial' ? '📖' :
                                            res.type === 'docs' ? '📄' :
                                                res.type === 'paper' ? '🔬' :
                                                    res.type === 'wiki' ? '🌐' :
                                                        res.type === 'article' ? '📰' : '🔗'}
                                </span>
                                <span className="resource-title">{res.title}</span>
                            </a>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

export default ResearchResult
