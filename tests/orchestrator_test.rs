use orchestrator::{Orchestrator, TimelineEvent, DecisionType};
use assert_fs::prelude::*;
use chrono::Utc;
use predicates::prelude::*;
use anyhow::Result;

#[test]
fn test_new_orchestrator() -> Result<()> {
    let temp = assert_fs::TempDir::new()?;
    let orchestrator = Orchestrator::new(temp.path().to_path_buf())?;
    
    // Timeline.json should not exist yet
    temp.child("timeline.json").assert(predicate::path::missing());
    
    Ok(())
}

#[test]
fn test_add_and_retrieve_events() -> Result<()> {
    let temp = assert_fs::TempDir::new()?;
    let mut orchestrator = Orchestrator::new(temp.path().to_path_buf())?;

    // Add test events
    let event1 = TimelineEvent::new(
        Some("abc123".to_string()),
        DecisionType::Accept,
        vec!["src/main.rs".to_string()],
        "Add error handling".to_string(),
        "Good improvement".to_string(),
        vec!["error-handling".to_string(), "safety".to_string()],
    );

    let event2 = TimelineEvent::new(
        Some("def456".to_string()),
        DecisionType::Reject,
        vec!["src/lib.rs".to_string()],
        "Remove error checking".to_string(),
        "Would reduce safety".to_string(),
        vec!["safety".to_string()],
    );

    orchestrator.add_event(event1)?;
    orchestrator.add_event(event2)?;

    // Verify events were saved
    temp.child("timeline.json").assert(predicate::path::exists());

    // Test retrieval by tag
    let safety_events = orchestrator.get_events_by_tag("safety");
    assert_eq!(safety_events.len(), 2);

    // Test retrieval by decision
    let accepted = orchestrator.get_events_by_decision(DecisionType::Accept);
    assert_eq!(accepted.len(), 1);
    let rejected = orchestrator.get_events_by_decision(DecisionType::Reject);
    assert_eq!(rejected.len(), 1);

    Ok(())
}

#[test]
fn test_pattern_analysis() -> Result<()> {
    let temp = assert_fs::TempDir::new()?;
    let mut orchestrator = Orchestrator::new(temp.path().to_path_buf())?;

    // Add events with different success rates for different tags
    for i in 0..10 {
        let event = TimelineEvent::new(
            Some(format!("commit{}", i)),
            if i % 2 == 0 { DecisionType::Accept } else { DecisionType::Reject },
            vec!["test.rs".to_string()],
            "Test change".to_string(),
            "Test feedback".to_string(),
            vec!["tag1".to_string(), if i < 8 { "tag2".to_string() } else { "tag3".to_string() }],
        );
        orchestrator.add_event(event)?;
    }

    let patterns = orchestrator.analyze_patterns();
    
    // tag1 should have 50% success rate (5/10 accepted)
    assert!((patterns["tag1"] - 0.5).abs() < f64::EPSILON);
    
    // tag2 should have 50% success rate (4/8 accepted)
    assert!((patterns["tag2"] - 0.5).abs() < f64::EPSILON);
    
    // tag3 should have 50% success rate (1/2 accepted)
    assert!((patterns["tag3"] - 0.5).abs() < f64::EPSILON);

    Ok(())
}
