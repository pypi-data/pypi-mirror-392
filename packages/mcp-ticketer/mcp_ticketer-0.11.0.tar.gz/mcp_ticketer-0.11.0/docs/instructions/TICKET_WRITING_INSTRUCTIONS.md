# Ticket Writing Instructions for AI Agents

## Core Principle
**Specificity without verbosity.** Tickets must be actionable, scannable, and pass the "Absent-Factor Test": Could someone else pick this up without asking questions?

## Critical Anti-Patterns to Avoid
- ❌ Vague titles: "Fix issue", "Feature request", "Update component"
- ❌ Implementation details: Lines of code, specific file paths, prescribed technical approaches
- ❌ Generic users: "As a user" instead of specific roles
- ❌ Unmeasurable criteria: "user-friendly", "performs well", "works as expected"
- ❌ Missing context: No business value, no reproduction steps, no edge cases
- ❌ Information buried in comments: Decisions must migrate to description

## Ticket Type Templates

### Epic (Large multi-sprint work)
**Title Pattern:** "Strategic objective in 50-60 chars"
```
**Overview:** What this epic accomplishes and why it matters

**Business Goals:** 
- KPI or metric this supports
- Strategic objective alignment

**Scope:**
- IN SCOPE: Specific features/components included
- OUT OF SCOPE: Explicit exclusions

**Success Metrics:** How we measure completion

**Child Stories:** Links to constituent tasks

**Timeline:** Target quarter/release

**Resources:** Link to PRD, designs, specs (do NOT duplicate content)
```

### Task/Story (1-2 week work item)
**Title Pattern:** Start with action verb, 50-60 chars
- Good: "Build user authentication flow", "Fix mobile nav collapse bug"
- Bad: "Authentication", "Nav issue", "Update homepage"

```
**User Story:** (when applicable)
As a [specific role], I want [specific function], so that [concrete benefit]

**Request Details:**
[Concrete, specific requirements. Include:]
- Exact URLs or entry points
- Specific data/content requirements  
- Design/UX specifications
- Technical constraints or dependencies
- Environment details (for bugs: browser, device, OS)

**Acceptance Criteria:**
[Choose format based on complexity:]

Simple tasks (checklist):
- [ ] Specific, testable outcome
- [ ] Another measurable result
- [ ] Third concrete criterion

Complex workflows (Given-When-Then):
- GIVEN [initial state/context]
  WHEN [action taken]
  THEN [expected result with specifics]

**Edge Cases:** (if applicable)
- Error handling requirements
- Boundary conditions
- Permission/access scenarios

**Resources:**
- Link to designs: [URL]
- Related docs: [URL]
- Dependencies: TICKET-123
```

### Bug Report
**Title Pattern:** "Who/what/where/how the bug manifests"
- Good: "Login button unresponsive on iOS Safari", "API returns 500 on bulk user import"
- Bad: "Login broken", "Server error"

```
**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Steps to Reproduce:**
1. Exact step with specifics (URL, button label, data entered)
2. Next action
3. Observed failure

**Environment:**
- Browser/App: [version]
- Device: [model/OS]
- User role/permissions: [specifics]
- Frequency: [always/intermittent/X% of time]

**Impact:**
[Who's affected, how many users, business severity]

**Additional Context:**
- Screenshots/recordings
- Console errors
- Network logs
```

## Title Crafting Rules
1. **Length:** 50-60 characters (displays correctly across all systems)
2. **Action verbs:** Build, Fix, Implement, Configure, Create, Update, Remove
3. **Front-load keywords:** Most important terms first for truncated displays
4. **Be specific:** "Fix login OAuth redirect loop" not "Fix login"
5. **Include scope indicators:** "[Blog] Build post content type" for visual grouping

## Description Structure
Use four sections with clear headers:

1. **Why (User Story/Context):** Business value, user impact - for non-technical stakeholders
2. **What (Request Details):** Specific requirements, concrete examples, URLs, data
3. **Done (Acceptance Criteria):** 3-7 testable, independent criteria
4. **Resources:** Links only, never duplicate content

## Acceptance Criteria Standards
**Must be:**
- **Testable:** Clear pass/fail determination
- **Specific:** No ambiguity - include numbers, percentages, time limits
- **Independent:** Each can be tested separately
- **Achievable:** Within reasonable scope
- **Clear:** Plain language, avoid jargon

**Quantity:** 3-7 criteria per story
- < 3 = insufficient detail
- > 7 = decompose into smaller stories

**Format selection:**
- Simple checklist: Straightforward features, configuration, content
- Given-When-Then: User interactions, workflows, complex logic
- Rule-oriented: Validation, compliance, non-functional requirements

## Cross-Functional Communication
**Structure for multiple audiences:**
- Lead with business impact (executives, PMs, stakeholders)
- Follow with implementation details (developers, QA)
- Use analogies for technical concepts when non-technical readers involved
- Eliminate jargon or define on first use
- Use visual aids (screenshots, diagrams) for clarity

**Business context must include:**
- Why this matters (revenue, efficiency, compliance, user satisfaction)
- Who benefits (customer segment, internal team, partners)
- Success metrics (how we measure value delivered)

## What NOT to Include
- ❌ Lines of code changed or files modified
- ❌ Commit messages or detailed git history  
- ❌ Time tracking details
- ❌ Meeting notes or discussion transcripts (capture decisions only)
- ❌ Duplicated information from linked resources
- ❌ Prescriptive implementation when developer creativity appropriate
- ❌ "Nice to have" features mixed with requirements (create separate tickets)

## Context Management
**In description:**
- Essential information for execution
- Decisions that affect implementation
- Constraints and dependencies
- Links to comprehensive resources

**In comments:**
- Questions and answers during work
- Progress updates
- Blockers and workarounds
- Decision rationale

**Migration rule:** When comments contain decisions that change requirements, update description and reference the comment.

## Special Scenarios

**When splitting tickets:**
- Architecture tickets: "Enable [capability]" - makes actions possible
- Task tickets: "Implement [feature]" - performs actions
- Each should be independently valuable and testable

**For research/spikes:**
- Time-box explicitly: "4-hour spike", "2-day investigation"  
- Define what questions need answers
- Specify deliverable: "Document findings in ticket comment with recommendation"

**For technical debt:**
- Explain the problem: what's slow, brittle, or blocked
- Quantify impact: build time, error rate, developer friction
- Don't force user story format - "Refactor X to improve Y" is fine

## Quality Checklist
Before finalizing any ticket, verify:
- [ ] Title is action-oriented and specific (50-60 chars)
- [ ] "Why" explains business value, not just feature description
- [ ] "What" has concrete specifics (URLs, values, scope boundaries)  
- [ ] Acceptance criteria are testable with clear pass/fail
- [ ] No jargon without definitions for cross-functional readers
- [ ] Resources linked, not duplicated
- [ ] Passes Absent-Factor Test: teammate could execute without questions

## Output Format
When generating tickets, structure your response as:

```
**TITLE:** [Generated title following rules above]

**DESCRIPTION:**
[Complete structured description using appropriate template]

**SUGGESTED TAGS:** [relevant, specific tags]

**ESTIMATED COMPLEXITY:** [T-shirt size or story points with brief rationale]
```

If information is missing to write a complete ticket, explicitly ask for:
- User role and benefit (for user stories)
- Specific technical requirements or constraints
- Acceptance criteria if not inferable
- Business context or urgency

Never fill gaps with assumptions - incomplete real information beats complete guesses.
