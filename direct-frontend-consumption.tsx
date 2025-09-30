/**
 * FRONTEND REFACTOR: Direct Backend Consumption
 * 
 * This React component directly consumes the backend format
 * without any legacy conversion layers.
 */

interface DirectBackendAMSPResponse {
  // Use the exact format returned by Python backend
  summary: {
    total_lines: number;
    parsed_lines: number;
    critical_count: number;
    error_count: number;
    warning_count: number;
  };
  intelligent_analysis: {
    system_health_score: number;
    ai_insights: {
      recommendations: string[];
      key_findings: string[];
      system_health_score: number;
    };
    important_events: Array<{
      timestamp: string;
      component: string;
      event_type: string;
      message: string;
    }>;
  };
  recommendations: string[];
  critical_issues: Array<{
    timestamp: string;
    component: string;
    message: string;
    severity_score: number;
  }>;
}

const DirectAMSPAnalysisDisplay: React.FC<{data: DirectBackendAMSPResponse}> = ({ data }) => {
  // Directly use backend data - no conversion needed!
  const healthScore = data.intelligent_analysis?.system_health_score || 0;
  const healthStatus = getHealthStatus(healthScore);
  const recommendations = data.recommendations || [];
  const criticalIssues = data.critical_issues || [];
  
  return (
    <div className="amsp-analysis-results">
      {/* System Health */}
      <div className="health-indicator">
        <div className={`health-score ${healthStatus.class}`}>
          {healthScore}/100 {healthStatus.status}
        </div>
      </div>
      
      {/* Processing Stats */}
      <div className="processing-stats">
        <div className="stat">
          <span className="label">Lines Processed:</span>
          <span className="value">{data.summary.parsed_lines.toLocaleString()}</span>
        </div>
        <div className="stat">
          <span className="label">Critical Issues:</span>
          <span className="value text-red-600">{data.summary.critical_count}</span>
        </div>
        <div className="stat">
          <span className="label">Warnings:</span>
          <span className="value text-yellow-600">{data.summary.warning_count}</span>
        </div>
      </div>
      
      {/* AI Recommendations */}
      <div className="recommendations">
        <h3>🧠 AI Analysis</h3>
        {recommendations.map((rec, index) => (
          <div key={index} className="recommendation" 
               dangerouslySetInnerHTML={{ __html: rec }} />
        ))}
      </div>
      
      {/* Critical Issues */}
      {criticalIssues.length > 0 && (
        <div className="critical-issues">
          <h3>🔴 Critical Issues</h3>
          {criticalIssues.slice(0, 10).map((issue, index) => (
            <div key={index} className="issue-item">
              <div className="issue-header">
                <span className="timestamp">{formatTimestamp(issue.timestamp)}</span>
                <span className="component">{issue.component}</span>
                <span className="severity">{issue.severity_score}/100</span>
              </div>
              <div className="issue-message">{issue.message}</div>
            </div>
          ))}
        </div>
      )}
      
      {/* Important Events Timeline */}
      {data.intelligent_analysis?.important_events && (
        <div className="timeline">
          <h3>⭐ Important Events</h3>
          {data.intelligent_analysis.important_events.map((event, index) => (
            <div key={index} className="timeline-event">
              <div className="event-time">{formatTimestamp(event.timestamp)}</div>
              <div className="event-content">
                <span className="event-component">{event.component}</span>
                <span className="event-type">{event.event_type}</span>
                <div className="event-message">{event.message}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const getHealthStatus = (score: number) => {
  if (score < 50) return { status: '🔴 Critical', class: 'critical' };
  if (score < 70) return { status: '🟡 Warning', class: 'warning' };
  if (score < 90) return { status: '🟠 Caution', class: 'caution' };
  return { status: '🟢 Healthy', class: 'healthy' };
};

const formatTimestamp = (timestamp: string) => {
  return new Date(timestamp).toLocaleString();
};