use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use anyhow::{Result, Context};

#[derive(Debug, Serialize, Deserialize)]
pub enum DecisionType {
    Accept,
    Reject,
    Partial,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TimelineEvent {
    timestamp: DateTime<Utc>,
    commit_hash: Option<String>,
    decision_type: DecisionType,
    files_modified: Vec<String>,
    llm_suggestion: String,
    user_feedback: String,
    tags: Vec<String>,
}

#[derive(Debug)]
pub struct Orchestrator {
    workspace_path: PathBuf,
    timeline_path: PathBuf,
    events: Vec<TimelineEvent>,
}

impl Orchestrator {
    pub fn new(workspace_path: PathBuf) -> Result<Self> {
        let timeline_path = workspace_path.join("timeline.json");
        let events = if timeline_path.exists() {
            let content = fs::read_to_string(&timeline_path)
                .context("Failed to read timeline.json")?;
            serde_json::from_str(&content)
                .context("Failed to parse timeline.json")?
        } else {
            Vec::new()
        };

        Ok(Self {
            workspace_path,
            timeline_path,
            events,
        })
    }

    pub fn add_event(&mut self, event: TimelineEvent) -> Result<()> {
        self.events.push(event);
        self.save_timeline()
    }

    pub fn save_timeline(&self) -> Result<()> {
        let json = serde_json::to_string_pretty(&self.events)
            .context("Failed to serialize timeline events")?;
        fs::write(&self.timeline_path, json)
            .context("Failed to write timeline.json")?;
        Ok(())
    }

    pub fn get_events_by_tag(&self, tag: &str) -> Vec<&TimelineEvent> {
        self.events.iter()
            .filter(|event| event.tags.contains(&tag.to_string()))
            .collect()
    }

    pub fn get_events_by_decision(&self, decision: DecisionType) -> Vec<&TimelineEvent> {
        self.events.iter()
            .filter(|event| matches!(event.decision_type, decision))
            .collect()
    }

    pub fn analyze_patterns(&self) -> HashMap<String, f64> {
        let mut tag_success_rates = HashMap::new();
        let mut tag_counts = HashMap::new();

        for event in &self.events {
            for tag in &event.tags {
                *tag_counts.entry(tag.clone()).or_insert(0) += 1;
                if matches!(event.decision_type, DecisionType::Accept) {
                    *tag_success_rates.entry(tag.clone()).or_insert(0.0) += 1.0;
                }
            }
        }

        tag_counts.iter().map(|(tag, &count)| {
            let success_rate = *tag_success_rates.get(tag).unwrap_or(&0.0) / count as f64;
            (tag.clone(), success_rate)
        }).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_orchestrator_basics() -> Result<()> {
        let temp_dir = TempDir::new()?;
        let mut orchestrator = Orchestrator::new(temp_dir.path().to_path_buf())?;

        let event = TimelineEvent {
            timestamp: Utc::now(),
            commit_hash: Some("abc123".to_string()),
            decision_type: DecisionType::Accept,
            files_modified: vec!["test.rs".to_string()],
            llm_suggestion: "Add function".to_string(),
            user_feedback: "Good change".to_string(),
            tags: vec!["feature".to_string()],
        };

        orchestrator.add_event(event)?;
        assert_eq!(orchestrator.events.len(), 1);
        
        let patterns = orchestrator.analyze_patterns();
        assert_eq!(patterns.get("feature"), Some(&1.0));

        Ok(())
    }
}
